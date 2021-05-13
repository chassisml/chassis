import json
import os
import mxnet as mx
import cv2
import numpy as np
from collections import namedtuple

from mxnet_ssd import deploy
from flask_psc_model import ModelBase, load_metadata

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_DIR = os.path.join(THIS_DIR,'weights/')
LABELS_PATH = os.path.join(THIS_DIR,'resources/labels.json')
HYPERPARAMS_PATH = os.path.join(MODEL_DIR,'hyperparams.json')
PARAMS = json.load(open(HYPERPARAMS_PATH,'rb'))

CONFIDENCE_THRESHOLD=0.2
SHAPE = int(PARAMS['image_shape'])
INPUT_SHAPES = [('data', (1, 3, SHAPE, SHAPE))]
NETWORK = "resnet50"
NUM_CLASSES = int(PARAMS['num_classes'])
NMS_THRESH = float(PARAMS['nms_threshold'])
EPOCH = int(PARAMS['epochs'])-1

DEFAULT_MODEL_NAME = 'model_algo_1'
DEFAULT_MODEL_FILENAMES = {
    'symbol': 'model_algo_1-symbol.json',
    'params': 'model_algo_1-{:04d}.params'.format(EPOCH)
}
PREFIX = os.path.join(MODEL_DIR,DEFAULT_MODEL_NAME)

os.environ["MXNET_CUDNN_AUTOTUNE_DEFAULT"] = '0'

class ObjectDetector(ModelBase):

    #: load the `model.yaml` metadata file from up the filesystem hierarchy;
    #: this will be used to avoid hardcoding the below filenames in this file
    metadata = load_metadata(__file__)

    #: a list of input filenames; specifying the `input_filenames` attribute is required to configure the model app
    input_filenames = list(metadata.inputs)

    #: a list of output filenames; specifying the `output_filenames` attribute is required to configure the model app
    output_filenames = list(metadata.outputs)

    def __init__(self):
        """Load the model files and do any initialization.

        A single instance of this model class will be reused multiple times to perform inference
        on multiple input files so any slow initialization steps such as reading in a data
        files or loading an inference graph to GPU should be done here.

        This function should require no arguments, or provide appropriate defaults for all arguments.

        NOTE: The `__init__` function and `run` function may not be called from the same thread so extra
        care may be needed if using frameworks such as Tensorflow that make use of thread locals.
        """
        # set ctx
        self.set_ctx()
        # load model+weights from SageMaker model artifacts
        self.load_model()
        # infer required image size from network input shape
        self.img_shape = (SHAPE,SHAPE,3)
        # load class labels from file
        self.labels = json.load(open(LABELS_PATH,'rb'))

    def gpu_device(gpu_number=0):
        try:
            _ = mx.nd.array([1, 2, 3], ctx=mx.gpu(gpu_number))
        except mx.MXNetError:
            return None
        return mx.gpu(gpu_number)

    def set_ctx(self):
        if not ObjectDetector.gpu_device():
            self.ctx = mx.cpu()
        else:
            self.ctx = mx.gpu(0)

    def load_model(self):

        """
        Load model from weights files output by SageMaker.
        """

        # convert to deployable
        deployable_path = deploy.convert_to_deployable(NETWORK,SHAPE,NUM_CLASSES,NMS_THRESH,PREFIX,EPOCH)

        # load
        sym, arg_params, aux_params = mx.model.load_checkpoint(deployable_path, 0)
        self.mod = mx.mod.Module(symbol=sym, label_names=[], context=self.ctx)
        self.mod.bind(for_training=False, data_shapes=INPUT_SHAPES)
        self.mod.set_params(arg_params, aux_params)

    def predict(self, img):
        Batch = namedtuple('Batch', ['data'])

        img = np.swapaxes(img, 0, 2)
        img = np.swapaxes(img, 1, 2)
        img = img[np.newaxis, :]
    
        self.mod.forward(Batch([mx.nd.array(img)]))
        prob = self.mod.get_outputs()[0].asnumpy()
        prob = np.squeeze(prob)

        return prob

    def format(self,detections,orig_shape):

        output = {
            "modelType": "objectDetection",
            "result": {
                    "detections": []
                }
        }
        orig_height = orig_shape[0] 
        orig_width = orig_shape[1] 
        for detection in detections:
            (class_index, score, x0, y0, x1, y1) = detection
            if score < CONFIDENCE_THRESHOLD:
                continue
            xmin = int((x0 * SHAPE) * (orig_width / SHAPE))
            ymin = int((y0 * SHAPE) * (orig_height / SHAPE))
            xmax = int((x1 * SHAPE) * (orig_width / SHAPE))
            ymax = int((y1 * SHAPE) * (orig_height / SHAPE))

            formatted_detection = {
                "label": self.labels[int(class_index)],
                "score": round(float(score), 2),
                "xmin": xmin,
                "xmax": xmax,
                "ymin": ymin,
                "ymax": ymax
            }

            output['result']['detections'].append(formatted_detection)

        return output

    def run(self, input_path, output_path):
        """Run the model on the given input file paths and write to the given output file paths.

        The input files paths followed by the output file paths will be passed into this function as
        positional arguments in the same order as specified in `input_filenames` and `output_filenames`.

        For example:
        ```
        class SingleInputOutputModel(ModelBase):
            input_filenames = ['input.txt']
            output_filenames = ['output.json']

            def run(self, input, output):
                run_the_model(input, output)

        class MultipleInputOutputModel(ModelBase):
            input_filenames = ['input1.png', 'input2.json', 'input3.txt']
            output_filenames = ['output1.png', 'output2.json']

            def run(self, input1, input2, input3, output1, output2):
                run_the_model(input1, input2, input3, output1, output2)
        ```
        """

        # read image
        img = cv2.imread(input_path)
        if img is None:
            raise ValueError("Incoming image path is empty")
        orig_shape = img.shape

        # make sure valid 3-channel image
        if img is None or len(img.shape)!=3:
            raise ValueError("unable to read image, must be RGB JPEG or PNG image")

        # resize if necessary
        if not img.shape==self.img_shape:
            img = cv2.resize(img,self.img_shape[:-1])

        # run inference
        results = self.predict(img)

        # format output
        formatted_results = self.format(results,orig_shape)

        # write output
        with open(output_path, "w", encoding="utf-8") as output_file:
            json.dump(formatted_results, output_file)


if __name__ == '__main__':
    # run the model independently from the full application; can be useful for testing
    #
    # to run from the repository root:
    #     python -m model_lib.model /path/to/input.txt /path/to/output.json
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='the input data filepath')
    parser.add_argument('output', help='the output results filepath')
    args = parser.parse_args()

    model = ObjectDetector()
    model.run(args.input, args.output)

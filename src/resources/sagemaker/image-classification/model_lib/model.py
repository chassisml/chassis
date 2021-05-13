import json
import os
import mxnet as mx
import cv2
import numpy as np

from pathlib import Path

from flask_psc_model import ModelBase, load_metadata

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_DIR = os.path.join(THIS_DIR,'weights/')
LABELS_PATH = os.path.join(THIS_DIR,'resources/labels.json')
DEFAULT_MODEL_NAME = 'image-classification'
DEFAULT_MODEL_FILENAMES = {
    'symbol': 'image-classification-symbol.json',
    'params': 'image-classification-*.params',
    'shapes': 'model-shapes.json',
}
os.environ["MXNET_CUDNN_AUTOTUNE_DEFAULT"] = '0'

class ImageClassifier(ModelBase):

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
        # load model+weights from SageMaker model artifacts
        self.load_model()
        # get network input shape
        self.input_shape = self.mod.data_shapes[0][1]
        # infer required image size from network input shape
        self.img_shape = (self.input_shape[2],self.input_shape[3],self.input_shape[1])
        # load class labels from file
        self.labels = json.load(open(LABELS_PATH,'rb'))

    def gpu_device(gpu_number=0):
        try:
            _ = mx.nd.array([1, 2, 3], ctx=mx.gpu(gpu_number))
        except mx.MXNetError:
            return None
        return mx.gpu(gpu_number)

    def load_model(self):

        """
        Load model from weights files output by SageMaker.
        """

        for f in DEFAULT_MODEL_FILENAMES.values():
            for path in Path(MODEL_DIR).rglob(f):
                if not os.path.exists(path):
                    raise ValueError('Failed to load model with default model_fn: missing file {}.'
                                     'Expected files: {}'.format(f, [file_name for _, file_name
                                                                     in DEFAULT_MODEL_FILENAMES.items()]))

        shapes_file = os.path.join(MODEL_DIR, DEFAULT_MODEL_FILENAMES['shapes'])
        preferred_batch_size = 1

        with open(shapes_file, 'r') as f:
            signatures = json.load(f)

        data_names = []
        data_shapes = []

        for s in signatures:
            name = s['name']
            data_names.append(name)

            shape = s['shape']

            if preferred_batch_size:
                shape[0] = preferred_batch_size

            data_shapes.append((name, shape))

        sym, args, aux = mx.model.load_checkpoint(os.path.join(MODEL_DIR, DEFAULT_MODEL_NAME), 2)

        if not ImageClassifier.gpu_device():
            self.ctx = mx.cpu()
        else:
            self.ctx = mx.gpu(0)

        self.ctx = mx.cpu(0)

        self.mod = mx.mod.Module(symbol=sym, context=self.ctx, data_names=data_names, label_names=None)
        self.mod.bind(for_training=False, data_shapes=data_shapes)
        self.mod.set_params(args, aux, allow_missing=True)

    def format(self,pred):
        """
        Return class names and rounded scores for top 5 preds.
        """
        output = {}
        top_5_indices = pred.argsort()[-5:][::-1]
        output['top_5_results'] = [(self.labels[i],round(float(pred[i]),5)) for i in top_5_indices]
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

        # make sure valid 3-channel image
        if img is None or len(img.shape)!=3:
            raise ValueError("unable to read image, must be RGB JPEG or PNG image")

        # resize if necessary
        if not img.shape==self.img_shape:
            img = cv2.resize(img,self.img_shape[:-1])

        # reshape to match network input
        img_reshaped = np.moveaxis(img, 2, 0)[np.newaxis,:,:,:]

        # run inference
        results = self.mod.predict(mx.nd.array(img_reshaped).as_in_context(self.ctx)).asnumpy()[0]

        # format output
        formatted_results = self.format(results)

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

    model = ImageClassifier()
    model.run(args.input, args.output)

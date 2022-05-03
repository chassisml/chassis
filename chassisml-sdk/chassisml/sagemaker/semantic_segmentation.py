def get_process_fn(weights_path,ordered_class_list):

    import os
    import io
    import json
    import mxnet as mx
    import numpy as np
    import gluoncv
    from gluoncv.data.transforms.presets.segmentation import test_transform
    from chassisml.misc.onnx_utils import WrappedInferenceSession

    params = json.load(open(os.path.join(weights_path,'hyperparams.json'),'rb'))
    gluon_model_name = "{}_{}_voc".format(params['algorithm'],params['backbone'].replace('-',''))

    ctx = mx.cpu()
    model = gluoncv.model_zoo.get_model(gluon_model_name,ctx=ctx)
    model.load_parameters(os.path.join(weights_path,"model_algo-1"))

    def process(input_bytes):
        img = mx.image.imdecode(input_bytes)
        transformed = test_transform(img, ctx).astype('float32')
        model_output = model.predict(transformed)
        pred_mask = mx.nd.squeeze(mx.nd.argmax(model_output, 1)).asnumpy().astype(int)

        formatted_output = {"data":{"result": {"mask": pred_mask.tolist(),"ordered_class_list":ordered_class_list}}}

        return formatted_output

    return process
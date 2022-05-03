def get_process_fn(weights_path,ordered_class_list):
    import os
    import json
    import cv2
    import mxnet as mx
    import numpy as np
    from chassisml.misc.onnx_utils import WrappedInferenceSession

    full_mx_paths = {}
    for filename in os.listdir(weights_path):
        if filename.endswith('params'):
            full_mx_paths['params'] = os.path.join(weights_path,filename)
        elif filename.endswith('symbol.json'):
            full_mx_paths['symbol'] = os.path.join(weights_path,filename)
        elif filename.endswith('shapes.json'):
            full_mx_paths['shapes'] = os.path.join(weights_path,filename)
        else:
            continue

    if not full_mx_paths.keys() == {'params','symbol','shapes'}:
        raise ValueError("params, symbol, and shapes files all required")
    
    # convert to onnx
    orig_shape = json.load(open(full_mx_paths['shapes'],'rb'))[0]['shape']
    shape = (1,)+tuple(orig_shape[-3:])
    onnx_path = os.path.join(weights_path,'mxnet_exported_ic.onnx')
    mx.contrib.onnx.export_model(full_mx_paths['symbol'],full_mx_paths['params'],[shape],np.float32,onnx_path)

    # create wrapped inference session
    session = WrappedInferenceSession(open(onnx_path,'rb').read())

    # define process fn
    def process(input_bytes):
        decoded = cv2.imdecode(np.frombuffer(input_bytes, np.uint8), -1)
        resized = cv2.resize(decoded, shape[-2:])
        chan_first = np.moveaxis(resized, -1, 0)
        img = np.reshape(chan_first, shape).astype(np.float32)
        pred = session.run(None, {"data": img})[0][0]
        #TODO: is softmax needed?
        output = {"data":{"result": {}}}
        top_5_indices = pred.argsort()[-5:][::-1]
        labeled_preds = [(ordered_class_list[i] if ordered_class_list else i,round(float(pred[i]),5)) for i in top_5_indices]
        output["data"]["result"]["classPredictions"] = [{"score": x[1],"class": x[0]} for x in labeled_preds]
        return output

    return process
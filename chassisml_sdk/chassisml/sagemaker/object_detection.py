def get_process_fn(weights_path,ordered_class_list):

    import os
    import cv2
    import json
    import mxnet as mx
    import numpy as np
    from collections import namedtuple
    from chassisml.misc.mxnet_ssd import deploy
    from chassisml.misc.onnx_utils import WrappedInferenceSession

    # read and parse params from file
    params = json.load(open(os.path.join(weights_path,'hyperparams.json'),'rb'))
    shape = int(params['image_shape'])
    input_shape = [('data', (1, 3, shape, shape))]
    network = params['base_network']
    if network == 'vgg-16':
        network = 'vgg16_reduced'
    if network == 'resnet-50':
        network = 'resnet50'
    num_classes = int(params['num_classes'])
    nms_thresh = float(params['nms_threshold'])
    epoch = int(params['epochs'])-1
    prefix = os.path.join(weights_path,'model_algo_1')
    
    # convert to deployable model
    dep_params_path,dep_sym_path = deploy.convert_to_deployable(network,shape,num_classes,nms_thresh,prefix,epoch)

    # convert to onnx
    onnx_path = os.path.join(weights_path,'mxnet_exported_od.onnx')
    mx.contrib.onnx.export_model(dep_sym_path,dep_params_path,[input_shape[0][1]],np.float32,onnx_path)

    # create wrapped inference session
    session = WrappedInferenceSession(open(onnx_path,'rb').read())

    # define process fn
    def process(input_bytes):
        decoded = cv2.imdecode(np.frombuffer(input_bytes, np.uint8), -1)
        orig_shape = decoded.shape
        resized = cv2.resize(decoded, shape[-2:])
        chan_first = np.moveaxis(resized, -1, 0)
        img = np.reshape(chan_first, shape).astype(np.float32)
        detections = session.run(None, {"data": img})
        print(detections)

        output = {"data":{"result": {'detections':[]}}}
        
        orig_height = orig_shape[0] 
        orig_width = orig_shape[1] 
        for detection in detections:
            (class_index, score, x0, y0, x1, y1) = detection
            xmin = int((x0 * shape) * (orig_width / shape))
            ymin = int((y0 * shape) * (orig_height / shape))
            xmax = int((x1 * shape) * (orig_width / shape))
            ymax = int((y1 * shape) * (orig_height / shape))

            formatted_detection = {
                "label": ordered_class_list[int(class_index)] if ordered_class_list else int(class_index),
                "score": round(float(score), 2),
                "xmin": xmin,
                "xmax": xmax,
                "ymin": ymin,
                "ymax": ymax
            }

            output['data']['result']['detections'].append(formatted_detection)

        return output
        
    return process
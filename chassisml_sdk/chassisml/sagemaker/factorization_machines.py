def get_classification_process_fn(weights_path,ordered_class_list):
    import io
    import os
    import json
    import zipfile
    import mxnet as mx
    import numpy as np

    with zipfile.ZipFile(os.path.join(weights_path,'model_algo-1'), 'r') as zip_ref:
        zip_ref.extractall(weights_path)
    os.rename(os.path.join(weights_path,'symbol.json'),os.path.join(weights_path,'model-symbol.json'))
    os.rename(os.path.join(weights_path,'params'),os.path.join(weights_path,'model-0000.params'))

    model = mx.module.Module.load(os.path.join(weights_path,'model'), 0, False, label_names=['out_label'])
    model_params = json.load(open(os.path.join(weights_path,'meta.json'), 'rb'))

    V = model._arg_params['v'].asnumpy()
    if 'w0_weight' in model._arg_params:
        b = model._arg_params['w0_weight'].asnumpy()
    else:
        b = model._arg_params['Linear_Plus_Bias_bias'].asnumpy()

    if 'w1_weight' in model._arg_params:
        w = model._arg_params['w1_weight'].asnumpy().T
        V = V.T
    else:
        w = model._arg_params['Linear_Plus_Bias_weight'].asnumpy()

    num_features = model_params["training_parameters"]["feature_dim"]

    def process(input_bytes):

        X = np.genfromtxt(io.BytesIO(input_bytes), delimiter=",")
        if np.isnan(np.sum(X)):
            raise ValueError("The incoming file format is not supported by this implementation")

        feature_vector = X.reshape((1,-1))
        if feature_vector.shape[1] != int(num_features):
            raise ValueError("The number of incoming features doesn't match that of the trained model")

        linear_output = np.matmul(feature_vector, w.T)
        v = V.T
        t0 = np.matmul(feature_vector, v)
        t1 = np.power(feature_vector, 2)
        t2 = np.power(v, 2)
        term = t0 ** 2 - np.matmul(t1, t2)
        factor_output = 0.5 * np.sum(term, axis = 1)
        prob = 1.0 / (1.0 + np.exp(-np.mean(b + linear_output + factor_output, axis=0)[0]))

        formatted_preds = sorted([{"class":ordered_class_list[0] if ordered_class_list else 0,"score":1-prob},
                                {"class":ordered_class_list[1] if ordered_class_list else 1,"score":prob}],
                                key = lambda x: x["score"],reverse=True)
        formatted_output = {"data":{"result":{"classPredictions":formatted_preds}}}

        return formatted_output

    return process

def get_regression_process_fn(weights_path,**kwargs):
    
    import io
    import os
    import json
    import zipfile
    import mxnet as mx
    import numpy as np

    with zipfile.ZipFile(os.path.join(weights_path,'model_algo-1'), 'r') as zip_ref:
        zip_ref.extractall(weights_path)
    os.rename(os.path.join(weights_path,'symbol.json'),os.path.join(weights_path,'model-symbol.json'))
    os.rename(os.path.join(weights_path,'params'),os.path.join(weights_path,'model-0000.params'))

    model = mx.module.Module.load(os.path.join(weights_path,'model'), 0, False, label_names=['out_label'])
    model_params = json.load(open(os.path.join(weights_path,'meta.json'), 'rb'))

    V = model._arg_params['v'].asnumpy()
    if 'w0_weight' in model._arg_params:
        b = model._arg_params['w0_weight'].asnumpy()
    else:
        b = model._arg_params['Linear_Plus_Bias_bias'].asnumpy()

    if 'w1_weight' in model._arg_params:
        w = model._arg_params['w1_weight'].asnumpy().T
        V = V.T
    else:
        w = model._arg_params['Linear_Plus_Bias_weight'].asnumpy()

    num_features = model_params["training_parameters"]["feature_dim"]

    def process(input_bytes):

        X = np.genfromtxt(io.BytesIO(input_bytes), delimiter=",")
        if np.isnan(np.sum(X)):
            raise ValueError("The incoming file format is not supported by this implementation")

        feature_vector = X.reshape((1,-1))
        if feature_vector.shape[1] != int(num_features):
            raise ValueError("The number of incoming features doesn't match that of the trained model")

        linear_output = np.matmul(feature_vector, w.T)
        v = V.T
        t0 = np.matmul(feature_vector, v)
        t1 = np.power(feature_vector, 2)
        t2 = np.power(v, 2)
        term = t0 ** 2 - np.matmul(t1, t2)
        factor_output = 0.5 * np.sum(term, axis = 1)
        regression_value = np.mean(b + linear_output + factor_output, axis=0)[0]
        formatted_output = {"data":{"result":{"result":regression_value}}}

        return formatted_output 

    return process

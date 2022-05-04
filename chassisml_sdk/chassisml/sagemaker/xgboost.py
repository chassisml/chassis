def _is_float(element):
    try:
        float(element)
        return True
    except ValueError:
        return False

def get_classification_process_fn(weights_path,**kwargs):

    import io
    import os
    import xgboost as xgb
    import pickle as pkl
    import pandas as pd
    from scipy.special import softmax
    
    model = pkl.load(open(os.path.join(weights_path,'xgboost-model'), "rb"))

    def process(input_bytes):

        if any(_is_float(item) for item in input_bytes.decode("utf-8").splitlines()[0].split(',')):
            input_data = pd.read_csv(io.BytesIO(input_bytes),header=None)
        else:
            input_data = pd.read_csv(io.BytesIO(input_bytes))

        X_matrix = xgb.DMatrix(input_data,feature_names=model.feature_names)
        preds = model.predict(X_matrix, output_margin=True)
        formatted_preds = {"data":{"results": preds }}

        return formatted_preds
    
    return process

def get_regression_process_fn(weights_path,**kwargs):

    import io
    import os
    import xgboost as xgb
    import pandas as pd

    model = xgb.Booster()
    model.load_model(os.path.join(weights_path,'xgboost-model'))
    
    def process(input_bytes):

        if any(_is_float(item) for item in input_bytes.decode("utf-8").splitlines()[0].split(',')):
            input_data = pd.read_csv(io.BytesIO(input_bytes),header=None)
        else:
            input_data = pd.read_csv(io.BytesIO(input_bytes))

        X_matrix = xgb.DMatrix(input_data,feature_names=model.feature_names)
        preds = model.predict(X_matrix, output_margin=True)
        formatted_preds = {"data":{"results": preds }}

        return formatted_preds
    
    return process
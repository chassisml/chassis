def get_classification_process_fn(weights_path,ordered_class_list):

    import io
    import os
    import xgboost as xgb
    import pickle as pkl
    import pandas as pd
    from scipy.special import softmax
    
    model = pkl.load(open(os.path.join(weights_path,'xgboost-model'), "rb"))

    if ordered_class_list:
        n_classes = len(ordered_class_list)

    def process(input_bytes):

        input_data = pd.read_csv(io.BytesIO(input_bytes))

        try:
            if not any(input_data.iloc[0].apply(lambda x: isinstance(x, str))):
                input_data = pd.read_csv(io.BytesIO(input_bytes),header=None)

            X_matrix = xgb.DMatrix(input_data,feature_names=model.feature_names)
            preds = model.predict(X_matrix, output_margin=True)

        except IndexError:
            input_data = pd.read_csv(io.BytesIO(input_bytes),header=None)
            X_matrix = xgb.DMatrix(input_data,feature_names=model.feature_names)
            preds = model.predict(X_matrix, output_margin=True)

        if ordered_class_list:
            if preds[0].shape[0] != n_classes:
                raise ValueError(f"Length of 'ordered_class_list' ({preds[0].shape[0]}) doesn't match number of model output classes ({n_classes})")

        formatted_preds = {"data":{"results":[]}}
        for pred in preds:
            entries = []
            softmaxed_preds = softmax(pred)
            for j,score in enumerate(softmaxed_preds):
                entries.append({'score':score,'class':ordered_class_list[j] if ordered_class_list else j})
            formatted_preds["data"]["results"].append(sorted(entries,key = lambda x: x["score"],reverse=True))

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

        input_data = pd.read_csv(io.BytesIO(input_bytes))

        if not any(input_data.iloc[0].apply(lambda x: isinstance(x, str))):
            input_data = pd.read_csv(io.BytesIO(input_bytes),header=None)

        X_matrix = xgb.DMatrix(input_data,feature_names=model.feature_names)                
        preds = model.predict(X_matrix, output_margin=True)

        formatted_output = {"data":{"results": preds}}

        return formatted_output
    
    return process
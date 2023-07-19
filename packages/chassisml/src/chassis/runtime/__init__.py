from .model_runner import ModelRunner

PACKAGE_DATA_PATH = "data"

PYTHON_MODEL_KEY = "__chassis_model"


# PYTHON_PREPROCESSOR_KEY = "__chassis_preprocessor"
# PYTHON_POSTPROCESSOR_KEY = "__chassis_postprocessor"
# PYTHON_FORMATTER_KEY = "__chassis_formatter"
# PYTHON_SINGLE_PREDICT_FUNCTION_KEY = "__chassis_single_predict_function"

def python_pickle_filename_for_key(key):
    if key == PYTHON_MODEL_KEY:
        return "model.pkl"
    # if key == PYTHON_PREPROCESSOR_KEY:
    #     return "preprocessor.pkl"
    # if key == PYTHON_POSTPROCESSOR_KEY:
    #     return "postprocessor.pkl"
    # if key == PYTHON_FORMATTER_KEY:
    #     return "formatter.pkl"
    # if key == PYTHON_SINGLE_PREDICT_FUNCTION_KEY:
    #     return "simple_python_pipeline.pkl"

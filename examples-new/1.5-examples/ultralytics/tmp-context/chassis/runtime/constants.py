PACKAGE_DATA_PATH = "data"

PYTHON_MODEL_KEY = "__chassis_model"


# PYTHON_PREPROCESSOR_KEY = "__chassis_preprocessor"
# PYTHON_POSTPROCESSOR_KEY = "__chassis_postprocessor"
# PYTHON_FORMATTER_KEY = "__chassis_formatter"
# PYTHON_SINGLE_PREDICT_FUNCTION_KEY = "__chassis_single_predict_function"

def python_pickle_filename_for_key(key: str) -> str:
    """
    Helper function for serializing and deserializing Python functions.

    When used in the SDK, it returns the name of the file that should be written
    out in the build context based on what kind of function it is.

    When used inside the built container, it does exactly the opposite, it
    returns the name of the file that it should load to hydrate the function.

    Args:
        key: One of the keys defined in [chassis.runtime.constants][].

    Returns:
        The appropriate filename for the given `key`.
    """
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
    raise ValueError("Unsupported key")

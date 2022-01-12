import sys
import mlflow

# load model
model = mlflow.pyfunc.load_model(sys.argv[1])

# read file
file_bytes = open(sys.argv[2],'rb').read()

# single input prediction
print("Single input prediction:\n")
print(model.predict(file_bytes))

# to facilitate backwards compatibility  
if hasattr(model._model_impl.python_model,"batch_input") and model._model_impl.python_model.batch_input:
    batch_input = [file_bytes for _ in range(model._model_impl.python_model.batch_size)]
    print("\nBatch input predictions:\n")
    print(model._model_impl.python_model.batch_predict(None,batch_input))

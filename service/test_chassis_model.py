import sys
import mlflow

model = mlflow.pyfunc.load_model(sys.argv[1])
file_bytes = open(sys.argv[2],'rb').read()
print(model.predict(file_bytes))
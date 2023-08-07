import time

from io import StringIO
import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

from chassis.builder import DockerBuilder
from chassisml import ChassisClient, ChassisModel

'''
Train model
'''

# load data
data = load_iris()
X_train, X_test, y_train, y_test = train_test_split(data['data'], data['target'], test_size=.2)
# create model instance
bst = XGBClassifier(n_estimators=2, max_depth=2, learning_rate=1, objective='binary:logistic')
# fit model
bst.fit(X_train, y_train)
# make predictions
preds = bst.predict(X_test)
# define classnames
classes = data['target_names'].tolist()

# define legacy process function
def process(input_bytes):
    # load data
    inputs = pd.read_csv(StringIO(str(input_bytes, "utf-8")))    
    
    # run inference
    preds = bst.predict_proba(inputs)
    
    # structure results
    inference_result = {
        "classPredictions": [
            {"row": i+1, "class": classes[np.argmax(pred)], "score": np.max(pred)} for i, pred in enumerate(preds)
        ]
    }

    structured_output = {
        "data": {
            "result": inference_result,
            "explanation": None,
            "drift": None,
        }
    }
    return structured_output


'''
Create Model
'''
# # legacy way
# chassis_client = ChassisClient("https://chassis.app.modzy.com")
# model = chassis_client.create_model(process_fn=process)
# new way
model = ChassisModel(process_fn=process, legacy_predict_fn=True)

# add pip requirements
model.add_requirements(["scikit-learn", "numpy", "xgboost", "pandas"])

# test model
sample_filepath = './data/iris_data.csv'
results = model.test(sample_filepath)
print(results)

# build container
builder = DockerBuilder(model)
start_time = time.time()
res = builder.build_image(name="1.5-xgboost-iris-classification", tag="0.0.1", show_logs=True)
end_time = time.time()
print(res)
print(f"Container image built in {round((end_time-start_time)/60, 5)} minutes")
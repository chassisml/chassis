import time

from chassis.builder import DockerBuilder
from chassisml import ChassisClient, ChassisModel

import pandas as pd
import numpy as np
import lightgbm as lgb
from io import StringIO
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

'''
Model training
'''
# load breast cancer dataset
df = pd.read_csv('./data/Breast_cancer_data.csv')
# preprocess data
X = df[['mean_radius','mean_texture','mean_perimeter','mean_area','mean_smoothness']]
y = df['diagnosis']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.3, random_state = 0)

# build and train model
clf = lgb.LGBMClassifier()
clf.fit(X_train, y_train)

# make predictions and evaluate model accuracy
y_pred=clf.predict(X_test)

accuracy=accuracy_score(y_pred, y_test)
print('LightGBM Model accuracy score: {0:0.4f}'.format(accuracy_score(y_test, y_pred)))

# define process function
classes = ["No Cancer", "Cancer"]
def process(input_bytes):
    inputs = pd.read_csv(StringIO(str(input_bytes, "utf-8")))
    preds = clf.predict_proba(inputs)
    
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
# legacy way
# chassis_client = ChassisClient("https://chassis.app.modzy.com")
# model = chassis_client.create_model(process_fn=process)
# new way
model = ChassisModel(process_fn=process, legacy_predict_fn=True)

# add pip requirements
model.add_requirements(["scikit-learn", "numpy", "lightgbm", "pandas"])

# test model
sample_filepath = './data/sample_cancer_data.csv'
results = model.test(sample_filepath)
print(results)

# build container
builder = DockerBuilder(model)
start_time = time.time()
res = builder.build_image(name="1.5-lightgbm-cancer-classification", tag="0.0.1", show_logs=True)
end_time = time.time()
print(res)
print(f"Container image built in {round((end_time-start_time)/60, 5)} minutes")


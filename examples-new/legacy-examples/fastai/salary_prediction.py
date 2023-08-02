import os
import time
from typing import Mapping

from chassis.builder import DockerBuilder
from chassisml import ChassisModel, ChassisClient

import pandas as pd
from io import StringIO
from fastai.tabular.all import TabularDataLoaders, RandomSplitter, TabularPandas, tabular_learner, Categorify, FillMissing, Normalize, range_of, accuracy

'''
Model Development
'''
df = pd.read_csv("./data/adult_sample/adult.csv")
df.head()

dls = TabularDataLoaders.from_csv("./data/adult_sample/adult.csv", path=os.path.join(os.getcwd(), "data/adult_sample"), y_names="salary",
    cat_names = ['workclass', 'education', 'marital-status', 'occupation', 'relationship', 'race'],
    cont_names = ['age', 'fnlwgt', 'education-num'],
    procs = [Categorify, FillMissing, Normalize])

splits = RandomSplitter(valid_pct=0.2)(range_of(df))
to = TabularPandas(df, procs=[Categorify, FillMissing,Normalize],
                   cat_names = ['workclass', 'education', 'marital-status', 'occupation', 'relationship', 'race'],
                   cont_names = ['age', 'fnlwgt', 'education-num'],
                   y_names='salary',
                   splits=splits)

# build and train model
learn = tabular_learner(dls, metrics=accuracy)
learn.fit_one_cycle(1)

# define labels and process function
labels = ['<50k', '>50k']

def process(input_bytes):
    inputs = pd.read_csv(StringIO(str(input_bytes, "utf-8")))
    dl = learn.dls.test_dl(inputs)
    preds = learn.get_preds(dl=dl)[0].numpy()
    
    inference_result = {
        "classPredictions": [
            {
                "row": i+1,
                "predictions": [
                    {"class": labels[j], "score": round(pred[j], 4)} for j in range(2)
                ]
            } for i, pred in enumerate(preds)
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
model.add_requirements(["fastai", "pandas"])

# test model
sample_filepath = './data/sample_adult_data.csv'
results = model.test(sample_filepath)
print(results)

# build container
builder = DockerBuilder(model)
start_time = time.time()
res = builder.build_image(name="1.5-fastai-salary-prediction", tag="0.0.1", show_logs=True)
end_time = time.time()
print(res)
print(f"Container image built in {round((end_time-start_time)/60, 5)} minutes")

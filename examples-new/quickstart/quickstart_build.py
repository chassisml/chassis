import asyncio
from chassis.client import OMIClient
from chassis.builder import DockerBuilder
import chassis.guides as guides 
import cloudpickle
cloudpickle.register_pickle_by_value(guides)

# initialize model
model = guides.QuickstartDigitsClassifier
results = model.test(guides.DigitsSampleData)
print(results)

# build container
builder = DockerBuilder(model)
res = builder.build_image("my-first-chassis-model")
print(res)




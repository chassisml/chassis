import cloudpickle
import chassis.guides as guides
from chassis.builder import DockerBuilder
# cloudpickle.register_pickle_by_value(guides)

model = guides.QuickstartDigitsClassifier
results = model.test(guides.DigitsSampleData)
print(results)

builder = DockerBuilder(model)
job_results = builder.build_image("my-first-chassis-model")
print(job_results)

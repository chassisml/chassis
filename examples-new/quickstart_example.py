from chassis.builder import DockerBuilder
from chassis.guides import QuickstartDigitsClassifier, DigitsSampleData

model = QuickstartDigitsClassifier
results = model.test(DigitsSampleData)
print(results)

builder = DockerBuilder(model)
res = builder.build_image("my-first-chassis-model")
print(res)
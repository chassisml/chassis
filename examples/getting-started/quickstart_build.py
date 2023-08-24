import chassis.guides as guides
from chassis.builder import DockerBuilder

# Import a pre-trained scikit-learn digit classification model with pre-defined container metadata
model = guides.QuickstartDigitsClassifier
# Test the model with a picture of a handwritten "5"
results = model.test(guides.DigitsSampleData)
# View test results
print(results)

# Configure container builder option as Docker
builder = DockerBuilder(model)
# Build container for the model locally
job_results = builder.build_image("my-first-chassis-model")
# View container info after the build completes
print(job_results)

from chassis.client import OMIClient
from chassis.guides import DigitsSampleData

# Execute the test_container method to spin up the container, run inference, and return the results
res = OMIClient.test_container(container_name="my-first-chassis-model", inputs=DigitsSampleData, pull=False)
# Parse results from output item 
result = res.outputs[0].output["results.json"]
# View results
print(f"Result: {result}")
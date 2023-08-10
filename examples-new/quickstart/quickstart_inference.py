from chassis.client import OMIClient
from chassis.guides import DigitsSampleData

with OMIClient("localhost", 45000) as client:
    status = client.status()
    print(f"Status: {status}")
    res = client.run([{'input': DigitsSampleData}])
    result = res.outputs[0].output["results.json"]
    print(f"Result: {result}")
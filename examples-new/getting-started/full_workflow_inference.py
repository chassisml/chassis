from chassis.client import OMIClient
from chassis.guides import DigitsSampleData

# Instantiate OMI Client connection to model running on localhost:45000 
with OMIClient("localhost", 45000) as client:
    # Call and view results of status RPC 
    status = client.status()
    print(f"Status: {status}")
    # Submit inference with quickstart sample data
    res = client.run(DigitsSampleData)
    # Parse results from output item 
    result = res.outputs[0].output["results.json"]
    # View results
    print(f"Result: {result}")
import asyncio
from chassis.client import OMIClient
from chassis.guides import DigitsSampleData


async def run_test():
    # Instantiate OMI Client connection to model running on localhost:45000
    async with OMIClient("localhost", 45000) as client:
        # Call and view results of status RPC
        status = await client.status()
        print(f"Status: {status}")
        # Submit inference with quickstart sample data
        res = await client.run(DigitsSampleData)
        # Parse results from output item
        result = res.outputs[0].output["results.json"]
        # View results
        print(f"Result: {result}")


if __name__ == '__main__':
    asyncio.run(run_test())

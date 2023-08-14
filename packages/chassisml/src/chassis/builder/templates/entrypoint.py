import os.path
import sys

base_dir = os.path.dirname(__file__)
server_dir = os.path.join(base_dir, "chassis", "server")

if os.path.exists(os.path.join(server_dir, "omi")):
    try:
        import asyncio
        from chassis.server.omi import serve
        asyncio.run(serve())
        sys.exit(0)
    except Exception as e:
        print(f"Error starting OMI server: {e}")
        sys.exit(1)

if os.path.exists(os.path.join(server_dir, "kserve")):
    try:
        from chassis.server.kserve import serve
        serve()
        sys.exit(0)
    except Exception as e:
        print(f"Error starting KServe server: {e}")
        sys.exit(1)

print("Unable to find suitable server")
sys.exit(1)

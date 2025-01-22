# if the use_debugpy is set to True, the debugpy will be used to debug the test cases
import os

if os.environ.get("TESTS_USE_DEBUGPY", "false").lower() == "true":
    import debugpy

    assert "TESTS_DEBUGPY_PORT" in os.environ, "TESTS_DEBUGPY_PORT environment variable must be set"

    debugpy_port = int(os.environ["TESTS_DEBUGPY_PORT"])
    debugpy.listen(debugpy_port)
    print(f"Waiting for debugger attach on port {debugpy_port}...")
    debugpy.wait_for_client()

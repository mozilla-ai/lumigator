class FakeJobSubmissionClient:
    """A mock implementation of Ray's JobSubmissionClient for testing purposes.
    Simulates basic job submission and management functionality.
    """
    def __init__(self):
        self.jobs: dict[str, dict] = {}  # Store jobs and their metadata
        self.runtime_env = {}

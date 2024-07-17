from mzai.backend.services.groundtruth import GroundTruthService


class FakeGroundTruthService(GroundTruthService):
    def __init__(self, deployment_repo):
        super().__init__(deployment_repo, ray_client=None)

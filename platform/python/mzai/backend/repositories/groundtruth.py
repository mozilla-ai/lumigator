from sqlalchemy.orm import Session

from mzai.backend.records.groundtruth import GroundTruthDeploymentRecord
from mzai.backend.repositories.base import BaseRepository


class  GroundTruthDeploymentRepository(BaseRepository[ GroundTruthDeploymentRecord]):
    def __init__(self, session: Session):
        super().__init__(GroundTruthDeploymentRecord, session)

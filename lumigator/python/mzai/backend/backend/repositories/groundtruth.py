from sqlalchemy.orm import Session

from backend.records.groundtruth import GroundTruthDeploymentRecord
from backend.repositories.base import BaseRepository


class GroundTruthDeploymentRepository(BaseRepository[GroundTruthDeploymentRecord]):
    def __init__(self, session: Session):
        super().__init__(GroundTruthDeploymentRecord, session)

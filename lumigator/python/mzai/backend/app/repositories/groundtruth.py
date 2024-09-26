from sqlalchemy.orm import Session

from app.records.groundtruth import GroundTruthDeploymentRecord
from app.repositories.base import BaseRepository


class GroundTruthDeploymentRepository(BaseRepository[GroundTruthDeploymentRecord]):
    def __init__(self, session: Session):
        super().__init__(GroundTruthDeploymentRecord, session)

from abc import ABC, abstractmethod
from uuid import UUID

from lumigator_schemas.jobs import JobCreate
from pydantic import BaseModel


class JobDefinition(ABC):
    """Abstract base class for jobs.

    Attributes:
    ----------
    command : str
        The command to execute the job.
    pip_reqs : str, optional
        Path to a requirements file specifying dependencies (default: None).
    work_dir : str, optional
        Working directory for the job (default: None).
    config_model : BaseModel
        Pydantic model representing job-specific configuration.

    """

    command: str
    pip_reqs: str | None
    work_dir: str | None
    config_model: BaseModel
    type: str

    # This should end up not being necessary, since we'd expose the whole job config
    @abstractmethod
    def generate_config(
        self, request: JobCreate, record_id: UUID, dataset_path: str, storage_path: str, type: str
    ) -> BaseModel:
        """Generates

        Parameters
        ----------
        request : JobCreate
            Non-job-specific parameters for job creation
        record_id : UUID
            Job ID assigned to the job
        dataset_path : str
            S3 path for the input dataset
        storage_path : str
            S3 where the backend will store the results from the job

        Returns:
        -------
        generate_config : BaseModel
            A job-specific pydantic model that will be sent to the Ray job instance
        """
        pass

    @abstractmethod
    def store_as_dataset(self) -> bool:
        """Returns:
        -------
        store_as_dataset : bool
            Whether the results should be stored in an S3 path
        """
        pass

    def __init__(self, command, pip_reqs, work_dir, config_model, type):
        self.command = command
        self.pip_reqs = pip_reqs
        self.work_dir = work_dir
        self.config_model = config_model
        self.type = type

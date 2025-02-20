

from lumigator_schemas.keys import Key

from backend.repositories.keys import KeyRepository


class KeyService:
    def __init__(self, key_repo: KeyRepository):
        self._key_repo = key_repo

    def upload_key(self, key: Key, key_name: str) -> None:
        """Uploads a key under a certain name"""
        self._key_repo.create(**key.model_dump(), key_name=key_name)

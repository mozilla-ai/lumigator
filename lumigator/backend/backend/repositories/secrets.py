from uuid import UUID

from sqlalchemy.orm import Session

from backend.records.secrets import SecretRecord
from backend.repositories.base import BaseRepository


class SecretRepository(BaseRepository[SecretRecord]):
    def __init__(self, session: Session):
        super().__init__(SecretRecord, session)

    def delete_secret(self, name: str) -> bool:
        """Delete a secret identified by its name.

        :param name: The name of the secret to be deleted
        :returns: ``True`` if the secret was deleted, ``False`` if the secret was not found.
        """
        secret = self.get_secret_by_name(name)
        if not secret:
            return False

        return bool(self.delete(secret.id))

    def get_secret_by_name(self, name: str) -> SecretRecord | None:
        """Retrieve secret by name (case-insensitive)."""
        return self.session.query(SecretRecord).filter(SecretRecord._name == name.lower()).first()

    def list_secrets(self) -> list[SecretRecord]:
        """List all secrets."""
        return self.list()

    def save_secret(self, name: str, secret_data: dict) -> bool:
        """Save a secret (create or update) to the database.

        Checks if a secret already exists by name. If it does, the secret is updated.
        If it doesn't exist, a new secret is created.

        @param name: The name of the secret
        @param secret_dict: A dictionary containing the secret's details (value and description)
        @returns: A boolean indicating whether the secret was newly created (`True`) or updated (`False`).
        @rtype: bool
        """
        existing_secret = self.get_secret_by_name(name)

        if existing_secret:
            self._update_secret(existing_secret.id, secret_data)
            return False
        else:
            self._create_secret(secret_data)
            return True

    def _create_secret(self, secret_data: dict) -> SecretRecord:
        """Create a new secret."""
        secret = SecretRecord(**secret_data)
        self.session.add(secret)
        self.session.commit()

        return secret

    def _update_secret(self, secret_id: UUID, secret_data: dict) -> SecretRecord | None:
        """Update an existing secret."""
        secret: SecretRecord | None = self.session.query(SecretRecord).filter(SecretRecord.id == secret_id).first()
        if not secret:
            return None

        for key, value in secret_data.items():
            setattr(secret, key, value)
        self.session.commit()

        return secret

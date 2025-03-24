from lumigator_schemas.tasks import TaskDefinition
from model_clients.translation_utils import resolve_user_input_language


class LanguageCodesSetupMixin:
    """Mixin with common functionality for translation clients"""

    def setup_translation_languages(self, task_definition: TaskDefinition):
        """Initialize source and target language information for translation"""
        source_language_user_input = getattr(task_definition, "source_language", None)
        target_language_user_input = getattr(task_definition, "target_language", None)

        if not source_language_user_input or not target_language_user_input:
            raise ValueError("Source and target languages must be provided for translation task.")

        source_language_info = resolve_user_input_language(source_language_user_input)
        target_language_info = resolve_user_input_language(target_language_user_input)

        self.source_language_iso_code = source_language_info["iso_code"]  # e.g. "en"
        self.source_language = source_language_info["full_name"]  # e.g. "English"
        self.source_language_alpha3_code = source_language_info["alpha3_code"]  # e.g. "eng"
        self.target_language_iso_code = target_language_info["iso_code"]  # e.g. "de"
        self.target_language = target_language_info["full_name"]  # e.g. "German"
        self.target_language_alpha3_code = target_language_info["alpha3_code"]  # e.g. "deu"

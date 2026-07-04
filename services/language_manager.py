from typing import Any

from settings import GeneralSettings
from utils import JsonUtility
from utils.logger import get_logger

_log = get_logger(__name__)


class LanguageManager:
    data: dict = None
    registered_widgets: list[Any] = []

    @staticmethod
    def update_language() -> None:
        LanguageManager.initialize()
        LanguageManager.update_widgets_text()

    @staticmethod
    def update_widgets_text() -> None:
        """
        Updates language in all registered widgets based on the current language.
        """
        for widget in LanguageManager.registered_widgets:
            try:
                widget.update_widgets_text()
            except Exception:
                _log.exception("update_widgets_text failed for %r", widget)

    @staticmethod
    def initialize() -> None:
        lang_file = f"data/languages/{GeneralSettings.settings['lang_code']}.json"
        LanguageManager.data = JsonUtility.read_from_file(lang_file)

    @staticmethod
    def register_widget(widget: Any) -> None:
        """
        Registers a widget with the LanguageManager for language updates.

        Args:
            widget (Any): The widget to register.
        """
        LanguageManager.registered_widgets.append(widget)

    @staticmethod
    def unregister_widget(widget: Any) -> None:
        """
        Unregisters a widget from the LanguageManager.

        Args:
            widget (Any): The widget to LanguageManager.
        """
        LanguageManager.registered_widgets.remove(widget)

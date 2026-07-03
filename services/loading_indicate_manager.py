import threading
import time

from settings import GeneralSettings


class LoadingIndicateManager:
    """
    Manages a loading indicator by displaying dots in a loop.
    """

    dots_count: int = 1
    max_dots_count: int = 4

    @staticmethod
    def loading_indicator() -> None:
        """
        Displays loading indicator dots in a loop.

        This method continuously updates the dots_count to create a loading indicator effect.
        """
        while True:
            for LoadingIndicateManager.dots_count in range(1, LoadingIndicateManager.max_dots_count + 1):
                time.sleep(GeneralSettings.settings["update_delay"])

    @staticmethod
    def initialize() -> None:
        """
        Initializes the loading indicator manager.

        Starts a separate thread for running the loading indicator.
        """
        loading_indicator_thread = threading.Thread(target=LoadingIndicateManager.loading_indicator)
        loading_indicator_thread.daemon = True
        loading_indicator_thread.start()

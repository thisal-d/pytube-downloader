import queue
import threading
from collections.abc import Callable

from settings.general_settings import GeneralSettings


class LoadManager:
    """
    Manages the loading queue videos and controls the loading process.
    """

    # Class variables to keep track of active and queued loads
    active_load_count: int = 0
    queued_load_count: int = 0
    queued_loads: list = []
    active_loads: list = []
    status_change_callback: Callable = None

    # Queue used to signal the manager thread when the queue state changes
    _signal_queue: queue.Queue = queue.Queue()

    @staticmethod
    def manage_load_queue() -> None:
        """
        Manages the load queue by initiating loads if conditions are met.

        Blocks on a queue.Queue instead of polling with time.sleep, so it wakes
        up immediately when a new item is registered or an active load finishes.
        """
        while True:
            # Block until signalled (no busy-wait)
            LoadManager._signal_queue.get()

            if (
                GeneralSettings.settings["max_simultaneous_loads"] > LoadManager.active_load_count
                and LoadManager.queued_load_count > 0
            ):
                try:
                    # Dequeue a video, initiate loading, and update counts
                    LoadManager.queued_load_count -= 1
                    LoadManager.queued_loads[0].load_video()
                    LoadManager.active_load_count += 1
                    LoadManager.active_loads.append(LoadManager.queued_loads.pop(0))
                except Exception as error:
                    print(f"load_manager.py : failed to start load: {error}")
                    # Re-queue the item count so the queue stays consistent
                    LoadManager.queued_load_count += 1
                LoadManager.status_change_callback()

    @staticmethod
    def _signal() -> None:
        """Puts a token into the internal signal queue to wake the manager thread."""
        LoadManager._signal_queue.put(True)

    @staticmethod
    def register(video) -> None:
        """
        Registers a video to be loaded.

        Adds the video to the load queue, updates the queued load count,
        and signals the manager thread.
        """
        LoadManager.queued_loads.append(video)
        LoadManager.queued_load_count += 1
        LoadManager.status_change_callback()
        LoadManager._signal()

    @staticmethod
    def unregister_from_queued(video) -> None:
        """
        Unregisters a video from the load queue.

        Removes the video from the load queue and updates the queued load count.
        """
        if video in LoadManager.queued_loads:
            LoadManager.queued_loads.remove(video)
            LoadManager.queued_load_count -= 1
        LoadManager.status_change_callback()

    @staticmethod
    def unregister_from_active(video) -> None:
        """
        Unregisters a video from the active load list.

        Removes the video from the active load list, updates the active load count,
        and signals the manager thread so it can start the next queued item.
        """
        if video in LoadManager.active_loads:
            LoadManager.active_loads.remove(video)
            LoadManager.active_load_count -= 1
        LoadManager.status_change_callback()
        LoadManager._signal()

    @staticmethod
    def initialize(status_change_callback: Callable) -> None:
        """
        Initializes the load manager by starting a separate thread for managing the load queue.

        Args:
            status_change_callback (Callable, optional): A callback function to be called on status changes.
        """
        LoadManager.status_change_callback = status_change_callback
        loading_manage_thread = threading.Thread(target=LoadManager.manage_load_queue)
        loading_manage_thread.daemon = True
        loading_manage_thread.start()

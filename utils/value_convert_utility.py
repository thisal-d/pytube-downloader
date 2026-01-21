from typing import Union


class ValueConvertUtility:
    @staticmethod
    def convert_time(seconds: int) -> str:
        """
        Convert seconds to a human-readable time format (HH:MM:SS).

        Args:
            seconds (int): The number of seconds.

        Returns:
            str: The converted time string.
        """
        hours = int(seconds / 3600)
        minutes = int((seconds - (hours * 3600)) / 60)
        seconds = seconds - (hours * 3600) - (minutes * 60)

        if hours > 0:
            converted_time = f"{hours}:{minutes:0>2}:{int(seconds):0>2}"
        else:
            converted_time = f"{minutes}:{int(seconds):0>2}"

        return converted_time

    @staticmethod
    def convert_size(size: Union[int, float], decimal_points: int) -> str:
        """
        Convert size to a human-readable format (e.g., KB, MB, GB) with specified decimal points.

        Args:
            size (Union[int, float]): The size value.
            decimal_points (int): The number of decimal points to round to.

        Returns:
            str: The converted size string.
        """
        data_units = ["B", "KB", "MB", "GB", "TB", "PB", "EB"]
        index = 0

        while len(str(int(size))) > 3 and (index + 1) < len(data_units):
            size = size / 1024
            index += 1
        if decimal_points > 0:
            converted_size = f"{round(size, decimal_points)} {data_units[index]}"
        else:
            converted_size = f"{int(size)} {data_units[index]}"

        return converted_size
    
    @staticmethod
    def MB_KB_to_Bytes(value: str) -> str:
        if value.endswith("MB"):
            return float(value[:-2]) * 1024 * 1024
        elif value.endswith("KB"):
            return float(value[:-2]) * 1024
        else:
            return 0

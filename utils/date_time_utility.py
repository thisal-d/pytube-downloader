import datetime


class DateTimeUtility:
    @staticmethod
    def get_current_date_time() -> str:
        # Get the current date and time
        current_time = datetime.datetime.now()

        # Format the date and time
        formatted_time = current_time.strftime("%Y/%m/%d %H:%M:%S")

        return formatted_time

from typing import List, Dict
import pytubefix
from .value_convert_utility import ValueConvertUtility


class DownloadInfoUtility:
    @staticmethod
    def sort_download_qualities(qualities_info: List[Dict]) -> List[Dict]:
        """
        Sort the list of download qualities information based on their keys.

        Args:
            qualities_info (List[Dict]): A list of dictionaries containing download qualities information.

        Returns:
            List[Dict]: The sorted list of download qualities information.
        """
          # Separate videos and audio into different lists
        videos = []
        audio = []
        
        for item in qualities_info:
                if item['type'] == 'video':
                    videos.append(item)
                elif item['type'] == 'audio':
                    audio.append(item)
        
        # Sort videos manually based on resolution
        for i in range(len(videos)):
            for j in range(len(videos) - i - 1):
                try:
                    # Extract resolutions as integers
                    res1 = int(videos[j]['reso'].replace('p', '')) if 'reso' in videos[j] else 0
                    res2 = int(videos[j + 1]['reso'].replace('p', '')) if 'reso' in videos[j + 1] else 0
                    
                    # Swap if the current video's resolution is less than the next one
                    if res1 < res2:
                        videos[j], videos[j + 1] = videos[j + 1], videos[j]
                except Exception as error:
                    print(f"download_info_utility.py L-44 : {error}")
            
       
        # Combine videos and audio, videos first
        return videos + audio

    @staticmethod
    def to_dict(data) -> list[dict[str, str]]:
        """
        Convert data to a list of dictionaries.

        Args:
            data: Data to be converted.

        Returns:
            list[dict]: A list of dictionaries.
        """
        data_list = []
        for d in data:
            data_list.append(
                {value.split("=")[0]: value.split("=")[1] for value in str(d)[9:-1].replace('"', "").split(" ")})
        return data_list

    @staticmethod
    def get_supported_download_types(video_streams: pytubefix.StreamQuery) -> list[dict[str, int]]:
        """
        Get supported download types from video streams.

        Args:
            video_streams (pytubefix.StreamQuery): video streams.

        Returns:
            list[dict]: A list of supported download types.
        """
        data = DownloadInfoUtility.to_dict(video_streams.all())
        supported_download_types = []
        supported_download_resos = []
        
        audio_stream_file_size = video_streams.get_audio_only().filesize
        
        for stream_type in data[0::]:
            if stream_type["type"] == "video":
                # Progressive True means video has inbuilt audio
                if stream_type["progressive"] == 'True':
                    try:
                        file_size = video_streams.get_by_itag(stream_type["itag"]).filesize
                        download_info = {"itag": stream_type["itag"], "type": "video", "reso": stream_type["res"], "size": file_size, "inbuilt_audio" : True}
                        if stream_type["res"] not in supported_download_resos and stream_type["res"] != 'None':
                            supported_download_types.append(download_info)
                            supported_download_resos.append(stream_type["res"])
                    except Exception as error:
                        print(f"download_info_utility.py L-87 : {error}")
                        pass
                
        for stream_type in data[0::]:
            if stream_type["progressive"] == 'False' and stream_type["type"] == "video":
                try:
                    file_size = video_streams.get_by_itag(stream_type["itag"]).filesize
                    download_info = {"itag": stream_type["itag"], "type": "video", "reso": stream_type["res"], "size": file_size + audio_stream_file_size, "inbuilt_audio" : False}
                    if stream_type["res"] not in supported_download_resos and stream_type["res"] != 'None':
                        supported_download_types.append(download_info)
                        supported_download_resos.append(stream_type["res"])
                except Exception as error:
                    print(f"download_info_utility.py L-99 : {error}")
                    pass
    
        try:
            audio_stream = video_streams.get_audio_only()
            file_size = audio_stream.filesize
            audio_bit_rate = f"{str(int(audio_stream.bitrate / 1024))}kbps"
            supported_download_types.append({"itag": stream_type["itag"], "bitrate": audio_bit_rate, "size": file_size, "type": "audio",  "inbuilt_audio" : True})
        except Exception as error:
            print(f"download_info_utility.py  L-107 : {error}")
            pass

        return supported_download_types

    @staticmethod
    def generate_download_options(download_types: List[Dict]) -> List[str]:
        """
        Generate download options for CTk combo box based on download types and their sizes.

        Args:
            download_types List[Dict[str, int]]: A dictionary containing download types and their sizes.

        Returns:
            List[str]: A list of combo box values formatted as "type | size".
        """
        download_options = []
        
        for data_dict in download_types:
            if data_dict["type"] == "video":
                download_options.append(f"{data_dict["reso"]} | {ValueConvertUtility.convert_size(data_dict['size'], 1)}")
            else:
                download_options.append(f"{data_dict["bitrate"]} | {ValueConvertUtility.convert_size(data_dict['size'], 1)}")
                
        return download_options

    @staticmethod  
    def get_estimated_time(total_download_size: int, current_taken_time: int, current_download_size: int) -> int:
        """
        Estimate the total time required to download a file based on the current download progress.

        Args:
            total_download_size (int): The total size of the file to be downloaded in bytes.
            current_taken_time (int): The time already taken to download the file in seconds.
            current_download_size (int): The amount of data already downloaded in bytes.

        Returns:
            int: The estimated total time required to download the file in seconds.
        """
        try:
            avg_download_speed = current_download_size / current_taken_time
            remaining_download_size = total_download_size - current_download_size
            estimated_remaining_time = remaining_download_size / avg_download_speed
        except Exception as error:
            print(f"download_info_utility.py L-156 : {error}")
            return 0
            
        return estimated_remaining_time
    
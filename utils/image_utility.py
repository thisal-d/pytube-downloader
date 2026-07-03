from urllib import request

from PIL import Image, ImageDraw


class ImageUtility:
    """
    A utility class for processing images.
    """

    @staticmethod
    def crop_image(image: Image, start_position: tuple[int, int], end_position: tuple[int, int]) -> Image.Image:
        """
        Crop the input image

        Args:
            image (Image): Image
            start_position (Tuple[int, int]): Starting position (x, y) of the crop.
            end_position (Tuple[int, int]): Ending position (x, y) of the crop.

        Returns:
            Image: cropped image.
        """
        cropped_image = image.crop((start_position[0], start_position[1], end_position[0], end_position[1]))
        return cropped_image

    @staticmethod
    def resize_image(image: Image, new_size: tuple[int, int]) -> Image.Image:
        """
        Resize the input image to the specified size

        Args:
            image (Image): Image
            new_size (Tuple[int, int]): New size (width, height) of the image.

        Returns:
            Image: resized image.
        """
        resized_image = image.resize(new_size, Image.Resampling.LANCZOS)
        return resized_image

    @staticmethod  # from stackoverflow
    def create_image_with_rounded_corners(image: Image, radius: int) -> Image.Image:
        """
        Create a new image with rounded corners based on the input image.

        Args:
            image (Image): Image
            radius (int): Radius of the rounded corners.

        Returns:
            Image: image with rounded corners.
        """
        rounded_corner_added_image = image
        circle_mask = Image.new("L", (radius * 2, radius * 2), 0)
        draw_circle = ImageDraw.Draw(circle_mask)
        draw_circle.ellipse((0, 0, radius * 2 - 1, radius * 2 - 1), fill=255)
        alpha_mask = Image.new("L", rounded_corner_added_image.size, 255)
        w, h = rounded_corner_added_image.size
        alpha_mask.paste(circle_mask.crop((0, 0, radius, radius)), (0, 0))
        alpha_mask.paste(circle_mask.crop((0, radius, radius, radius * 2)), (0, h - radius))
        alpha_mask.paste(circle_mask.crop((radius, 0, radius * 2, radius)), (w - radius, 0))
        alpha_mask.paste(circle_mask.crop((radius, radius, radius * 2, radius * 2)), (w - radius, h - radius))
        rounded_corner_added_image.putalpha(alpha_mask)
        return rounded_corner_added_image

    @staticmethod
    def create_image_with_hover_effect(image: Image, intensity_increase: int) -> Image.Image:
        """
        Create a new image with a hover effect based on the input image

        Args:
            image (Image): Image
            intensity_increase (int): Amount of intensity increase for the hover effect.

        Returns:
            Image: new image with the hover effect.
        """
        image_with_hover_effect = image.convert("RGB")
        image_data = image_with_hover_effect.getdata()
        modified_image_data = []

        for pixel in image_data:
            modified_pixel = list(pixel)
            for index, channel_value in enumerate(modified_pixel):
                new_channel_value = min(channel_value + intensity_increase, 255)
                modified_pixel[index] = new_channel_value
            modified_image_data.append(tuple(modified_pixel))

        image_with_hover_effect.putdata(modified_image_data)
        return image_with_hover_effect

    @staticmethod
    def download_image(image_url: str = None, quality: int = None, output_image_path: str = None) -> str:
        """
        Download an image from the specified URL and save it locally.

        Args:
            image_url (str): URL of the image to download.
            quality (int): Optional. Quality parameter for the image download.
            output_image_path (str): Path to save the downloaded image.

        Returns:
            str: Path to the downloaded image.
        """
        if quality is not None:
            image_url = f"{image_url}?size={quality}"

        request.urlretrieve(image_url, output_image_path)

        return output_image_path

    @staticmethod
    def image_width(input_image_path: str = None) -> int:
        """
        Get a width of image

        Args:
            input_image_path (str): Path to the input image.
        Returns:
            int: Width of the input image
        """
        image = Image.open(input_image_path)

        return image.width

    @staticmethod
    def image_height(input_image_path: str = None) -> int:
        """
        Get a height of image

        Args:
            input_image_path (str): Path to the input image.
        Returns:
            int: Height of the input image
        """
        image = Image.open(input_image_path)

        return image.height

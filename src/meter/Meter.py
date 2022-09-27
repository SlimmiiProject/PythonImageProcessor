from typing import Dict

from pyrect import Box
from re import match
from pytesseract import pytesseract

try:
    from meter.MeterDetectionModel import MeterDetectionModel
except ModuleNotFoundError:
    from MeterDetectionModel import MeterDetectionModel

class Meter:
    __video = None

    def __init__(self, **kwargs: Dict[str, any]) -> None:
        """
        Meter object for meter analyzation (Uses VideoCapture to detect and extract meter information from video)

        :param kwargs: 
            camera_id={int} : cv2.VideoCapture(camera_id)
        """

        # Check voor api key in kwargs (optionele named argumenten, (ex: Meter(api_key="hello world"))
        assert isinstance(kwargs.get("camera_id"), int)
        
        try:
            from meter.MeterVideo import MeterVideo
        except ModuleNotFoundError:
            from MeterVideo import MeterVideo

        self.__video = MeterVideo(self, kwargs.get("camera_id"))

    # region properties (getters)

    @property
    def video_interface(self):
        """
        Get the bound MeterVideo interface.

        :return: MeterVideo(self)
        """
        return self.__video

    @property  # Getter property
    def meter_image(self):
        """
        Get the detected meter image if found, otherwise returns None.

        :return: numpy.ndarray | None
        """

        rect: Box = MeterDetectionModel.getMeterLocation(self.video_interface.camera_frame)
        if rect is None:
            return rect

        return self.video_interface.camera_frame[rect.top:rect.top + rect.height, rect.left:rect.left + rect.width]

    @property  # Getter property
    def meter_value(self):
        """
         Get the current value on meter if valid, otherwise returns None.

        :return: string | None
        """
        output = None
        try:  # Exception capture -> raised soms invalid image object error als frame niet goed gecaptured is.

            # Todo: Image processing toevoegen voor OCR resultaat te optimalizeren

            output = pytesseract.image_to_string(self.meter_image, config="digits")
            # Patroon check is 8 karakters van 0-9 om foute OCR resultaten te filteren (Moet nog uitgebreid worden)
            if not match(r"^[0-9]{8}$", output):
                print("Meter has invalid format: " + output)
                output = None

        except Exception as e:
            print(e)
        finally:
            return output

    # endregion

if __name__ == "__main__":
    meter = Meter(camera_id=0)
    print(meter)
    meter.video_interface.show()
from typing import Dict

from pyrect import Box
from re import match
from pytesseract import pytesseract
from meter.MeterDetectionModel import MeterDetectionModel
from meter.MeterVideo import MeterVideo
from os import path
import cv2

class Meter:
    __source = None
    

    def __init__(self, **kwargs: Dict[str, any]) -> None:
        """
        Meter object for meter analyzation (Uses VideoCapture to detect and extract meter information from video)

        :param kwargs: 
            camera_id={int} : cv2.VideoCapture(camera_id)
        """

        # Check voor api key in kwargs (optionele named argumenten, (ex: Meter(api_key="hello world"))
        assert isinstance(kwargs.get("source"), str)
        if not path.exists(kwargs.get("source")):
            raise FileExistsError("FileNotFound: File did not exist.")

        self.__source = cv2.imread(kwargs.get("source"))



    
    @property  # Getter property
    def meter_image(self):
        """
        Get the detected meter image if found, otherwise returns None.

        :return: numpy.ndarray | None
        """

        rect: Box = MeterDetectionModel.getMeterLocation(self.__source)
        if rect is None:
            return rect

        image = self.__source[rect.top:rect.top + rect.height, rect.left:rect.left + rect.width]
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        tresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        image = cv2.Canny(tresh, 50, 200)

        originalSize = image.shape 
        
        image = cv2.bitwise_not(cv2.resize(tresh, (int(originalSize[1]*.5), int(originalSize[0]*.5))))
        
        # Remove horizontal
        # horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25,1))
        # detected_lines = cv2.morphologyEx(tresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
        # cnts = cv2.findContours(detected_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        # for c in cnts:
        #     cv2.drawContours(tresh, [c], -1, (255,255,255), 2)

        return image

    @property  # Getter property
    def meter_value(self):
        """
         Get the current value on meter if valid, otherwise returns None.

        :return: string | None
        """
        output = None
        try:  # Exception capture -> raised soms invalid image object error als frame niet goed gecaptured is.
            # Todo: Image processing toevoegen voor OCR resultaat te optimalizeren
            output = pytesseract.image_to_string(self.meter_image, config="--psm 8 digits")
            # Patroon check is 8 karakters van 0-9 om foute OCR resultaten te filteren (Moet nog uitgebreid worden)
            if not match(r"^[0-9]{8}$", output):
                print("Meter has invalid format: " + output)
                output = None
        except Exception as e:
            print(e)
        finally:
            return output

    # endregion
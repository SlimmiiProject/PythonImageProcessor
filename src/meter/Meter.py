import re
from typing import Dict

from pyrect import Box
from re import match
from pytesseract import pytesseract
from meter.MeterDetectionModel import MeterDetectionModel
from meter.MeterVideo import MeterVideo
from os import path, listdir
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
        print(listdir("../"))
        assert isinstance(kwargs.get("source"), str)
        if not path.exists(kwargs.get("source")):
            raise FileExistsError("FileNotFound: File did not exist.")

        self.__source = cv2.imread(kwargs.get("source"))

    
    @property  # Getter property
    def meter_images(self):
        """
        Get the detected meter image if found, otherwise returns None.

        :return: numpy.ndarray | None
        """

        rects: Box = MeterDetectionModel.getMeterLocation(self.__source)
        if rects is None or not len(rects):
            return rects

        output = []
        for rect in rects:
            image = self.__source[rect.top:rect.top + rect.height, rect.left:rect.left + rect.width]
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            tresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            image = cv2.Canny(tresh, 50, 200)

            originalSize = image.shape

            image = cv2.bitwise_not(cv2.resize(tresh, (int(originalSize[1]*.5), int(originalSize[0]*.5))))
            output.append(image)

        return output

    @property  # Getter property
    def meter_value(self):
        """
         Get the current value on meter if valid, otherwise returns None.

        :return: string | None
        """
        output = {"dag": -1, "nacht": -1}

        try:  # Exception capture -> raised soms invalid image object error als frame niet goed gecaptured is.
            images = self.meter_images
            for i in range(0, len(images)):
                # Todo: Image processing toevoegen voor OCR resultaat te optimalizeren
                output["dag" if i == 0 else "nacht"] = re.sub("[a-zA-Z-\n]*", "", pytesseract.image_to_string(images[i], config="--psm 8 digits"))
        except Exception as e:
            print(e)
        finally:
            print(output)
            return output

    # endregion
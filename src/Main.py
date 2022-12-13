from argparse import ArgumentParser
from typing import Dict
import cv2

from pytesseract import pytesseract
import winreg
from platform import system

from meter.Meter import Meter
from meter.MeterDetectionModel import MeterDetectionModel

# Meer comments en beschrijving komen er aan, code is eerst geschreven en dan de comments dus nog even geduld voor de hele documentatie ':) 
    
class Main:
    def __init__(self, **kwargs: Dict[str, any]):
        """
        Main application entry point

        :param kwargs: 
            camera_id={int} : OpenCV camera id
            api_key={str}   : Roboflow API Key for ObjectDetectionModel 
            headless={bool} :  No video display?
        """
        # Stel tesseract in indien op windows, op linux is dit meestal all geinstalleerd
        if system() == "Windows":
            try:
                registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)

                tesseract_registry_key = winreg.OpenKey(registry, "SOFTWARE\Tesseract-OCR")
                _, path, _ = winreg.EnumValue(tesseract_registry_key, 0)

                pytesseract.tesseract_cmd = r'{root}\tesseract.exe'.format(root=path)
            except FileNotFoundError:
                print("Tesseract OCR not installed, download and install from: https://tesseract-ocr.github.io/tessdoc/Installation.html")
                return

        # Stel roboflow API key in (tijdelijk voor MeterDetectionModel moet vervangen worden met offline model)
        assert "api_key" in list(kwargs.keys())
        assert isinstance(kwargs.get("api_key"), str)

        MeterDetectionModel.setAPIKey(kwargs.get("api_key"))

        # Creer meter parser object gebaseerd op CLI argument "camera_id" (default: 0)
        self.__meter = Meter(**kwargs)
        self.__Start()

    def __Start(self):
        """
            Start application if all checks verified.

            :param headless: No video display
        """
        print(self.__meter.meter_value)


if __name__ == '__main__':
    # Creer CLI argumenten object.
    parser = ArgumentParser()
    parser.add_argument("--api_key", metavar="api_key", type=str, help="Roboflow API Key")
    parser.add_argument("--source", metavar="source", type=str, help="Input source filepath")

    # Parse CLI argumenten.
    args = parser.parse_args()

    # Verkrijg alle namen van args object, filter protected/private functies en variabele en zet om in een list -
    # loop over die list en maak hiervan een tupel van de naam / waarde, convert deze dan naar een dict.
    # Gebruik deze als volgt als "named parameters" met de **kwargs optie.
    Main(**dict([(i, args.__getattribute__(i)) for i in list(filter(lambda i: not i.startswith("_"), dir(args)))]))
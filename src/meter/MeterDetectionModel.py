import cv2

from pyrect import Box
from roboflow import Roboflow
from roboflow.core.workspace import Workspace
from roboflow.models.object_detection import ObjectDetectionModel


class __MeterDetectionModel:
    __rf: Roboflow = None
    __rf_workspace: Workspace = None
    __rf_model: ObjectDetectionModel = None
    __frame_filepath: str = "./currentFrame.png"

    def setAPIKey(self, key: str) -> None:
        """
        Set the roboflow API key for fetching dataset.

        :param key:
        :return:
        """
        # In laden van dataset en ObjectDetection model uit workspace object halen.
        self.__rf = Roboflow(api_key=key)
        self.__rf_workspace = self.__rf.workspace("jannick-oste-yamid").project("gasmeter-belgium")
        self.__rf_model = self.__rf_workspace.version(3).model

    def getMeterLocation(self, frame) -> Box:
        """
        Get area where meter is located in (x, y, width, height)

        :return: Box
        """
        # Slaag frame op voor ObjectDetection model en probeer meter locatie te verkrijgen
        cv2.imwrite(self.__frame_filepath, frame)
        predictions = self.__rf_model.predict(self.__frame_filepath, confidence=40, overlap=30).json()["predictions"]

        # Indien niet gevonde geef niet return, anders een Box van (x, y, width, height)
        if len(predictions) == 0:
            return None
        else:
            prediction = predictions[0]

            return Box(
                # X, Y
                int(prediction["x"] - (prediction["width"] / 2)), int(prediction["y"] - (prediction["height"] / 2)),
                # Width, Height
                int(prediction["width"]), int(prediction["height"])
            )


# Singleton patroon, zo wordt de API maar éénmaal ingeladen
MeterDetectionModel = __MeterDetectionModel()

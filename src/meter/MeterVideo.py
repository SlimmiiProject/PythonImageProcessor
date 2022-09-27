import cv2
from numpy import ndarray


class MeterVideo:
    __fontStyle = {
        "fontFace": cv2.FONT_HERSHEY_COMPLEX,
        "fontScale": 1,
        "thickness": 1
    }

    def __init__(self, meter, camera_id) -> None:
        """
        Meter video interface

        :param meter: target meter
        """
        try:
            from meter.Meter import Meter
        except ModuleNotFoundError:
            from Meter import Meter

       # assert isinstance(meter, Meter)
        assert isinstance(camera_id, int)

        self.__meter = meter
        self.__camera = cv2.VideoCapture(camera_id)

    @property  # Getter property
    def camera_frame(self):
        """
        Get the current frame from bound VideoCapture

        :return: numpy.ndarray
        """
        _, frame = self.__camera.read()

        return frame

    @property
    def info_frame(self) -> ndarray:
        """
        Current frame on bound meter's camera with additional information

        :return: numpy.ndarray
        """
        frame: ndarray = self.camera_frame

        try:
            # Meter state verkrijgen met binary checks en text instellen gebaseerd op resultaat.
            text: str = ""
            if self.__meter.meter_image is None:
                text = "Meter not found"
            else:
                meter_value = self.__meter.meter_value
                text = meter_value if meter_value is not None else "Invalid meter value"

            # Verkrijg font en image grote
            font_width, font_height = cv2.getTextSize(text=text, **self.__fontStyle)[0]
            frameWidth, frameHeight, _ = frame.shape

            cv2.putText(
                frame,
                text=text,
                org=(int(frameWidth - (font_width / 2)), int((frameHeight * .7) - font_height)),
                color=(0, 255, 255),
                **self.__fontStyle
            )

        except Exception as e:
            print("[{className}]: Exception captured\n{err}".format(className="MeterCamera", err=e))

        return frame

    def show(self, **kwargs):
        """
        Show camera of current bound meter target (default with optional info, can be disabled using kwargs)

        :param kwargs: 
            *info={true/false}: Display state information
        :return: None
        """

        info = kwargs.get("info") if "info" in list(kwargs.keys()) else True
        assert isinstance(info, bool)

        frame_override = kwargs.get("frame")
        while True:
            try:
                cv2.imshow('Camera ', frame_override if frame_override is not None else (self.info_frame if info else self.camera_frame))
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            except Exception as e:
                print(e)
                continue

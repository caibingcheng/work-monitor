import cv2
import os
import datetime
import time
import pathlib

from monitor.log import Logging
from monitor.config import platform


class Capture(object):
    captured_frames_ = 0
    max_retry_ = 10

    @staticmethod
    def captured_frames():
        return Capture.captured_frames_

    def __init__(self, video_path_for_debug="", config=None):
        self.config_ = config
        if self.config_ is None:
            raise ValueError("config is None")

        self.live_ = False
        self.cap_ = None
        self.one_shot_ = False
        if video_path_for_debug != "" and pathlib.Path(video_path_for_debug).exists():
            Logging.info(f"Load frames from {video_path_for_debug}")
            self.cap_ = cv2.VideoCapture(video_path_for_debug)
        else:
            # no file specified, use camera
            self.live_ = True
            self.prefered_api_ = cv2.CAP_V4L2
            if platform == "nt":
                self.prefered_api_ = cv2.CAP_DSHOW

    def update_config(self, config):
        self.config_ = config

    def get_capture(self):
        self.one_shot_ = self.config_["capture_mode"] == "one_shot"

        if self.live_ and self.cap_ is None:
            self.cap_ = cv2.VideoCapture(self.config_["camera_id"], self.prefered_api_)

        if not self.cap_.isOpened():
            Logging.error("Capture not valid")
            raise Exception(
                "Capture not valid, camera id: " + str(self.config_["camera_id"]),
                ", please verify the config: ",
                str(self.config_["config_dir"] / "config.json"),
            )

        return self.cap_.read()

    def release_capture(self):
        if self.live_ and self.one_shot_:
            self.cap_.release()
            self.cap_ = None

    def capture(self):
        max_retry = Capture.max_retry_

        while True:
            ret, frame = self.get_capture()
            if not ret:
                time.sleep(1)
                max_retry -= 1
                if max_retry == 0:
                    Logging.error(f"Open camera failed, retrying {max_retry}")
                    raise Exception("Open camera failed")
                else:
                    Logging.error(f"Open camera failed, retrying {max_retry}")
                continue

            capture_date = datetime.datetime.now()
            # 2021/01/01 00:00:00.000
            frame_date = capture_date.strftime("%Y/%m/%d %H:%M:%S.%f")
            frame_date = frame_date[:-3]
            Logging.info(f"Captured {frame_date}")
            cv2.putText(
                frame,
                frame_date,
                (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                # yellow
                (0, 255, 255),
                2,
                cv2.LINE_AA,
            )

            # set jpeg quality
            capture_date = capture_date.strftime("%Y%m%d%H%M%Ss%f")
            capture_date = capture_date[:-3]
            cv2.imwrite(
                f"{self.config_['frames_dir']}/{capture_date}.jpeg",
                frame,
                [int(cv2.IMWRITE_JPEG_QUALITY), self.config_["quality"]],
            )
            Capture.captured_frames_ += 1

            self.release_capture()

            break

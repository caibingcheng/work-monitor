import cv2
import os
import datetime
import time
import pathlib

from monitor.log import Logging


class Capture(object):
    captured_frames_ = 0
    max_retry_ = 10

    @staticmethod
    def captured_frames():
        return Capture.captured_frames_

    def __init__(self, video_path_for_debug="", config=None):
        self.config_ = config
        self.video_path_for_debug_ = video_path_for_debug
        self.cap_ = None
        self.live_ = True
        if (
            self.video_path_for_debug_ != ""
            and pathlib.Path(self.video_path_for_debug_).exists()
        ):
            Logging.info(f"Load frames from {self.video_path_for_debug_}")
            self.cap_ = cv2.VideoCapture(self.video_path_for_debug_)
            self.live_ = False

    def update_config(self, config):
        self.config_ = config

    def capture(self):
        max_retry = Capture.max_retry_

        while True:
            # no file specified, use camera
            if self.cap_ is None:
                self.cap_ = cv2.VideoCapture(self.config_["camera_id"], cv2.CAP_V4L2)
            if not self.cap_.isOpened():
                Logging.error("Capture not valid")
                raise Exception("Capture not valid")

            ret, frame = self.cap_.read()
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

            if self.live_:
                self.cap_.release()
            break

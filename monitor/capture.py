import cv2
import os
import datetime
import time

from monitor.config import config
from monitor.log import log_info, log_error


def capture(video_path_for_debug=""):
    max_retry = 10

    while True:
        # no log print
        cap = (
            cv2.VideoCapture(video_path_for_debug)
            if video_path_for_debug
            else cv2.VideoCapture(config["camera_id"], cv2.CAP_V4L2)
        )
        if not cap.isOpened():
            log_error("Capture not valid")
            raise Exception("Capture not valid")
        ret, frame = cap.read()
        if not ret:
            time.sleep(1)
            max_retry -= 1
            if max_retry == 0:
                log_error("Failed to capture")
                cap.release()
                # kill the process
                this_pid = os.getpid()
                os.system(f"kill {this_pid}")
            else:
                log_error(f"Open camera failed, retrying {max_retry}")
            continue
        capture_date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        log_info(f"Capturing {capture_date}")
        # set jpeg quality
        cv2.imwrite(
            f"{config['frames_dir']}/{capture_date}.jpeg",
            frame,
            [int(cv2.IMWRITE_JPEG_QUALITY), config["quality"]],
        )

        cap.release()
        break


if __name__ == "__main__":
    capture()
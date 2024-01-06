import time

from monitor.capture import capture
from monitor.video import generate_video, all_frames
from monitor.config import config


def easy_policy(video_path_for_debug):
    easy_config = config["easy_policy"]
    if len(all_frames()) >= easy_config["frames_per_video"]:
        generate_video()
    capture(video_path_for_debug)
    time.sleep(easy_config["frames_interval"])

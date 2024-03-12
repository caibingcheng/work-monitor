import time

from monitor.capture import capture
from monitor.video import generate_video, all_frames
from monitor.config import config

frames_count = len(all_frames())
def easy_policy(**kwargs):
    easy_config = config["easy_policy"]
    frames_per_video = easy_config["frames_per_video"]
    frames_interval = easy_config["frames_interval"]

    global frames_count
    if frames_count >= frames_per_video:
        generate_video()
        frames_count = 0

    # update the actual frames count, but not frequently
    if frames_count == (frames_per_video // 2):
        frames_count = len(all_frames())

    capture(kwargs.get("video_path_for_debug", ""))
    frames_count += 1
    time.sleep(frames_interval)

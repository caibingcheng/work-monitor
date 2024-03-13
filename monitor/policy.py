import time

from monitor.capture import Capture
from monitor.video import Video
from monitor.config import Config
from monitor.log import Logging


def is_in_time_range(time_range_str):
    def parse_time_range(time_range):
        pairs = time_range.split(",")
        result = []
        for pair in pairs:
            start, end = pair.split("-")
            result.append((start, end))
        return result

    time_range = parse_time_range(time_range_str)

    current_time = time.localtime()
    current_time_str = time.strftime("%H:%M", current_time)
    for time_pair in time_range:
        start, end = time_pair.split("-")
        if start <= current_time_str <= end:
            return True
    return False


frames_count = len(all_frames())
log_debug(f"Initial frames count: {frames_count}")


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
        log_debug(f"Before update frames count: {frames_count}")
        frames_count = len(all_frames())
        log_debug(f"After update frames count: {frames_count}")

    capture(kwargs.get("video_path_for_debug", ""))
    frames_count += 1
    time.sleep(frames_interval)

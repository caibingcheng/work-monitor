import time

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
    Logging.debug(f"Time range: {time_range}")

    current_time = time.localtime()
    current_time_str = time.strftime("%H:%M", current_time)
    Logging.debug(f"Current time: {current_time_str}")
    for time_pair in time_range:
        Logging.debug(f"Range pair: {time_pair}")
        start, end = time.strftime(
            "%H:%M", time.strptime(time_pair[0], "%H:%M")
        ), time.strftime("%H:%M", time.strptime(time_pair[1], "%H:%M"))
        if start <= current_time_str <= end:
            Logging.debug("In range")
            return True
    Logging.debug("Not in range")
    return False


class PolicyParams(object):
    frames_count = 0


def easy_policy(config, capture, video):
    if PolicyParams.frames_count == 0:
        PolicyParams.frames_count = len(video.all_frames())
        Logging.debug(f"Initial frames count: {PolicyParams.frames_count}")

    easy_config = config["easy_policy"]
    frames_per_video = easy_config["frames_per_video"]
    frames_interval = easy_config["frames_interval"]

    Logging.debug(f"Frames count: {PolicyParams.frames_count}, frames per video: {frames_per_video}, frames interval: {frames_interval}")
    if PolicyParams.frames_count >= frames_per_video and is_in_time_range(
        config["generate_time"]
    ):
        Logging.debug("Generate video")
        video.generate_video()
        PolicyParams.frames_count = 0

    # update the actual frames count, but not frequently
    if PolicyParams.frames_count == (frames_per_video // 2):
        Logging.debug(f"Before update frames count: {PolicyParams.frames_count}")
        PolicyParams.frames_count = len(video.all_frames())
        Logging.debug(f"After update frames count: {PolicyParams.frames_count}")

    capture.capture()
    PolicyParams.frames_count += 1
    time.sleep(frames_interval)

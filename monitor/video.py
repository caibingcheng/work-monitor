import cv2
import time
import pathlib

from monitor.config import config
from monitor.log import log_info

# when generating video, capture will still run
video_in_progress = False


def all_frames(frames_dir=config["frames_dir"]) -> list:
    # when generating video, capture will still run, so do not check frames dir
    global video_in_progress
    if video_in_progress:
        return []

    target_frames_suffix = {".jpeg", ".jpg", ".png"}
    frames = []
    for frame_path in pathlib.Path(frames_dir).glob("*"):
        if frame_path.suffix in target_frames_suffix:
            frames.append(frame_path)
    return frames


def load_frames(frames_dir):
    frames = []
    first_frame_date = None
    last_frame_date = None
    sorted_frame_paths = sorted(all_frames(frames_dir))
    for frame_path in sorted_frame_paths:
        frame = str(frame_path)
        frames.append(frame)
        if not first_frame_date:
            first_frame_date = frame_path.stem
        last_frame_date = frame_path.stem
    frames_date_range = f"{first_frame_date}-{last_frame_date}"
    return frames, frames_date_range


global generated_videos
generated_videos = []


def generate_video_from_frames(frames, frames_date_range, video_dir, fps):
    base_frame = cv2.imread(frames[0])
    height, width, _ = base_frame.shape
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    output_path = pathlib.Path(video_dir) / f"{frames_date_range}.mp4"
    if output_path.exists():
        log_info(f"Removing existing video {output_path}")
        output_path.unlink()
    log_info(f"Generating video {output_path}")
    video = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

    skip_write = False
    frame_save = config["frames_save"]
    for frame_path in frames:
        frame = cv2.imread(frame_path)
        if not frame_save:
            pathlib.Path(frame_path).unlink()
        if not skip_write:
            video.write(frame)
    video.release()
    log_info(f"Video generated {output_path}")

    global generated_videos
    generated_videos.append(frames_date_range)

    global video_in_progress
    video_in_progress = False


def generate_video():
    # only one video can be generated at a time
    global video_in_progress
    if video_in_progress:
        return

    log_info("Generating video")
    frames, frames_date_range = load_frames(config["frames_dir"])
    log_info(f"Total frames: {len(frames)}, date range: {frames_date_range}")
    if not frames:
        return

    video_in_progress = True
    import threading

    threading.Thread(
        target=generate_video_from_frames,
        args=(frames, frames_date_range, config["video_dir"], config["fps"]),
    ).start()


if __name__ == "__main__":
    generate_video()

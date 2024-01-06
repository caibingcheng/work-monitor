import cv2
import pathlib

from monitor.config import config
from monitor.log import log_info


def all_frames(frames_dir=config["frames_dir"]) -> list:
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
        frame = cv2.imread(str(frame_path))
        frames.append(frame)
        if not first_frame_date:
            first_frame_date = frame_path.stem
        last_frame_date = frame_path.stem
    frames_date_range = f"{first_frame_date} - {last_frame_date}"
    if not config["frames_save"]:
        log_info("Removing frames")
        for frame_path in sorted_frame_paths:
            frame_path.unlink()
    return frames, frames_date_range


def generate_video_from_frames(frames, frames_date_range, video_dir, fps):
    height, width, _ = frames[0].shape
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    output_path = pathlib.Path(video_dir) / f"{frames_date_range}.mp4"
    log_info(f"Generating video {output_path}")
    video = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    for frame in frames:
        video.write(frame)
    video.release()


def generate_video():
    frames, frames_date_range = load_frames(config["frames_dir"])
    if not frames:
        return
    generate_video_from_frames(
        frames, frames_date_range, config["video_dir"], config["fps"]
    )


if __name__ == "__main__":
    generate_video()

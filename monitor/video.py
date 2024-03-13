import cv2
import time
import pathlib

from monitor.log import Logging


class Video(object):
    # when generating video, capture will still run
    video_in_progress_ = False
    generated_videos_ = []

    @staticmethod
    def generated_videos():
        return Video.generated_videos_

    def __init__(self, config=None):
        self.config_ = config

    def update_config(self, config):
        self.config_ = config

    def all_frames(self) -> list:
        frames_dir = self.config_["frames_dir"]
        # when generating video, capture will still run, so do not check frames dir
        if Video.video_in_progress_:
            return []

        target_frames_suffix = {".jpeg", ".jpg", ".png"}
        frames = []
        for frame_path in pathlib.Path(frames_dir).glob("*"):
            if frame_path.suffix in target_frames_suffix:
                frames.append(frame_path)
        return frames

    def generate_video(self):
        # only one video can be generated at a time
        if Video.video_in_progress_:
            Logging.debug("Video in progress, skip generating video")
            return

        Logging.info("Generating video")
        frames, frames_date_range = self.load_frames_()
        Logging.info(f"Total frames: {len(frames)}, date range: {frames_date_range}")
        if not frames:
            return

        Video.video_in_progress_ = True
        import threading

        threading.Thread(
            target=self.generate_video_from_frames_,
            args=(
                frames,
                frames_date_range,
                self.config_["video_dir"],
                self.config_["fps"],
            ),
        ).start()

    def load_frames_(self):
        frames_dir = self.config_["frames_dir"]
        frames = []
        first_frame_date = None
        last_frame_date = None
        sorted_frame_paths = sorted(self.all_frames())
        for frame_path in sorted_frame_paths:
            frame = str(frame_path)
            frames.append(frame)
            if not first_frame_date:
                first_frame_date = frame_path.stem
            last_frame_date = frame_path.stem
        frames_date_range = f"{first_frame_date}-{last_frame_date}"
        return frames, frames_date_range

    def generate_video_from_frames_(self, frames, frames_date_range, video_dir, fps):
        base_frame = cv2.imread(frames[0])
        height, width, _ = base_frame.shape
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        output_path = pathlib.Path(video_dir) / f"{frames_date_range}.mp4"
        if output_path.exists():
            Logging.info(f"Removing existing video {output_path}")
            output_path.unlink()
        Logging.info(f"Generating video {output_path}")
        video = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

        skip_write = False
        frame_save = self.config_["frames_save"]
        for frame_path in frames:
            frame = cv2.imread(frame_path)
            if not frame_save:
                pathlib.Path(frame_path).unlink()
            if not skip_write:
                video.write(frame)
        video.release()
        Logging.info(f"Video generated {output_path}")

        Video.generated_videos_.append(frames_date_range)
        self.remove_outdated_videos_(video_dir)

        Video.video_in_progress_ = False

    def remove_outdated_videos_(self, video_dir):
        video_paths = sorted(pathlib.Path(video_dir).glob("*.mp4"))
        filtered_video_paths = []

        import re

        # the pattern is like "20240107153612s239-20240107153637s319.mp4"
        for video_path in video_paths:
            match = re.search(r"(\d+s\d+)-(\d+s\d+)", video_path.stem)
            if not match:
                continue
            start, end = video_path.stem.split("-")
            if len(start) != 18 or len(end) != 18:
                continue
            filtered_video_paths.append(video_path)

        Logging.debug(f"Found {len(filtered_video_paths)} videos")

        sorted_video_paths = sorted(filtered_video_paths)
        for video_path in sorted_video_paths[: -self.config_["iterations"]]:
            Logging.info(f"Removing outdated video {video_path}")
            video_path.unlink()

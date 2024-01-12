import sys
import pathlib
import datetime
import os

from monitor.config import config

latest_log_file = None


def get_latest_log_file():
    def generate_log_file_by_date():
        current_date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        log_path = pathlib.Path(config["log_dir"]) / f"{current_date}.log"
        log_path.touch()
        return log_path

    log_files = sorted(pathlib.Path(config["log_dir"]).glob("*.log"))
    global latest_log_file
    if not log_files:
        latest_log_file = generate_log_file_by_date()
        return
    latest_log_file = log_files[-1]
    # size > 1 MB
    if latest_log_file.stat().st_size > 1e6:
        latest_log_file = generate_log_file_by_date()
    # max 10 files
    if len(log_files) > 10:
        log_files[0].unlink()


def should_generate_new_log_file():
    global latest_log_file
    if not latest_log_file:
        get_latest_log_file()
    if latest_log_file.stat().st_size > 1e6:
        return True
    return False


def write_log(tag, *args, **kwargs):
    global latest_log_file
    if should_generate_new_log_file():
        get_latest_log_file()

    # caller_name = sys._getframe(2).f_code.co_name
    caller_file = sys._getframe(2).f_code.co_filename
    caller_line = sys._getframe(2).f_lineno
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    caller_file = pathlib.Path(caller_file).name
    caller_info = f"{caller_file}:{caller_line}"
    prefix_info = f"{current_time} [{os.getpid()}] {tag} {caller_info}"
    message = f"{prefix_info} {' '.join([str(arg) for arg in args])} {' '.join([f'{key}={value}' for key, value in kwargs.items()])}"
    with open(latest_log_file, "a") as f:
        print(message, file=f)
    return message


def log_info(*args, **kwargs):
    print(write_log("[INFO ]", *args, **kwargs))


def log_error(*args, **kwargs):
    print(write_log("[ERROR]", *args, **kwargs))

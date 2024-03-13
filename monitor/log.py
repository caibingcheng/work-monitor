import sys
import pathlib
import datetime
import os


class Logging(object):
    log_levels_ = ["FATAL", "ERROR", "WARN", "INFO", "DEBUG"]
    latest_log_file_ = None
    log_level_ = 3
    config_ = None

    @staticmethod
    def update_config(config):
        Logging.config_ = config

    @staticmethod
    def update_log_level(log_level):
        Logging.log_level_ = Logging.log_levels_.index(log_level)

    @staticmethod
    def info(*args, **kwargs):
        Logging.log_("INFO", *args, **kwargs)

    @staticmethod
    def error(*args, **kwargs):
        Logging.log_("ERROR", *args, **kwargs)

    @staticmethod
    def debug(*args, **kwargs):
        Logging.log_("DEBUG", *args, **kwargs)

    @staticmethod
    def warn(*args, **kwargs):
        Logging.log_("WARN", *args, **kwargs)

    @staticmethod
    def fatal(*args, **kwargs):
        Logging.log_("FATAL", *args, **kwargs)

    @staticmethod
    def write(tag, *args, **kwargs):
        if Logging.should_generate_new_log_file_():
            Logging.get_latest_log_file_()

        # caller_name = sys._getframe(2).f_code.co_name
        caller_file = sys._getframe(2).f_code.co_filename
        caller_line = sys._getframe(2).f_lineno
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        caller_file = pathlib.Path(caller_file).name
        caller_info = f"{caller_file}:{caller_line}"
        prefix_info = f"{current_time} [{os.getpid()}] {tag} {caller_info}"
        message = f"{prefix_info} {' '.join([str(arg) for arg in args])} {' '.join([f'{key}={value}' for key, value in kwargs.items()])}"
        with open(Logging.latest_log_file_, "a") as f:
            print(message, file=f)
        return message

    @staticmethod
    def get_latest_log_file_():
        def generate_log_file_by_date():
            current_date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            log_path = pathlib.Path(Logging.config_["log_dir"]) / f"{current_date}.log"
            log_path.touch()
            return log_path

        log_files = sorted(pathlib.Path(Logging.config_["log_dir"]).glob("*.log"))
        if not log_files:
            Logging.latest_log_file_ = generate_log_file_by_date()
            return
        Logging.latest_log_file_ = log_files[-1]
        # size > 1 MB
        if Logging.latest_log_file_.stat().st_size > 1e6:
            Logging.latest_log_file_ = generate_log_file_by_date()
        # max 10 files
        if len(log_files) > 10:
            log_files[0].unlink()

    @staticmethod
    def should_generate_new_log_file_():
        if not Logging.latest_log_file_:
            Logging.get_latest_log_file_()
        if Logging.latest_log_file_.stat().st_size > 1e6:
            return True
        return False

    @staticmethod
    def log_(level, *args, **kwargs):
        Logging.check_config_ready_()
        if Logging.log_levels_.index(level) > Logging.log_level_:
            return
        print(Logging.write(f"[{level}]", *args, **kwargs))

    @staticmethod
    def check_config_ready_():
        if not Logging.config_:
            raise Exception("Logging config not ready")

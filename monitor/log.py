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
    def update_config(self, config):
        self.config_ = config

    @staticmethod
    def update_log_level(self, log_level):
        self.log_level_ = self.log_levels_.index(log_level)

    @staticmethod
    def info(self, *args, **kwargs):
        self.log_("INFO", *args, **kwargs)

    @staticmethod
    def error(self, *args, **kwargs):
        self.log_("ERROR", *args, **kwargs)

    @staticmethod
    def debug(self, *args, **kwargs):
        self.log_("DEBUG", *args, **kwargs)

    @staticmethod
    def warn(self, *args, **kwargs):
        self.log_("WARN", *args, **kwargs)

    @staticmethod
    def fatal(self, *args, **kwargs):
        self.log_("FATAL", *args, **kwargs)

    @staticmethod
    def get_latest_log_file_(self):
        def generate_log_file_by_date():
            current_date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            log_path = pathlib.Path(self.config_["log_dir"]) / f"{current_date}.log"
            log_path.touch()
            return log_path

        log_files = sorted(pathlib.Path(self.config_["log_dir"]).glob("*.log"))
        if not log_files:
            self.latest_log_file_ = generate_log_file_by_date()
            return
        self.latest_log_file_ = log_files[-1]
        # size > 1 MB
        if self.latest_log_file_.stat().st_size > 1e6:
            self.latest_log_file_ = generate_log_file_by_date()
        # max 10 files
        if len(log_files) > 10:
            log_files[0].unlink()

    @staticmethod
    def should_generate_new_log_file_(self):
        if not self.latest_log_file_:
            self.get_latest_log_file_()
        if self.latest_log_file_.stat().st_size > 1e6:
            return True
        return False

    @staticmethod
    def write_log_(self, tag, *args, **kwargs):
        if self.should_generate_new_log_file_():
            self.get_latest_log_file_()

        # caller_name = sys._getframe(2).f_code.co_name
        caller_file = sys._getframe(2).f_code.co_filename
        caller_line = sys._getframe(2).f_lineno
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        caller_file = pathlib.Path(caller_file).name
        caller_info = f"{caller_file}:{caller_line}"
        prefix_info = f"{current_time} [{os.getpid()}] {tag} {caller_info}"
        message = f"{prefix_info} {' '.join([str(arg) for arg in args])} {' '.join([f'{key}={value}' for key, value in kwargs.items()])}"
        with open(self.latest_log_file_, "a") as f:
            print(message, file=f)
        return message

    @staticmethod
    def log_(self, level, *args, **kwargs):
        self.check_config_ready_()
        if self.log_levels_.index(level) > self.log_level_:
            return
        print(self.write_log_(f"[{level}]", *args, **kwargs))

    @staticmethod
    def check_config_ready_(self):
        if not self.config_:
            raise Exception("Logging config not ready")

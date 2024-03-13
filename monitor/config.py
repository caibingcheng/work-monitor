import json
import os
import pathlib


class Config(object):
    raw_config_ = {
        "camera_id": 0,
        "video_dir": "$HOME/Videos",
        "frames_dir": "$HOME/Pictures/work-monitor",
        "config_dir": "$HOME/.work-monitor",
        "log_dir": "$HOME/.work-monitor/log",
        "fps": 60,
        "quality": 75,
        "frames_save": False,
        "generate_time": "23:00-00:00,00:00-06:00",
        "iterations": 10,
        "policy": "easy_policy",
        "easy_policy": {"frames_interval": 10, "frames_per_video": 1000},
        "server": {
            "port": 22311,
        },
    }
    config_ = None

    @staticmethod
    def get():
        return Config.config_.copy()

    @staticmethod
    def set(value):
        Config.config_ = value

    @staticmethod
    def init() -> None:
        if Config.config_ is not None:
            return

        Config.config_ = Config.raw_config_.copy()
        try:
            Config.config_ = Config.initialize_config(Config.config_)
            Config.verify_config(Config.config_)
        except Exception as e:
            print(e)
            choise = input("Reset config? (y/n)")
            if choise == "y":
                print("Resetting config")
                Config.config_ = Config.update_better_config(
                    Config.config_, Config.raw_config_
                )
                print("Raw config: ")
                print(json.dumps(Config.raw_config_, indent=4))
                print("Current config: ")
                print(json.dumps(Config.config_, indent=4))
                Config.config_ = Config.initialize_config(Config.config_, force=True)
            else:
                print("Using raw config")
                Config.config_ = Config.raw_config_
        Config.config_ = Config.preprocess_config(Config.config_)
        Config.verify_config(Config.config_)

    @staticmethod
    def update_config(config, other_config):
        config.update(other_config)
        return config

    @staticmethod
    def parse_time_range(config, key):
        pairs = config[key].split(",")
        result = []
        for pair in pairs:
            start, end = pair.split("-")
            start = list(map(int, start.split(":")))
            end = list(map(int, end.split(":")))
            result.append((start, end))
        return result

    @staticmethod
    def preprocess_config(config):
        def replace_env_var(config):
            for key, value in config.items():
                if isinstance(value, str):
                    config[key] = value.replace("$HOME", os.environ["HOME"])
                elif isinstance(value, dict):
                    replace_env_var(value)

        def replace_stringnumber_to_number(config):
            for key, value in config.items():
                if isinstance(value, str):
                    if value.isdigit():
                        config[key] = int(value)
                    elif value.replace(".", "", 1).isdigit():
                        config[key] = float(value)
                elif isinstance(value, dict):
                    replace_stringnumber_to_number(value)

        def create_dir_if_not_exist(config):
            for key, value in config.items():
                if isinstance(value, str) and key.endswith("_dir"):
                    config[key] = pathlib.Path(value)
                    pathlib.Path(value).mkdir(parents=True, exist_ok=True)
                elif isinstance(value, dict):
                    create_dir_if_not_exist(value)

        def reset_value_range(config, key, min_value, max_value):
            if key not in config:
                return
            if config[key] < min_value:
                config[key] = min_value
            elif config[key] > max_value:
                config[key] = max_value

        replace_env_var(config)
        replace_stringnumber_to_number(config)
        create_dir_if_not_exist(config)
        reset_value_range(config, "quality", 0, 100)
        return config

    @staticmethod
    def stringify_config(config):
        def stringify(config):
            for key, value in config.items():
                if isinstance(value, pathlib.Path):
                    config[key] = str(value)
                elif isinstance(value, dict):
                    stringify(value)

        stringify(config)
        return config

    @staticmethod
    def initialize_config(config, force=False):
        Config.preprocess_config(config)
        config_path = config["config_dir"] / "config.json"
        if not config_path.exists() or force:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            json.dump(Config.stringify_config(config), open(config_path, "w"), indent=4)
        config = json.load(open(config_path))
        return config

    @staticmethod
    def verify_config(config):
        raw_config_keys = set()
        config_keys = set()

        def append_sub_keys(keys, config, prefix=""):
            for key, value in config.items():
                keys.add(f"{prefix}{key}")
                if isinstance(value, dict):
                    append_sub_keys(keys, value, prefix=f"{prefix}{key}_")

        append_sub_keys(raw_config_keys, Config.raw_config_)
        append_sub_keys(config_keys, config)

        if raw_config_keys != config_keys:
            not_match = raw_config_keys ^ config_keys
            raise Exception("Config keys not match", not_match)

    @staticmethod
    def update_better_config(config, raw_config):
        def update_better_config_helper(config, raw_config):
            for key, value in config.items():
                if key not in raw_config:
                    config.pop(key)
                    continue
                if type(value) != type(raw_config[key]):
                    config[key] = raw_config[key]
                if isinstance(value, dict):
                    update_better_config_helper(value, raw_config[key])

        update_better_config_helper(config, raw_config)

        def add_missing_keys(config, raw_config):
            for key, value in raw_config.items():
                if key not in config:
                    config[key] = value
                if isinstance(value, dict):
                    add_missing_keys(config[key], value)

        add_missing_keys(config, raw_config)

        return config

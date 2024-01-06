import json
import os
import pathlib

raw_config = {
    "camera_id": 0,
    "video_dir": "$HOME/Videos",
    "frames_dir": "$HOME/Pictures/work-monitor",
    "config_dir": "$HOME/.work-monitor",
    "log_dir": "$HOME/.work-monitor/log",
    "fps": 60,
    "quality": 75,
    "frames_save": False,
    "policy": "easy_policy",
    "easy_policy": {"frames_interval": 10, "frames_per_video": 1000},
    "server": {
        "port": 22311,
    },
}
global config
config = raw_config


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


def stringify_config(config):
    def stringify(config):
        for key, value in config.items():
            if isinstance(value, pathlib.Path):
                config[key] = str(value)
            elif isinstance(value, dict):
                stringify(value)

    stringify(config)
    return config


def initialize_config(config, force=False):
    preprocess_config(config)
    config_path = config["config_dir"] / "config.json"
    if not config_path.exists() or force:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        json.dump(stringify_config(config), open(config_path, "w"), indent=4)
    config = json.load(open(config_path))
    return config


def verify_config(config):
    raw_config_keys = set()
    config_keys = set()

    def append_sub_keys(keys, config, prefix=""):
        for key, value in config.items():
            keys.add(f"{prefix}{key}")
            if isinstance(value, dict):
                append_sub_keys(keys, value, prefix=f"{prefix}{key}_")

    append_sub_keys(raw_config_keys, raw_config)
    append_sub_keys(config_keys, config)
    if raw_config_keys != config_keys:
        raise Exception("Config keys not match", raw_config_keys, config_keys)


def update_config(config, other_config):
    config.update(other_config)
    return config


try:
    config = initialize_config(config)
    verify_config(config)
except Exception as e:
    print(e)
    choise = input("Reset config? (y/n)")
    if choise == "y":
        print("Resetting config")
        config = raw_config
        config = initialize_config(config, force=True)
    else:
        print("Using raw config")
        config = raw_config
config = preprocess_config(config)
verify_config(config)

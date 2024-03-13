import sys
from monitor.config import Config
from monitor.log import Logging


def main():
    Config.init()
    Logging.update_config(Config.get())

    command_section = sys.argv[1] if len(sys.argv) > 1 else "help"
    command_argument = sys.argv[2:] if len(sys.argv) > 2 else []

    from monitor.command import Command

    command = Command.get()
    if command_section not in command:
        raise ValueError(
            f"Section {command_section} not found, valid keys are {command.keys()}"
        )
    command[command_section]["command"](command_section, *command_argument)


if __name__ == "__main__":
    main()

import sys
from monitor.command import command


def main():
    command_section = sys.argv[1] if len(sys.argv) > 1 else "help"
    command_argument = sys.argv[2:] if len(sys.argv) > 2 else []
    if command_section not in command:
        raise ValueError(f"Section {command_section} not found")

    if command[command_section]["server"]:
        command[command_section]["command"](command_section, *command_argument)
    else:
        command[command_section]["command"](*command_argument)


if __name__ == "__main__":
    main()

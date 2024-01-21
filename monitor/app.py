import sys
from monitor.command import command


def main():
    command_section = sys.argv[1] if len(sys.argv) > 1 else "help"
    command_argument = sys.argv[2:] if len(sys.argv) > 2 else []
    if command_section not in command:
        # find smiliar command
        from difflib import get_close_matches

        print(f"Section {command_section} not found")
        similar_command = get_close_matches(command_section, command.keys())
        if similar_command:
            print(f"Did you mean {similar_command[0]}?")
        exit(1)

    # run as server
    if command[command_section]["server"]:
        command[command_section]["command"](command_section, *command_argument)
    else:  # run as client
        command[command_section]["command"](*command_argument)


if __name__ == "__main__":
    main()

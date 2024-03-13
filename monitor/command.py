from monitor.log import Logging
from monitor.config import Config
from monitor.capture import Capture
from monitor.video import Video
from monitor.policy import *


def client_send_msg_to_server(msg, *args):
    from monitor.server import send_msg_to_server

    send_msg = " ".join([msg, *args])
    response = send_msg_to_server(send_msg)

    Logging.write("[INFO ]", "Client received", response)
    if response:
        print(response)


class Command(object):
    command_ = {}

    @staticmethod
    def get():
        return Command.command_

    @staticmethod
    def add_command(name, help="", server=False):
        if not Command.command_:
            from monitor.server import ServerCommand

            server_command = ServerCommand.get()

            for srever_command_name, value in server_command.items():
                Command.command_[srever_command_name] = {
                    "command": client_send_msg_to_server,
                    "help": value["help"],
                    "server": True,
                }
                Logging.debug(
                    f"Command[{srever_command_name}] {Command.command_[srever_command_name]}"
                )

        def decorator(func):
            Command.command_[name] = {
                "command": func,
                "help": help,
                "server": server,
            }
            Logging.debug(f"Command[{name}] {Command.command_[name]}")
            return func

        return decorator


@Command.add_command("help", "Print help")
def help(command_name):
    Logging.debug(f"Command[{command_name}]")
    help_str = """Usage: python3 -m monitor <command> [arguments]
Commands:
"""
    for name, value in Command.get().items():
        help_str += f"    {name}: {value['help']}\n"
    print(help_str)


@Command.add_command("development", "Development mode, show more logs")
def development(command_name, *args):
    Logging.update_log_level("DEBUG")
    Logging.debug(f"Command[{command_name}]")
    server("server", *args)


@Command.add_command("server", "Start server [video_path], default video_path is empty")
def server(command_name, *args):
    Logging.debug(f"Command[{command_name}]")
    Logging.info("Starting")
    config = Config.get()
    policy = config["policy"]
    Logging.info(f"Using policy {policy}")
    # str to function
    policy = globals()[policy]

    video_path_for_debug = "" if len(args) == 0 else args[0]
    video = Video(config)
    capture = Capture(config=config, video_path_for_debug=video_path_for_debug)

    from monitor.server import start_server, should_stop

    start_server()
    while not should_stop():
        try:
            config = Config.get()
            video.update_config(config)
            capture.update_config(config)

            policy(config, capture, video)
        except Exception as e:
            Logging.error(e)
            # backtrace
            import traceback

            traceback.print_exc()
            client_send_msg_to_server("stop")
    Logging.info("Stopped")
    exit(0)

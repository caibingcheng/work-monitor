from monitor.log import log_info, log_error
from monitor.config import config
from monitor.policy import *

global command
command = {}


def add_command(name, help=""):
    def decorator(func):
        global command
        command[name] = {
            "command": func,
            "help": help,
        }
        return func

    return decorator


@add_command("help", "Print help")
def help():
    help_str = """Usage: python3 -m monitor <command> [arguments]
Commands:
"""
    for name, value in command.items():
        help_str += f"    {name}: {value['help']}\n"
    print(help_str)


@add_command("server", "Start server [video_path], default video_path is empty")
def server(*args):
    log_info("Starting")
    policy = config["policy"]
    log_info(f"Using policy {policy}")
    # str to function
    policy = globals()[policy]

    from monitor.server import start_server, should_stop

    start_server()
    video_path_for_debug = "" if len(args) == 0 else args[0]
    while not should_stop():
        try:
            policy(video_path_for_debug)
        except Exception as e:
            log_error(e)
            # backtrace
            import traceback

            traceback.print_exc()
            stop()
    log_info("Stopped")


@add_command("stop", "Client command, stop server")
def stop():
    from monitor.server import send_msg_to_server

    response = send_msg_to_server("stop")
    log_info("Client received", response)


@add_command("restart", "Client command, restart server")
def restart():
    from monitor.server import send_msg_to_server

    response = send_msg_to_server("restart")
    log_info("Client received", response)


@add_command("get_config", "Client command, get config")
def get_config():
    from monitor.server import send_msg_to_server

    response = send_msg_to_server("get_config")
    log_info("Client received", response)


@add_command("set_config", "Client command, set config")
def set_config(*args):
    from monitor.server import send_msg_to_server

    response = send_msg_to_server("set_config " + " ".join(args))
    log_info("Client received", response)

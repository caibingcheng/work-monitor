from monitor.log import log_info, log_error
from monitor.config import config
from monitor.policy import *
from monitor.server import server_command

global command
command = {}


def add_command(name, help="", server=False):
    def decorator(func):
        global command
        command[name] = {
            "command": func,
            "help": help,
            "server": server,
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
            policy(video_path_for_debug=video_path_for_debug)
        except Exception as e:
            log_error(e)
            # backtrace
            import traceback

            traceback.print_exc()
            client_send_msg_to_server("stop")
    log_info("Stopped")
    exit(0)


def client_send_msg_to_server(msg, *args):
    from monitor.server import send_msg_to_server

    send_msg = " ".join([msg, *args])
    response = send_msg_to_server(send_msg)

    from monitor.log import write_log

    write_log("[INFO ]", "Client received", response)
    if response:
        print(response)


for name, value in server_command.items():
    add_command(name, value["help"], server=True)(client_send_msg_to_server)

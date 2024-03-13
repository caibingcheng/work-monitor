# server to receive command from client

import socket
import os
import pathlib
import json
import threading

from monitor.config import Config
from monitor.log import Logging


class ServerCommand(object):
    server_command_ = {}

    @staticmethod
    def get():
        return ServerCommand.server_command_

    @staticmethod
    def add_server_command(name, help=""):
        def decorator(func):
            ServerCommand.server_command_[name] = {
                "command": func,
                "help": help,
            }
            return func

        return decorator


class ServerParams(object):
    should_stop = False


def get_config_string(config):
    config = Config.stringify_config(config)
    config_str = json.dumps(config, indent=4)
    Logging.info(f"Sending config {config_str}")
    return config_str


@ServerCommand.add_server_command("get_config", "Get config")
def get_config_server():
    Logging.info("Sending config")
    return get_config_string(Config.get())


@ServerCommand.add_server_command("set_config", "Set config [key1] [key2] ... [value]")
def set_config_server(*args):
    Logging.info("Setting config")
    if len(args) < 2:
        raise Exception("Not enough arguments")
    current = Config.get()
    current_header = current
    keys = args[:-1]
    value = args[-1]
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            raise Exception(f"Key {key} not found")
        current = current[key]
    current[keys[-1]] = value
    current_header = Config.initialize_config(current_header, force=True)
    config_str = json.dumps(current_header, indent=4)
    Logging.info(f"Sending config {config_str}")
    Config.set(Config.update_config(Config.get(), current_header))
    return config_str


@ServerCommand.add_server_command("stop", "Stop server")
def stop_server():
    Logging.info("Stopping")
    ServerParams.should_stop = True
    exit(0)


def should_stop():
    return ServerParams.should_stop


@ServerCommand.add_server_command("restart", "Restart server")
def restart_server():
    Logging.info("Restarting")
    import sys

    this_command = " ".join(["python3"] + sys.argv)
    this_pid = os.getpid()

    os.system(this_command + " &")
    os.system(f"kill {this_pid}")


@ServerCommand.add_server_command("status", "Get status")
def status_server():
    Logging.info("Getting status")
    from monitor.capture import Capture
    from monitor.video import Video
    from monitor.policy import PolicyParams

    return f"captured_frames: {Capture.captured_frames()}/{PolicyParams.frames_count} generated_videos: {len(Video.generated_videos())}"


def start_server():
    # create a socket object
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # get local machine name
    host = socket.gethostname()
    port = Config.get()["server"]["port"]

    # force to release the port
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # bind to the port
    serversocket.bind((host, port))

    # queue up to 5 requests
    serversocket.listen(5)

    def server_loop():
        Logging.info("Server started")
        server_command = ServerCommand.get()
        while True:
            # establish a connection
            try:
                serversocket.settimeout(60)
                clientsocket, addr = serversocket.accept()
            except socket.timeout:
                continue

            Logging.info(f"Got a connection from {addr}")
            msg = clientsocket.recv(1024).decode("utf-8").split()
            Logging.info(f"Received {msg}")
            argument = msg[1:]
            msg = msg[0]
            try:
                if msg not in server_command:
                    Logging.error(f"Unknown command {msg}")
                    clientsocket.send("failed".encode("utf-8"))
                else:
                    response = server_command[msg]["command"](*argument)
                    if isinstance(response, str):
                        response = response.encode("utf-8")
                    clientsocket.send(response)
            except Exception as e:
                # show backtrace
                Logging.error("Server failed", e)
                Logging.error("Config", Config.get())

                clientsocket.send("failed".encode("utf-8"))
            finally:
                clientsocket.close()

    threading.Thread(target=server_loop).start()


def send_msg_to_server(msg):
    # create a socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # get local machine name
    host = socket.gethostname()
    port = Config.get()["server"]["port"]

    try:
        # connection to hostname on the port.
        client.connect((host, port))
    except Exception as e:
        Logging.error("Client failed to connect to server", e)
        exit(1)

    # Receive no more than 1024 bytes
    client.send(msg.encode("utf-8"))
    response = client.recv(1024).decode("utf-8")
    client.close()

    return response

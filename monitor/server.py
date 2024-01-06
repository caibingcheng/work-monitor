# server to receive command from client

import socket
import os
import pathlib
import json
import threading

from monitor.config import config, stringify_config, initialize_config, update_config
from monitor.log import log_info, log_error

global server_command
server_command = {}


def add_server_command(name):
    def decorator(func):
        global server_command
        server_command[name] = func
        return func

    return decorator


def get_config_string(config):
    config_copy = config.copy()
    config_copy = stringify_config(config_copy)
    config_str = json.dumps(config_copy, indent=4).encode("utf-8")
    log_info(f"Sending config {config_str}")
    return config_str


@add_server_command("get_config")
def get_config_server():
    return get_config_string(config)


@add_server_command("set_config")
def set_config_server(*args):
    if len(args) < 2:
        raise Exception("Not enough arguments")
    current = config.copy()
    current_header = current
    keys = args[:-1]
    value = args[-1]
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            raise Exception(f"Key {key} not found")
        current = current[key]
    current[keys[-1]] = value
    current_header = initialize_config(current_header, force=True)
    config_str = json.dumps(current_header, indent=4).encode("utf-8")
    log_info(f"Sending config {config_str}")
    update_config(config, current_header)
    return config_str


@add_server_command("stop")
def stop_server():
    log_info("Stopping")
    this_pid = os.getpid()
    os.system(f"kill {this_pid}")


@add_server_command("restart")
def restart_server():
    log_info("Restarting")
    import sys

    this_command = " ".join(["python3"] + sys.argv)
    this_pid = os.getpid()

    os.system(this_command + " &")
    os.system(f"kill {this_pid}")


def start_server():
    # create a socket object
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # get local machine name
    host = socket.gethostname()
    port = config["server"]["port"]

    # force to release the port
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # set keep alive
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    serversocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1)
    serversocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 1)
    serversocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)

    # bind to the port
    serversocket.bind((host, port))

    # queue up to 5 requests
    serversocket.listen(5)

    def server_loop():
        log_info("Server started")
        while True:
            # establish a connection
            clientsocket, addr = serversocket.accept()
            log_info(f"Got a connection from {addr}")
            msg = clientsocket.recv(1024).decode("utf-8").split()
            log_info(f"Received {msg}")
            argument = msg[1:]
            msg = msg[0]
            try:
                if msg not in server_command:
                    log_error(f"Unknown command {msg}")
                    clientsocket.send("failed".encode("utf-8"))
                else:
                    clientsocket.send(server_command[msg](*argument))
            except Exception as e:
                # show backtrace
                log_error("Server failed", e)
                log_error("Config", config)

                clientsocket.send("failed".encode("utf-8"))
            finally:
                clientsocket.close()

    threading.Thread(target=server_loop).start()


def send_msg_to_server(msg):
    # create a socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # get local machine name
    host = socket.gethostname()
    port = config["server"]["port"]

    try:
        # connection to hostname on the port.
        client.connect((host, port))
    except Exception as e:
        log_error("Client failed to connect to server", e)
        exit(1)

    # Receive no more than 1024 bytes
    client.send(msg.encode("utf-8"))
    response = client.recv(1024).decode("utf-8")
    client.close()

    return response
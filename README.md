### Work-Monitor

I create this project to monitor my work environment by laptop camera.

This project will capture photo intervally and combined them into a video.

### Usage

Get help.

```bash
python3 -m monitor help
```

Start the monitor server.

```bash
python3 -m monitor server
```

As a client, you can control the monitor server by sending commands to the server.

```bash
# Stop the monitor server.
python3 -m monitor stop
# Get the monitor server config
python3 -m monitor get_config
```

### Requirements

- Python 3.6+
- OpenCV 3.4+
- Numpy 1.16+

### Installation

```bash
pip3 install work-monitor
```

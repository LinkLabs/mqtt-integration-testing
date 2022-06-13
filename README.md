# MQTT Integration Test Environment

## Required Software

* [Docker Compose](https://docs.docker.com/compose/install/)
* [Python 3.x](https://www.python.org/downloads/)
* [pip](https://pip.pypa.io/en/stable/installation/)

## Starting the MQTT Broker

Simply start the docker-compose file:
```bash
docker-compose up -d
```

### Default MQTT Credentials

This repo is set up with default credentials, which should never be used outside a local environment. For individual
authentication methods, please visit: https://mosquitto.org/documentation/authentication-methods/

The docker-compose utilizes the `config/passwds` file for authentication.

To allow completely open access to the server, the `# allow_anonymous true` line can be uncommented
from the `config/mosquitto.conf` file. However, the default credentials can also be referenced from the
`.env` file in the repo.

## Simulate MQTT Events

### Install Requirements

**Option 1: PIP**

It is highly recommended to create a virtual environment to isolate different python environments. This can be
accomplished with `python3 -m venv venv`

More info on how to activate the environment can be found here: https://docs.python.org/3/library/venv.html

With the virtual environment activated, the requirements can be installed with
`pip install -r requirements.txt`

**Option 2: PipEnv**

PipEnv will automatically create and manage a virtual environment for you.

Installation can be accomplished with the following lines:
```
pip install --user pipenv
pipenv install
```

### Application Usage

The help information can be access with the `-h` or `--help` flags:
```
➜ python3 simulate_events.py -h                                                                                                                                      06/13/22 -  2:26 PM
Loading .env environment variables...
usage: simulate_events.py [-h] [--msg_delay MSG_DELAY] json_data_filename

Publish MQTT Events to MQTT Broker

positional arguments:
  json_data_filename    file name of the json file containing data to publish

optional arguments:
  -h, --help            show this help message and exit
  --msg_delay MSG_DELAY
                        The amount of delay between messages (default: 0)
```

The *json_data* file should be in a format consistent with the [MQTT History API](https://clientedge-conductor.link-labs.com/clientEdge/docs.html#!/airfinderlocation-mqtt-data/getTimeRangeEvents).

### Working Example

There is an example dataset to test with in the repository:

`python3 simulate_events.py test_data.json --msg_delay 1`

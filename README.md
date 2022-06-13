# MQTT Integration Test Environment

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

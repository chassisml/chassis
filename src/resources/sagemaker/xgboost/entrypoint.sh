#!/bin/sh
#
# This shell script serves as the default command for the Docker container and will be executed
# when running the containerized application.
#
# This script should do any initialization needed for the environment (for example activating
# a Python virtual environment) and then start the webserver that provides the model API.
#
# Be sure to use the `exec` command to start the server. This replaces the currently running
# shell with the server command, tying the lifetime of container to the server and allowing
# the server process to receive signals sent to the container.
#
exec gunicorn --config gunicorn.conf.py app:app

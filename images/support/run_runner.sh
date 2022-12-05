#!/bin/bash
# First argment is the directory where the action_runner was set-up

su - builder -c "cd \"$1\" && ./run.sh"

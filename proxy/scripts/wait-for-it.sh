#!/bin/bash

HOST="$1"
PORT="$2"

shift
shift

CMD="$@"

until (echo > /dev/tcp/"$HOST"/"$PORT") &>/dev/null; do
  echo "Waiting KFServing to be ready ..."
  sleep 1;
done

exec $CMD

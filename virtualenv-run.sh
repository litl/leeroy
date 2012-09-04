#!/bin/bash
cd $(dirname $0)
source virtualenv/bin/activate
exec "$@"

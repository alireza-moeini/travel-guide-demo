#!/bin/bash

cd /app

script_name=$1
echo "Executing script: $script_name"
python -m "app.main.scripts.$script_name"

#!/bin/bash

pip install virtualenv
virtualenv chat_env
source chat_env/bin/activate
pip install -r requirements.txt

ip=`ifconfig wlp0s20f3 | grep inet | cut -d: -f2 | awk '{print $2}'`
echo "Your IP is $ip"
python3 server.py -IP=$ip -PORT=5050

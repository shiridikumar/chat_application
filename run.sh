#!/bin/bash

# start two terminal windows and run the following commands in each using tmux

# terminal 1
# run the server 

# cd server
# chmod +x start.sh
# ./start.sh

tmux new-session -d -s server
tmux send-keys -t server 'cd server' C-m
tmux send-keys -t server 'chmod +x start.sh' C-m
tmux send-keys -t server './start.sh' C-m

# terminal 2

# run the client frontend
# npm install
# npm start

tmux new-session -d -s client
tmux send-keys -t client 'cd client/frontend' C-m
tmux send-keys -t client 'npm install' C-m
tmux send-keys -t client 'npm start' C-m

# now you can see the client in the browser at localhost:3000

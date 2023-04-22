# Chat Application on Multiple servers


# directory structure

```
|____client/frontend
|           |____package.json
|           |____src
|                  |____App.js
|                  |____index.js
|                  |____components
|                         |____Chatbox.js 
|                         |____Homescreen.js
|                         |____Signin.js
|                         |____Tiles.js
|
|____server
|      |____db_microscervice.py
|      |____requirements.txt
|      |____server.py
|      |____start.sh
|
|____run.sh
|____stop.sh

```



# requirements
1. python 3.6
2. pip
3. virtualenv
4. nodejs
5. npm
6. tmux
7. ifconfig

# start chat Application


In one teriminal

```
cd server
chmod +x start.sh
./start.sh
```

and in another terminal

```
cd client/frontend
npm install
npm start
```


or
use the following which sets up the server and client in tmux

```
sudo apt install tmux
chmod +x run.sh
./run.sh
```


# stop chat Application

if you used run.sh

```
chmod +x stop.sh
./stop.sh
```
else
just use ctrl+c to stop the server and client

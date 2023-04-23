import * as React from 'react';
import axios, { Axios } from "axios";
import Tiles from './Tiles';
import Chatbox from './Chatbox';
import SendIcon from '@mui/icons-material/Send';
import { useLocation, useNavigate } from 'react-router-dom';
import { io } from "socket.io-client";
import GroupAddIcon from '@mui/icons-material/GroupAdd';
import DeleteForeverIcon from '@mui/icons-material/DeleteForever';
const Homescreen = () => {
    // harcoded for now , need to change it from fetched data
    const tiles = []
    const location = useLocation();
    const server_details = location.state.data;
    const [chats, setcontacts] = React.useState([]);
    const [lastchat, setlastchat] = React.useState([]);
    const [recv, setrecv] = React.useState(false);
    const currcont = React.useRef();
    const currlast = React.useRef();
    const currname = React.useRef();
    const [lastseen, setlastseen] = React.useState("");
    // const [sock,setsocket]=React.useState();
    const initbox = () => {
        return (
            <div>
                <img src={require("../images/chat.png")} style={{ height: "150px", width: "150px" }} />
                <h6>Chat Web</h6>
            </div>
        )
    }
    const sock = React.useRef(0);
    const sock1 = React.useRef(0);
    const currhis = React.useRef();
    const [chatname, setchat] = React.useState("")
    const initChatbox = initbox();
    const [chatbox, setchatbox] = React.useState(initChatbox);
    const [textfield, settext] = React.useState("");
    const [submitted, setsubmitted] = React.useState(false);
    const [dt, setdt] = React.useState("");
    const navigate = useNavigate();
    const HEADER = 64;
    const [chathis, setchats] = React.useState();
    const [chatui, setchatui] = React.useState(initChatbox);
    const [chatclick, setclick] = React.useState(false);
    const [grpid, setgrpid] = React.useState("");
    const currgrp = React.useRef(-1);
    const [addclicked, setaddclicked] = React.useState(false);
    const setadd = React.useRef(0);
    const [addmember, setmember] = React.useState("")
    const currmember = React.useRef("")
    // currgrp.current = -1

    console.log("Connected to server ", server_details.server, "********************************")

    const update_list = (from, last, currchats, currlastchat) => {
        console.log(currchats, currlastchat, "________________")
        let flag = 0;
        let ind = -1;
        for (var i = 0; i < currchats.length; i++) {
            if (currchats[i] == from) {
                flag = 1;
                ind = i;
                break
            }
        }
        const temp = []
        const temp2 = []
        if (flag == 0) {
            temp.push(from);
            temp2.push(last);
        }
        for (var i = 0; i < currchats.length; i++) {
            if (i == ind) {
                temp2.push(last);
                temp.push(currchats[i]);
                break;
            }
        }
        for (var i = 0; i < currchats.length; i++) {
            if (i != ind) {
                temp2.push(currlastchat[i]);
                temp.push(currchats[i]);
            }
        }
        setlastchat(temp2);
        setcontacts(temp);
    }

    React.useEffect(() => {
        setgrpid(grpid);
        currgrp.current = grpid;
    }, [grpid])

    React.useEffect(() => {
        const socket = io(`ws://${server_details.server}`);

        axios.post(`http://${server_details.server}/userdata`, { email: server_details.user }, {
            headers: {

                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,PUT,POST,DELETE,PATCH,OPTIONS',
                'Content-Type': "application/json",
            }

        }).then(response => {
            console.log(response.data);
            setcontacts(response.data.contacts);
            setlastchat(response.data.lastmessage);
            //   response.data["user"]=user
            //   navigate("/home",{state:{data:response.data}})
        })
        sock.current = socket;
        sock.current.emit("connectclient", { "email": server_details.user })
        sock.current.on('message', function (data) {
            console.log(data, "___________________", currcont.current, currlast.current)
            setrecv(!(recv));
            update_list(data["from"], data["msg"], currcont.current, currlast.current);
            if (currname.current == data["from"]) {
                const temp = []
                console.log(currhis.current, "************************")
                for (var i = 0; i < currhis.current.length; i++) {
                    temp.push(currhis.current[i]);
                }
                temp.push(data);
                setchats(temp);
            }
        });

        const socket1 = io(`ws://${"10.1.39.116:8080"}`);
        sock1.current = socket1;
        sock1.current.on("joingrp", function (data) {
            console.log("somehting happend", "?????????????????????????????",data)
            if (data["to"] == server_details.user) {
                const temp = ["group " + data["grpid"]]
                const temp1 = [data["last"]]
                for (var i = 0; i < currcont.current.length; i++) {
                    temp.push(currcont.current[i]);
                }
                for (var i = 0; i < currlast.current.length; i++) {
                    temp1.push(currlast.current[i]);
                }
                setlastchat(temp1);
                setcontacts(temp);
                console.log(data, "*******************", temp1, temp)
            }
            else {
                console.log("somehting happend", "?????????????????????????????",currgrp.current,currname.current)
                let ind = 0;
                for (var i = 0; i < currcont.current.length; i++) {
                    if (currcont[i] == "group " + data["grpid"]) {
                        ind = i;
                        break
                    }
                }
                const temp = ["group " + data["grpid"]]
                const temp1 = [data["last"]]
                for (var i = 0; i < currcont.current.length; i++) {
                    if (i != ind) {
                        temp.push(currcont.current[i]);
                        temp1.push(currlast.current[i]);
                    }
                }
                setlastchat(temp1);
                setcontacts(temp);
            }

            if (currname.current.slice(6,) == data["grpid"]) {
                const temp = [];
                for (var i = 0; i < currhis.current.length; i++) {
                    temp.push(currhis.current[i]);
                }
                temp.push({ "from": data["to"], "msg": data["last"] })
                console.log(temp,"???????????????????")

                setchats(temp);
            }
        });


        sock1.current.on("grpmessage", function (data) {
            console.log("recieved grp message *************",data)
            let ind = 0;
            for (var i = 0; i < currcont.current.length; i++) {
                if (currcont[i] == "group " + data["grpid"]) {
                    ind = i;
                    break
                }
            }
            const temp = ["group " + data["grpid"]]
            const temp1 = [data["msg"]]
            for (var i = 0; i < currcont.current.length; i++) {
                if (i != ind) {
                    temp.push(currcont.current[i]);
                    temp1.push(currlast.current[i]);
                }
            }
            setlastchat(temp1);
            setcontacts(temp);
            if(currgrp.current.slice(6,)==data["grpid"]){
                const temp=[];
                for(var i=0;i<currhis.current.length;i++){
                    temp.push(currhis.current[i]);
                }
                temp.push({"from":data["from"],"msg":data["msg"]})
                setchats(temp);
            }
           
            // }

        });

        sock.current.on('delivered', function (data) {
            console.log(data, "___________________", currcont.current, currlast.current)
            const temp = []
            console.log("deliver tick recieved doole mari", data.from, currname.current, data["chat_ind"], data["chat_ind"].length)
            if (currname.current == data.from) {
                for (var i = 0; i < currhis.current.length; i++) {
                    temp.push(currhis.current[i])
                }

                for (var i = 0; i < data["chat_ind"].length; i++) {
                    temp[data["chat_ind"][i]]["seen"] = 1;
                }
                console.log(temp);
                setchats(temp);
            }
            socket.on('connect_error', err => console.log("Server crashed *********************"))
            socket.on('connect_failed', err => console.log("Server crashed *********************"))
            socket.on('disconnect', err => console.log("Server crashed *********************"))
        })
        currgrp.current = -1;


    }, [])
    console.log(currgrp.current)



    React.useEffect(() => {
        setrecv(recv);
        setlastchat(lastchat);
        setcontacts(chats);
       
        currcont.current = chats
        currlast.current = lastchat
        for(var i=0;i<currcont.current.length;i++){
            console.log("asdasdasdasd","*********************************")
            if(chats[i].slice(0,6)=="group "){
                sock1.current.emit("join", { "grpid": currcont.current[i].slice(6,), "from": server_details.user })
            }
        }
        console.log(chats, lastchat)
    }, [chats, lastchat, recv])





    const chatnameref = React.useRef();


    React.useEffect(() => {
        setchat(chatname);

    }, [chatname])

    React.useEffect(() => {
        setclick(chatclick)
        console.log(chatclick);
        setchat(chatname);
        currname.current = chatname;
        if ("group " == currname.current.slice(0, 6)) {
            const hist = showgrp(currname.current);
            setgrpid(currname.current)
        }
        else {
            if (chatname != "" && chatname) {
                const chat = showchat(chatname);
                setgrpid(-1)
                setchatbox(chat);
            }
        }
    }, [chatclick])

    React.useEffect(() => {
        setgrpid(grpid)
        currgrp.current = grpid;
        console.log("asdasd************************************", currgrp.current)

    }, [grpid])


    React.useEffect(() => {
        if (chatname != "" && chatname) {
            setchats(chathis);
            currhis.current = chathis
            const temp = getchat()
            setchatui(temp);

        }
    }, [chathis])

    React.useEffect(() => {
        setlastseen(lastseen);

    }, [lastseen])


    React.useEffect(() => {
        setchatui(chatui);
        var messageBody = document.getElementById('scrollbar');
        if (messageBody) {
            // console.log(messageBody, "************************************************************")
            messageBody.scrollTop = messageBody.scrollHeight - messageBody.clientHeight;
            // console.log(messageBody.scrollTop, "==============================")
        }



    }, [chatui])




    React.useEffect(() => {
        settext(textfield);
        setdt(textfield);

    }, [textfield])

    React.useEffect(() => {
        setsubmitted(submitted);
        if (textfield != "") {
            var el = document.getElementById("inputtext");
            if (el.value != "") {
                sendchat(textfield);
            }
            // var el = document.getElementById("inputtext");
            el.value = "";
        }
    }, [submitted])



    const sendchat = (msg) => {
        var d = new Date,
            dformat = [d.getMonth() + 1,
            d.getDate(),
            d.getFullYear()].join('/') + ' ' +
                [d.getHours(),
                d.getMinutes(),
                d.getSeconds()].join(':');
        const obj = {
            "from": server_details.user,
            "msg": msg,
            "to": chatname,
            "time": dformat,
            "seen": 0
        }
        if (currname.current.slice(0, 6) == "group ") {
            sock1.current.emit("grpmessage", { "grpid": currgrp.current.slice(6,), "msg": msg, "from": server_details.user })
        }
        else {
            console.log(dformat, "??????????????????");
            const res = sock.current.emit('message', obj)
            const temp = [];
            update_list(obj["to"], obj["msg"], chats, lastchat);
            const temp1 = [];
            if (chathis) {
                for (var i = 0; i < chathis.length; i++) {
                    temp1.push(chathis[i]);
                }
            }
            temp1.push(obj);
            setchats(temp1);
        }

    }


    const showchat = (cha) => {
        console.log(cha, "************")
        axios.post(`http://${server_details.server}/fetchchat`, { chat: cha, user: server_details.user }, {
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,PUT,POST,DELETE,PATCH,OPTIONS',
                'Content-Type': "application/json",
            }

        }).then(response => {
            console.log(response.data, "????????????????????????");
            setchats(response.data["chats"])

            // console.log(response.data["chats"],chathis)
            // const res=socketRef.current.emit('message',{1:2,2:3})
            setlastseen(response.data["lastseen"])

            console.log("ok emitted", response.data["lastseen"], "?????????????????????????");
        })
            .catch(err => {
                console.log(err);
            })
    }

    const showgrp = () => {
        axios.post(`http://${"10.1.39.116:8080"}/fetchgrp`, { grpid: currname.current }, {
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,PUT,POST,DELETE,PATCH,OPTIONS',
                'Content-Type': "application/json",
            }

        }).then(response => {
            sock1.current.emit("join", { "grpid": currgrp.current.slice(6,), "from": server_details.user })
            console.log(response.data, "????????????????????????", currname.current);
            setchats(response.data["history"])
            console.log("ok emitted", "?????????????????????????");
        })
            .catch(err => {
                console.log(err);
            })
    }

    const getchat = () => {
        return (
            <div className="chatblock" style={{ display: "flex", flexDirection: "column", width: "100%", height: "100%", background: "rgb(240,242,245)" }}>
                <Chatbox chats={chathis} name={server_details.user} />
                <div className="enter_text" style={{ background: "rgb(240,242,245)", margin: "20px" }} >
                    <input id="inputtext" placeholder='Enter a new message' className='inputtext' onChange={(e) => { settext(e.target.value) }}></input>
                    <SendIcon onClick={() => { setsubmitted(!(submitted)) }} sx={{ cursor: "pointer", color: "rgb(0, 168, 132);", width: "40px", height: "40px" }} />

                </div>

            </div>
        )
    }



    const handlechatlick = (e) => {

        setchat(e.target.id)
        chatnameref.current = chatname
        const cha = e.target.id;
    }

    const handleGrpCreate = (e) => {
        const ret = sock1.current.emit('join', { "grpid": "", "from": server_details.user })
        console.log(ret);
        const temp = []
    }

    const createTiles = () => {
        // tiles.push(<Tiles name={-1} />)
        for (var i = 0; i < chats.length; i++) {
            tiles.push(
                <div id={chats[i]} className={chats[i] + "_chat"} onClick={(e) => { setchat(e.target.id); setclick(!(chatclick)) }} style={{ cursor: "pointer" }}>
                    <Tiles name={chats[i]} last={lastchat[i]} />
                </div>
            )
        }
        return tiles;
    }

    const addtogroup = () => {
        sock1.current.emit("join", { "grpid": currgrp.current.slice(6,), "from": currmember.current })
        // axios.post(`http://${server_details.server}/addtogrp`, { grpid: currname.current,email:currmember.current }, {
        //     headers: {
        //         'Access-Control-Allow-Origin': '*',
        //         'Access-Control-Allow-Methods': 'GET,PUT,POST,DELETE,PATCH,OPTIONS',
        //         'Content-Type': "application/json",
        //     }

        // }).then(response => {
        //     console.log(response.data, "????????????????????????", currname.current);
        //     setchats(response.data["history"])
        //     console.log("ok emitted", "?????????????????????????");
        // })
        //     .catch(err => {
        //         console.log(err);
        //     })


    }
    React.useEffect(() => {
        setaddclicked(addclicked);
        setadd.current = addclicked;
        if (!(setadd.current) && currmember.current != "") {
            addtogroup();
        }
    }, [addclicked])

    React.useEffect(() => {
        setmember(addmember);
        currmember.current = addmember;
    }, [addmember])

    const handleAddmember = () => {
        setaddclicked(!(addclicked));
    }

    return (
        <div className="homescreen" style={{ height: "100vh", width: "100%", background: "#d1d7db", padding: "0px" }}>
            <div className="topblock" style={{ display: "flex", "flexDirection": "row", alignContent: "center", height: "12%", background: "rgb(0,168,132)" }}>
                <div className='createGroup'>
                    <img src={require("../images/create-group.png")} style={{ width: "60px", borderRadius: "10px", paddingTop: "20px" }} onClick={() => { handleGrpCreate() }} />
                    {/* <img src={require("../images/chat.png")} style={{ height: "150px", width: "150px" }} /> */}

                </div>
                <div className="tilehead" style={{ width: "30%", display: "flex", flexDirection: "column", justifyContent: "center", alignContent: "center", "alignItems": "center" }} >
                    <h6 style={{ color: "white" }}>Logged into {server_details.user}</h6>
                    <div className="emailfield">
                        <input style={{ borderRadius: "5px", height: "30px", "width": "200px" }} placeholder='Enter a mail id' className='inputtext' onChange={(e) => { setchat(e.target.value) }}></input>
                        <SendIcon onClick={() => { setclick(!(chatclick)) }} sx={{ cursor: "pointer", color: "white", width: "40px", height: "40px" }} />
                    </div>
                    <h6 style={{ color: "white" }}>Start Conversation</h6>

                </div>
                <div className="chatname" style={{ width: "100%", background: "rgb(0,168,132)" }}>
                    <h6 style={{ fontSize: "20px", marginRight: "30px" }}>{chatname}</h6>
                    {lastseen && lastseen != "" && (
                        <h6>Last seen : {lastseen}</h6>
                    )
                    }
                </div>
                {currgrp.current != -1 && currgrp.current && (

                    <div className="grpoptions" style={{ padding: "20px" }}>
                        {addclicked && (
                            <div className="addmem">
                                <input style={{ borderRadius: "5px", height: "30px", "width": "200px" }} placeholder='Enter a mail id' className='inputtext' onChange={(e) => { setmember(e.target.value) }}></input>
                            </div>
                        )
                        }
                        <div className="grpadd">
                            <GroupAddIcon fontSize='large' color='white' style={{ color: "white", height: "50px", width: "50px", marginRight: "10px", cursor: "pointer" }} onClick={() => { handleAddmember() }} />
                        </div>
                        <div className="exit">
                            <DeleteForeverIcon fontSize='large' color='white' style={{ color: "white", height: "50px", width: "50px", cursor: "pointer" }} />
                        </div>
                    </div>
                )}
            </div>

            <div className="cont" style={{ height: "88%", margin: 0, display: "flex", flexDirection: "row", background: "white", pading: "0px", justifyContent: "center", width: "100%", padding: 0 }}>

                <div className="card" style={{ "width": "30%" }}>
                    <ul className="list-group list-group-flush">
                        {createTiles()}
                    </ul>
                </div>
                <div className="chatbox" style={{ width: "100%", "height": "100%", display: "flex", flexDirection: "column", "alignItems": "center", justifyContent: "center" }}>
                    {chatui}
                </div>

            </div>
        </div >
    )
}
export default Homescreen
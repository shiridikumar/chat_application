import * as React from 'react';
import axios, { Axios } from "axios";
import Tiles from './Tiles';
import Chatbox from './Chatbox';
import SendIcon from '@mui/icons-material/Send';
import { useLocation, useNavigate } from 'react-router-dom';
import { io } from "socket.io-client";
const Homescreen = () => {
    // harcoded for now , need to change it from fetched data
    const chats = ["Shiridi", "akanksha", "zyz", "narayana", "kumar", "kiran", "mukund"]
    const lastchat = ["Hi ra ela unnav", "wow amazing", "ok", "whats up", "super", "ok", "tc bye"]
    const tiles = []
    const location = useLocation();
    const server_details = location.state.data;
    const socket = io(`ws://10.1.39.116:5000`);
    const socketRef = React.useRef();
    socketRef.current = socket;
    const chatnameref = React.useRef();
    const initbox = () => {
        return (
            <div>
                <img src={require("../images/chat.png")} style={{ height: "150px", width: "150px" }} />
                <h6>Chat Web</h6>
            </div>
        )
    }
    const initChatbox = initbox();

    const [chatname, setchat] = React.useState("")
    const [chatbox, setchatbox] = React.useState(initChatbox);
    const [textfield, settext] = React.useState("");
    const [submitted, setsubmitted] = React.useState(false);
    const [dt, setdt] = React.useState("");
    const navigate = useNavigate();
    const HEADER = 64;
    const [chathis, setchats] = React.useState();
    const [chatui, setchatui] = React.useState(initChatbox);

    socket.on('message', function (data) {
        console.log(data, "___________________")
    });

    React.useEffect(() => {
        setchat(chatname);
        if (chatname != "" && chatname) {
            const chat = showchat(chatname);
            setchatbox(chat);
        }
    }, [chatname])

    React.useEffect(() => {
        if (chatname != "" && chatname) {
            setchats(chathis);
            const temp = getchat()
            setchatui(temp);
        }

    }, [chathis])



    React.useEffect(() => {
        settext(textfield);
        setdt(textfield);
    }, [textfield])

    React.useEffect(() => {
        setsubmitted(submitted);
        if (textfield != "") {
            sendchat(textfield);
        }

    }, [submitted])



    const sendchat = (msg) => {
        const obj = {
            "from": server_details.user,
            "msg": msg,
            "to": chatname
        }
        const res = socketRef.current.emit('message', obj)
        const temp = [];
        if (chathis) {
            for (var i = 0; i < chathis.length; i++) {
                temp.push(chathis[i]);
            }
        }
        temp.push(obj);
        setchats(temp);


    }

    // const send_msg = (id, msg) => {
    //     let m = { "_id": id, "msg": msg }
    //     m["from"] = String(server_details.user["_id"]);
    //     let data = JSON.stringify(m);
    //     let message = new TextEncoder("utf-8").encode(data);
    //     // let message = bytes(data,encoding="utf-8")
    //     let leng = message.length
    //     leng = new TextEncoder("utf-8").encode(leng);
    //     let space = new Uint8Array(HEADER - leng.length).fill(32);
    //     let result = new Uint8Array(leng.length + space.length);
    //     result.set(leng);
    //     result.set(space, leng.length);
    //     leng = result;
    //     socket.emit(leng);
    //     socket.emit(message);
    // }




    const showchat = (cha) => {

        axios.post(`http://${server_details.server}/fetchchat`, { chat: cha, user: server_details.user }, {
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,PUT,POST,DELETE,PATCH,OPTIONS',
                'Content-Type': "application/json",
            }

        }).then(response => {
            console.log(response.data,"????????????????????????");
            setchats(response.data["chats"])

            // console.log(response.data["chats"],chathis)
            // const res=socketRef.current.emit('message',{1:2,2:3})

            console.log("ok emitted");
        })
            .catch(err => {
                console.log(err);
            })


    }

    const getchat = () => {
        return (
            <div className="chatblock" style={{ display: "flex", flexDirection: "column", width: "100%", height: "100%", background: "rgb(240,242,245)" }}>
                <Chatbox chats={chathis} name={chatname} />
                <div className="enter_text" style={{ background: "rgb(240,242,245)", margin: "20px" }} >
                    <input placeholder='Enter a new message' className='inputtext' onChange={(e) => { settext(e.target.value) }}></input>
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

    const createTiles = () => {
        // tiles.push(<Tiles name={-1} />)
        for (var i = 0; i < chats.length; i++) {
            tiles.push(
                <div id={chats[i]} className={chats[i] + "_chat"} onClick={(e) => { setchat(e.target.id) }} style={{ cursor: "pointer" }}>
                    <Tiles name={chats[i]} last={lastchat[i]} />
                </div>
            )
        }
        return tiles;
    }
    return (
        <div className="homescreen" style={{ height: "100vh", width: "100%", background: "#d1d7db", paddingTop: "50px", paddingBottom: "50px", paddingLeft: "100px", paddingRight: "100px" }}>
            <div className="topblock" style={{ display: "flex", "flexDirection": "row", alignContent: "center", height: "50px", background: "rgb(0,168,132)" }}>
                <div className="tilehead" style={{ width: "30%" }}>
                    <Tiles name={-1} />
                </div>
                <div className="chatname" style={{ width: "100%", background: "rgb(0,168,132)" }}>
                    <h6 style={{ fontSize: "20px" }}>{chatname}</h6>
                </div>

            </div>


            <div className="cont" style={{ height: "100%", margin: 0, display: "flex", flexDirection: "row", background: "white", pading: "0px", justifyContent: "center", width: "100%", padding: 0 }}>

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
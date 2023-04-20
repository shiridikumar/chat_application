import * as React from 'react';
import axios, { Axios } from "axios";
import Tiles from './Tiles';
import Chatbox from './Chatbox';
import SendIcon from '@mui/icons-material/Send';
import { useLocation, useNavigate } from 'react-router-dom';
import { io } from "socket.io-client";
const Homescreen = () => {
    // harcoded for now , need to change it from fetched data
    const tiles = []
    const location = useLocation();
    const server_details = location.state.data;
    const [chats, setcontacts] = React.useState([]);
    const [lastchat, setlastchat] = React.useState([]);
    // const [sock,setsocket]=React.useState();
    const sock = React.useRef(0);

    const update_list = (from, last, currchats, currlastchat) => {
        console.log(currchats, currlastchat, "________________")
        let flag = 0;
        let ind =-1;
        for (var i = 0; i < currchats.length; i++) {
            if (currchats[i] == from) {
                flag = 1;
                ind =i;
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
            if(i==ind){
                temp2.push(last);
                temp.push(currchats[i]);
                break;
            }
        }
        for(var i=0;i<currchats.length;i++){
            if(i!=ind){
                temp2.push(currlastchat[i]);
                temp.push(currchats[i]);
            }
        }
        console.log("updating ra wolfa **************")
        setlastchat(temp2);
        setcontacts(temp);
    }



    React.useEffect(() => {
        const socket = io(`ws://${server_details.server}`);

        axios.post(`http://${server_details.server}/userdata`, {email:server_details.user}, {
            headers: {
      
              'Access-Control-Allow-Origin': '*',
              'Access-Control-Allow-Methods': 'GET,PUT,POST,DELETE,PATCH,OPTIONS',
              'Content-Type': "application/json",
            }
      
            }).then(response=>{
              console.log(response.data);
              setcontacts(response.data.contacts);
              setlastchat(response.data.lastmessage);
            //   response.data["user"]=user
            //   navigate("/home",{state:{data:response.data}})
            })

        socket.on('message', function (data) {
            console.log(data, "___________________")
            update_list(data["from"], data["msg"]);

        });
        sock.current = socket;
    }, [])

    React.useEffect(() => {
        // setsocket(sock);
        setlastchat(lastchat);
        setcontacts(chats);
    }, [chats, lastchat])


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
    const [chatclick, setclick] = React.useState(false);



    React.useEffect(() => {
        setchat(chatname);
    }, [chatname])

    React.useEffect(() => {
        setclick(chatclick)
        console.log(chatclick);
        setchat(chatname);
        if (chatname != "" && chatname) {
            const chat = showchat(chatname);
            setchatbox(chat);
        }
    }, [chatclick])

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
        
        if (textfield != "") {
            setsubmitted(submitted);
            sendchat(textfield);
            var el=document.getElementById("inputtext");
            el.value="";
            settext("");
        }
        
    }, [submitted])



    const sendchat = (msg) => {
        const obj = {
            "from": server_details.user,
            "msg": msg,
            "to": chatname
        }
        // console.log(sock);
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

            console.log("ok emitted");
        })
            .catch(err => {
                console.log(err);
            })
    }

    const getchat = () => {
        const handleKeyDown = event => {
            console.log('User pressed: ', event.key);
        
            if (event.key === 'Enter') {
              // 👇️ your logic here
              console.log('Enter key pressed ✅');
              setsubmitted(!(submitted))
            }
          };
        return (
            <div className="chatblock" style={{ display: "flex", flexDirection: "column", width: "100%", height: "100%", background: "rgb(240,242,245)" }}>
                <Chatbox chats={chathis} name={chatname} />
                <div className="enter_text" style={{ background: "rgb(240,242,245)", margin: "20px" }} onKeyDown={handleKeyDown}>
                    <input id ="inputtext" placeholder='Enter a new message' className='inputtext' onChange={(e) => { settext(e.target.value) }}></input>
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
                <div id={chats[i]} className={chats[i] + "_chat"} onClick={(e) => { setchat(e.target.id); setclick(!(chatclick)) }} style={{ cursor: "pointer" }}>
                    <Tiles name={chats[i]} last={lastchat[i]} />
                </div>
            )
        }
        return tiles;
    }
    const handleKeyDown = event => {
        console.log('User pressed: ', event.key);
    
        if (event.key === 'Enter') {
          // 👇️ your logic here
          console.log('Enter key pressed ✅');
          setclick(!(chatclick))
        }
      };
    return (
        <div className="homescreen" style={{ height: "100vh", width: "100%", background: "#d1d7db", padding:"0px" }}>
            <div className="topblock" style={{ display: "flex", "flexDirection": "row", alignContent: "center", height: "12%", background: "rgb(0,168,132)" }}>
                <div className="tilehead" style={{ width: "30%", display: "flex", flexDirection: "column", justifyContent: "center", alignContent: "center", "alignItems": "center" }} >
                    <div className="emailfield" onKeyDown={handleKeyDown} >
                        <input style={{ borderRadius: "5px", height: "30px", "width": "200px" }} placeholder='Enter a mail id' className='inputtext' onChange={(e) => { setchat(e.target.value) }}></input>
                        <SendIcon onClick={() => { setclick(!(chatclick)) }} sx={{ cursor: "pointer", color: "white", width: "40px", height: "40px" }} />
                    </div>
                    <h6 style={{ color: "white" }}>Start Conversation</h6>
                </div>
                <div className="chatname" style={{ width: "100%", background: "rgb(0,168,132)" }}>
                    <h6 style={{ fontSize: "20px" }}>{chatname}</h6>
                </div>
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
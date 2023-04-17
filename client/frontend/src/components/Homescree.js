import * as React from 'react';
import axios, { Axios } from "axios";
import Tiles from './Tiles';
import Chatbox from './Chatbox';
import SendIcon from '@mui/icons-material/Send';
const Homescreen = () => {
    // harcoded for now , need to change it from fetched data
    const chats = ["Shiridi", "akanksha", "zyz", "narayana", "kumar", "kiran", "mukund"]
    const lastchat = ["Hi ra ela unnav", "wow amazing", "ok", "whats up", "super", "ok", "tc bye"]
    const tiles = []
    const initbox = () => {
        return (
            <div>
                <img src={require("../images/chat.png")} style={{ height: "150px", width: "150px" }} />
                <h6>Chat Web</h6>


            </div>
        )

    }
    const initChatbox = initbox();
    // const [clickedchat, setchatbox] = React.useState(false)
    const [chat, setchat] = React.useState("")
    const [chatbox, setchatbox] = React.useState(initChatbox);

    const showchat = (cha) => {
        /*
        demo example of chat storage         */

        const a = [{
            "from": "xyz",
            "to": "Shiridi",
            "msg": "hi how are you , is eveyrthing fine"
        },
        {
            "from": "xyz",
            "to": "Shiridi",
            "msg": "chaala rojulu ayyindi neetho matladi"
        },
        {
            "from": "Shiridi",
            "to": "xyz",
            "msg": "yah im fine , what about you"
        },
        {
            "from": "Shiridi",
            "to": "xyz",
            "msg": "something"
        },
        {
            "from": "Shiridi",
            "to": "xyz",
            "msg": "dasara blockbuster telusa"
        },
        {
            "from": "xyz",
            "to": "Shiridi",
            "msg": "yah kinda meeda oopu nani  anna thopu :)"
        },
        {
            "from": "xyz",
            "to": "Shiridi",
            "msg": "ok bye"
        }
        ]
        return (
            <div className="chatblock" style={{display:"flex",flexDirection:"column" , width:"100%",height:"100%",background:"rgb(240,242,245)" }}>
                <Chatbox chats={a} name={cha} />
                <div className="enter_text" style={{background:"rgb(240,242,245)" , margin:"20px"}} >
                    <input placeholder='Enter a new message' className='inputtext'></input>
                    <SendIcon sx={{cursor:"pointer",color:"rgb(0, 168, 132);", width:"40px", height:"40px"}}/>
                
                </div>

            </div>
        )


    }
    const handlechatlick = (e) => {
        setchat(e.target.id)
        const cha = e.target.id;
        const chat = showchat(cha);
        setchatbox(chat);




    }

    const createTiles = () => {
        // tiles.push(<Tiles name={-1} />)
        for (var i = 0; i < chats.length; i++) {
            tiles.push(
                <div id={chats[i]} className={chats[i] + "_chat"} onClick={(e) => { handlechatlick(e) }} style={{ cursor: "pointer" }}>
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
                    <h6 style={{ fontSize: "20px" }}>{chat}</h6>
                </div>

            </div>


            <div className="cont" style={{ height: "100%", margin: 0, display: "flex", flexDirection: "row", background: "white", pading: "0px", justifyContent: "center", width: "100%", padding: 0 }}>

                <div className="card" style={{ "width": "30%" }}>
                    <ul className="list-group list-group-flush">
                        {createTiles()}
                    </ul>
                </div>
                <div className="chatbox" style={{ width: "100%", "height": "100%", display: "flex", flexDirection: "column", "alignItems": "center", justifyContent: "center" }}>
                    {chatbox}
                </div>

            </div>
        </div >


    )
}
export default Homescreen
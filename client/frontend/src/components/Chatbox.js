import * as React from 'react';
import axios, { Axios } from "axios";
// import image from  "../images/bg.webp" 
import "../components.css"
import Messagebox from './Messagebox';

const Chatbox = (props) => {
    const row = []
    let chats = props.chats
    if (!(props.chats)) {
        chats = [];
    }
    console.log(props.chats);
    const loadmessages = () => {
        for (var i = 0; i < chats.length; i++) {
            var align = "row-reverse"
            if (chats[i].from == props.name) {
                align = "row"
            }
            console.log(chats[i].from, props.name)
            row.push(
                <Messagebox align={align} text={chats[i].msg} time={chats[i].time} seen={chats[i].seen}/>
            )
        }
        return row;
    }
    React.useEffect(() => {
        var messageBody = document.getElementById('scrollbar');
        // console.log(messageBody, "************************************************************")
        messageBody.scrollTop = messageBody.scrollHeight - messageBody.clientHeight;



    }, [])

    return (
        <div className="chats" id="scrollbar" style={{ overflowY: "scroll", width: "100%", height: "100%", display: "block" }}>
            {loadmessages()}
        </div>
    )
}


export default Chatbox
import * as React from 'react';
import axios, { Axios } from "axios";
// import image from  "../images/bg.webp" 
import "../components.css"
import Messagebox from './Messagebox';

const Chatbox = (props) => {
    const row = []
    const loadmessages = () => {
        for (var i = 0; i < props.chats.length; i++) {
            var align = "row-reverse"
            if (props.chats[i].from == props.name) {
                align = "row"

            }
            console.log(props.chats[i].from,props.name)
            row.push(
                <Messagebox align={align} text={props.chats[i].msg} />
            )
        }
        return row;
    }

    return (
        <div className="chats" style={{ width: "100%", height: "100%" }}>
            {loadmessages()}
        </div>

    )
}


export default Chatbox
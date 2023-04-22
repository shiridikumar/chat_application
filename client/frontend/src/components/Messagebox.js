import * as React from 'react';
import axios, { Axios } from "axios";
// import image from  "../images/bg.webp" 
import "../components.css"
const Messagebox = (props) => {
    return (
        <div className="msgcard" style={{ width: "100%", display: "flex", flexDirection: props.align ,marginBottom:"5px"}}>
            <div className="message" style={{display:"flex",flexDirection:"column",alignItems:"flex-start"}}>
                <div className="msgtile"  style={{ display: "flex", flexDirection: "row", alignContent: "center", alignItems: "center" }}>
                    <p className='messagetexts'>{props.text}</p>
                    {props.align == "row-reverse" && (
                        <img src={require('../images/single.png')} style={{ height: "18px", width: "18px", marginLeft: "20px" }} />
                    )
                    }
                </div>
                <p style={{ margin: 0, fontSize: "12px", color: "grey" }}>{props.time}</p>
            </div>

        </div>
    )
}


export default Messagebox;
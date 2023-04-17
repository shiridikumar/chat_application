import * as React from 'react';
import axios, { Axios } from "axios";
// import image from  "../images/bg.webp" 
import "../components.css"

const Messagebox = (props) => {
    return (
        <div className="msgcard" style={{width:"100%" , display:"flex",flexDirection:props.align}}>
            <div className="message"  >
                <p className='messagetexts'>{props.text}</p>
            </div>

        </div>


    )
}


export default Messagebox;
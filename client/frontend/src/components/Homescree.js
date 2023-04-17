import * as React from 'react';
import axios, { Axios } from "axios";
import Tiles from './Tiles';
const Homescreen = () => {
    // harcoded for now , need to change it from fetched data
    const chats = ["Shiridi", "akanksha", "zyz", "narayana", "kumar", "kiran", "mukund"]
    const lastchat = ["Hi ra ela unnav", "wow amazing", "ok", "whats up", "super", "ok", "tc bye"]
    const tiles = []
    
    const createTiles = () => {
        tiles.push(<Tiles name={-1} />)
        for (var i = 0; i < chats.length; i++) {
            tiles.push(
                <div className="tile" onClick={() => { console.log("clicked") }}>
                    <Tiles name={chats[i]} last={lastchat[i]} />
                </div>
            )
        }
        return tiles;
    }
    return (
        <div className="homescreen" style={{ height: "100vh", width: "100%", background: "#d1d7db", padding: "50px" }}>


            <div className="container" style={{ height: "100%", margin: 0, display: "flex", flexDirection: "row", background: "white", pading: "0px", justifyContent: "center", width: "100%", padding: 0 }}>

                <div className="card" style={{ "width": "25rem" }}>
                    <ul className="list-group list-group-flush">
                        {createTiles()}
                    </ul>
                </div>
                <div className="chatbot" style={{ width: "100%", "height": "100%", display: "flex", flexDirection: "column", "alignItems": "center", justifyContent: "center" }}>
                    <img src={require("../images/chat.png")} style={{ height: "150px", width: "150px" }} />
                    <h6>Chat Web</h6>

                </div>

            </div>
        </div >


    )
}
export default Homescreen
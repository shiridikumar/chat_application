import * as React from 'react';
import axios, { Axios } from "axios";
import Avatar from '@mui/material/Avatar';

const Tiles = (props) => {
    return (
        <div style={{pointerEvents:"none"}} className="cont">
            {props.name == -1 &&
                (
                    <li className="list-group-item" style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "center", background: "rgb(0,168,132)" }}>
                        <Avatar src="../images/img.jpg" />
                        <div className="button" style={{ color: "white", margin: "5px", cursor: "pointer" }}>
                            Logout
                        </div>
                    </li>

                )
            }
            {
                props.name != -1 &&
                (
                    <li className="list-group-item" style={{ display: "flex", flexDirection: "row", alignItems: "center" ,pointerEvents:"none"}}>
                        <Avatar style={{pointerEvents:"none"}} src="../images/img.jpg" />
                        <div id={props.name + "_chat"} className="tile" style={{ display: "flex", "flexDirection": "column", alignItems: "flex-start", justifyContent: "center", marginLeft: "20px" }}>
                            <h6   >{props.name}</h6>
                            <p style={{ margin: 0 }}>{props.last}</p>


                        </div>
                    </li>
                )

            }
        </div>

    )
}


export default Tiles
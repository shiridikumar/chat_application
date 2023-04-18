var express = require("express");
var router = express.Router();
const ws=new WebSocket.Server({}) 

router.post("/test",(req,res)=>{
    console.log(req.body["key"]);

})


module.exports=router
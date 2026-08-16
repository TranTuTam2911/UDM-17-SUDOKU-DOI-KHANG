const http = require("http");
const fs = require("fs")
const path = require("path")
const Websocket = require("ws")
const sever = http.createServer((req,res) => {
  let filePath = "";

  if(req.url === "/") {
    filePath = "./index.html";
  } else {
    filePath = "." +req.url;
  }

const ext = path.extname(filePath)

const contentTypes = {
  ".html": "text/html",
  ".css": "text/css",
  ".js"

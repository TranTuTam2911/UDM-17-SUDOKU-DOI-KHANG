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
  ".js":"text/javascript"
};
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404);
      res.end("Not Found");
      return;
    }
    res.writeHead(200, {
      "content-Type": contentTypes[ext]
    });
    res.end(data);
  });
});
const wss = new WebSoket.Sever({
  sever
});
const rooms = {};
const players = {};
wss.on("conection",(player) => {
  console.log("Đã có người tham gia");
  player.on("message", (message) => {
    const data = JSON.parse(message);
    if (data.type === "Đăng Nhập") {
      players[data.playerId] = {
        playerId: data.playerId,
        playerName: data.playerName,
        player: player
      };
      console.log("Người chơi đã đăng nhập:", data.playerId);
    } else if (data.type === "Tạo Phòng") {
      const roomId = data.roomId;
      rooms[roomId] = {
        roomId: data.roomId,
        players: []
      };
      console.log("Phòng đã được tạo:", data.roomId);
    }
  });
});

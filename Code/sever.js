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
      socket.playerId = data.playerId;
      sockeet.send(JSON.stringify({
        type: "Đăng Nhập Thành Công",
        playerId: data.playerId,
        playerName: data.playerName
      }));
      console.log("Người chơi đã đăng nhập:", data.playerId);
sendRoomList();
    }
     if (data.type === "Tạo Phòng") {
      const roomId = Math.floor(Math.random() * 10000).toString();
      rooms[roomId] = {
        roomId: roomId,
        players: [data.playerId]
      };
      status = "Đang Chờ";
      console.log("Phòng đã được tạo:", roomId);
      sendRoomList();

    }
    if (data.type === "Tham Gia Phòng") {
      const roomId = data.roomId;
      if (rooms[roomId]) {
        rooms[roomId].players.push(data.playerId);
        console.log("Người chơi đã tham gia phòng:", roomId);
        sendRoomList();
      }
    }
    if(!rooms[data.roomId]) {
      player.send(JSON.stringify({
        type: "Phòng Không Tồn Tại"
      }));
      return;
    }
    if (rooms[data.roomId].players.length === 2) {
      rooms[data.roomId].status = "Đang chơi";
      console.log("Phòng đã bắt đầu:", data.roomId);
      sendRoomList();
    }
    return;
    rooms[data.roomId].players.forEach((playerId) => {
  });
});
sendRoomList();
      room.players.forEach(playerId => {
      const player =
      players[playerId];
        if (player) {
      player.socket.send(
        JSON.stringify({
      type: "Cập nhật Phòng",
      roomId: room.id,
      players: room.players,
      status: room.status
           })
         );
       }
   });
  });
  socket.on("close", () => {
  console.log(
  "Người chơi đã rời khỏi"
        );
    });
function sendRoomList() {
    const roomList =
        Object.values(rooms).map(room => ({
            id: room.id,
            players:
                room.players.length,
            status:
                room.status
        }));
    const message =
        JSON.stringify({
            type: "Cập nhật Phòng",
            rooms: roomList
        });
    Object.values(players).forEach(player => {
        if (
            player.socket.readyState ===
            WebSocket.OPEN
        ) {
            player.socket.send(message);
        }
    });
}
 server.listen(8080, () => {
 console.log(
  "Server chạy tại ....."
    );

});

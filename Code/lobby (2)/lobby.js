const username = localStorage.getItem("username");
if (username) {
    document.getElementById("username").innerText = username;
}
function createRoom() {
    window.location.href = "create-room.html";
}
function joinRoom(roomId) {
    localStorage.setItem("roomId", roomId);
    window.location.href = "room.html";
}
function refreshRooms() {
    alert("Đã làm mới danh sách phòng!");
}
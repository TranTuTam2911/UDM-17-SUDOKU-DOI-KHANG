function goBack() {
    window.location.href = "lobby.html";
}
function createRoom() {
    const roomName = document
        .getElementById("roomName")
        .value
        .trim();
    if (roomName === "") {
        alert("Vui lòng nhập tên phòng!");
        return;
    }
    const roomId =
        Math.floor(100 + Math.random() * 900);
    localStorage.setItem(
        "roomName",
        roomName
    );
    localStorage.setItem(
        "roomId",
        roomId
    );
    window.location.href = "room.html";
}
var ws = new WebSocket("ws://localhost:8888/chat");

ws.onopen = function() {};

ws.onmessage = function (evt) {
    var message = JSON.parse(evt.data)
    var messages = document.getElementById("messages");
    messages.innerHTML = "<p>" +
	"<strong>" + message.name + ": </strong>" +
	" <small>" + message.when + "</small> " +
	message.message + 
	"</p>" + messages.innerHTML;
};

function sendData() {
    var m = {"name": document.getElementById("namebox").value,
	     "message": document.getElementById("messagebox").value}; 
    ws.send(JSON.stringify(m));
}

document.getElementById("messagebox").addEventListener("keyup", function(event) {
    event.preventDefault();
    if (event.keyCode == 13) {
        document.getElementById("submitbutton").click();
	document.getElementById("messagebox").value = "";
    }
});

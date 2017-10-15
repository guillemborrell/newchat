var ws = new WebSocket("ws://localhost:8888/chat");
var cursor = -1;

function prepend_messages(message) {
    var messages = document.getElementById("messages");
    messages.innerHTML = "<p>" +
	"<strong>" + message.name + ": </strong>" +
	" <small>" + message.when + "</small>| " +
	message.message + 
	"</p>" + messages.innerHTML;
}

function append_messages(message) {
    var messages = document.getElementById("messages");
    messages.innerHTML = messages.innerHTML + "<p>" +
	"<strong>" + message.name + ": </strong>" +
	" <small>" + message.when + "</small>| " +
	message.message + 
	"</p>";    
}


ws.onopen = function() {};

ws.onmessage = function (evt) {
    var message = JSON.parse(evt.data)
    prepend_messages(message);
};

function sendData() {
    var m = {"name": document.getElementById("namebox").value,
	     "message": document.getElementById("messagebox").value,
	     "chat": document.getElementById("chatbox").value}; 
    ws.send(JSON.stringify(m));
}

function moreMessages(chat, from) {
    if (from == 1) {
	return
    }
    else {
	// Cursor has not been used.
	if (cursor < 0) {
	    url = "/old?from=" + from + "&chat=" + chat;
	    $.getJSON(url, function (data) {
		for (var i in data.messages) {
		    append_messages(data.messages[i]);
		}
		cursor = data.last;
	    })
	}
	// Cursor has been used, so button pressed already.
	else {
	    url = "/old?from=" + cursor + "&chat=" + chat;
	    $.getJSON(url, function (data) {
		for (var i in data.messages) {
		    append_messages(data.messages[i]);
		}
		cursor = data.last;
	    })
	}
    }
}

document.getElementById("messagebox").addEventListener("keyup", function(event) {
    event.preventDefault();
    if (event.keyCode == 13) {
        document.getElementById("submitbutton").click();
	document.getElementById("messagebox").value = "";
    }
});

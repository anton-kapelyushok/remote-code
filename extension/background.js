var socket = new WebSocket("ws:/127.0.0.1:8765");

socket.onmessage = function(event) {
	var self = this;
	var parts = event.data.split(" ");
	var number = +parts[0];
	console.log(number);
	chrome.tabs.query( {index: number}, function (tabs) {
		console.log(tabs[0]);
		var id = tabs[0].id;
		var cmd = parts.splice(1).join(" ");
		chrome.tabs.executeScript(id, {code: cmd}, function(results) { 
			console.log(cmd + " : " + results); 
		});
	});
};
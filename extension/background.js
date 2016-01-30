var socket = new WebSocket("ws:/127.0.0.1:8765/ext");

var handle_input = function(request) {
	chrome.tabs.query( {index: request.tab_index}, function (tabs) {
		var id = tabs[0].id;
		execute_command_on_tab(id, request.command);
	});
};

var handle_vk = function(request) {
	chrome.tabs.query({ url: "https://vk.com/audios*"}, function (tabs) {
		var id = tabs[0].id;
		var cmd = "";
		switch (request.command) {
			case "next":
				cmd = "if (audioPlayer.id) { audioPlayer.nextTrack(); } else { headPlayPause(); }"
			break;
			case "playPause":
				cmd = "headPlayPause();"
			break;
			case "prev":
				cmd = "if (audioPlayer.id) { audioPlayer.prevTrack(); } else { headPlayPause(); }"
			break;
		}
		execute_command_on_tab(id, cmd);
	});
};

var execute_command_on_tab = function(tabId, command) {
	cmd = "var script = document.createElement('script');script.innerHTML = '" + command + "';document.querySelector('head').appendChild(script);document.querySelector('head').removeChild(script);"
	chrome.tabs.executeScript(tabId, {code: cmd}, function(results) {
		string_results = JSON.stringify(results);
		console.log("Results: " + string_results);
		socket.send(string_results);
	});
};

socket.onmessage = function(event) {
	console.log("Received from server: " + event.data);
	var request = JSON.parse(event.data);

	switch(request.action) {
		case "input":
			handle_input(request);
		break;

		case "vk":
			handle_vk(request);
		break;
	}
};
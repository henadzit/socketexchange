"use strict";

var socketex = function() {
    var socketex = {};
    var config = {
    };
    var socket;
    var input;

    // public
    socketex.init = function(serverUrl, inputSelector) {
        config.serverUrl = serverUrl;
        config.inputSelector = inputSelector;

        onLoad();
    };

    // private
    function onLoad() {
        socket = io.connect(config.serverUrl);

        input = document.querySelector(config.inputSelector);

        if (!input) {
            console.error("Incorrect input selector");
            return;
        }

        input.onchange = onChange;

        socket.emit('init', {})
    }

    function onChange(e) {
        console.log("change event");
        socket.emit("change", {});
    }

    return socketex;
}();
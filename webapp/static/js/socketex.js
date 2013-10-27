"use strict";

var socketex = function() {
    var socketex = {};
    var config = {
        timeout: 2000
    };
    var socket;
    var input;
    var conflictElement;
    // a timeout before sending changed data to the server
    var onChangeTimeoutId;
    // contains last value received from the server
    var valueFromServer;

    // public
    socketex.init = function(options) {
        config.serverUrl = options.serverUrl;
        config.slug = options.slug;
        config.inputSelector = options.inputSelector;
        config.conflictElementSelector = options.conflictElementSelector;

        onLoad();
    };

    // private
    function onLoad() {
        socket = io.connect(config.serverUrl, {query: 'slug=' + config.slug});

        input = document.querySelector(config.inputSelector);
        conflictElement = document.querySelector(config.conflictElementSelector);

        if (!input) {
            console.error("Incorrect input selector");
            return;
        }

        socket.on('change', onServerChangeEvent);
        // send a get packet to let the server know that the server should send a change response containing
        // last data
        socket.emit('get');

        input.onkeyup = onInputChange;
    }

    function onInputChange(e) {
        console.log("input change event");

        if (isUpdatePending()) {
            clearTimeout(onChangeTimeoutId);
        }

        onChangeTimeoutId = setTimeout(emitChange, config.timeout);
    }

    function onServerChangeEvent(pkt) {
        valueFromServer = pkt.content;

        if (!isUpdatePending()) {
            input.value = valueFromServer;
        }
        else {
            conflictElement.style.display = 'block';
        }
    }

    function emitChange() {
        socket.emit("change", input.value);
        onChangeTimeoutId = null;
    }

    function isUpdatePending() {
        return !!onChangeTimeoutId;
    }



    return socketex;
}();
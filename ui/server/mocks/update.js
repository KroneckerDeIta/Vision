/*jshint node:true*/
module.exports = function(app) {
    var WebSocketServer = require('ws').Server;

    if (process["updateSocketServer"]) {
        process["updateSocketServer"].close();
        process["updateSocketServer"] = undefined;
    }

    process["updateSocketServer"] = new WebSocketServer({port: 13434, path: "/update"});

    sendMessage = function(message, websocket=undefined) {
        if (websocket) {
            websocket.send(message);
        } else {
            for (var i = 0; i < app["websocketConnections"].length; i++) {
                var ws = app["websocketConnections"][i]["websocket"];
                ws.send(message);
            }
        }
    }

    sendScoreUpdateToUser = function(username, id, score) {
        for (var i = 0; i < app["websocketConnections"].length; i++) {
            var connection = app["websocketConnections"][i];
            if (connection["username"] === username) {
                sendMessage(JSON.stringify({
                    "type": "scoreUpdate",
                    "scoreUpdate": {
                        "id": id,
                        "score": score
                    }
                }), connection["websocket"]);
            }
        }
    };

    sendResults = function(entryIds, websocket=undefined) {
        var results = JSON.stringify(getResults(entryIds));
        sendMessage(results, websocket);
    };

    sendAllResults = function(websocket=undefined) {
        entryIds = [];
        for (var i = 0; i < app["defaultEntries"].length; i++) {
            entryIds.push(app["defaultEntries"][i]["id"]);
        }
        sendResults(entryIds, websocket);
    };

    closeConnectionsForUsername = function(username) {
        // Loop backwards as we will be removing connections.
        for (var i = app["websocketConnections"].length - 1; i >=0; i--) {
            var connection = app["websocketConnections"][i];
            if (connection["username"] && connection["username"] === username) {
                app["websocketConnections"][i]["websocket"].close(1000, "Session Expired");
                app["websocketConnections"].splice(i, 1);
            }
        }
    };

    getResults = function(entryIds) {
        // First of all construct the results structure using the default entries.
        var results = {};
        for (var index in entryIds) {
            var entryId = entryIds[index];
            var resultsEntry = {};
            for (var score = -1; score < 11; score++) {
                resultsEntry[score.toString()] = 0;
            }
            results[entryId] = resultsEntry;
        }

        // Now to get the results from all the users' entries.
        for (var username in app["users"]) {
            for (var j = 0; j < app["users"][username]["entries"].length; j++) {
                var userEntry = app["users"][username]["entries"][j];
                var userId = userEntry["id"];
                var userScore = userEntry["attributes"]["score"];
                if (results[userId]) {
                    results[userId][userScore] += 1;
                }
            }
        }

        return {
            "type" : "results",
            "results" : results
        };
    };

    handleClientMessage = function(ws, message) {
        var messageJson = JSON.parse(message);

        if (messageJson["type"] === "refresh_token") {
            handleRefreshToken(ws, messageJson["refresh_token"]);
        } else {
            throw "Websocket type not recognised.";
        }
    };

    handleRefreshToken = function(ws, refreshToken) {
        var username = app['getUsernameFromRefreshToken'](refreshToken);

        for (var i = 0; i < app["websocketConnections"].length; i++) {
            var connection = app["websocketConnections"][i];
            if (connection["websocket"] === ws) {
                connection["username"] = username;
                break;
            }
        }

        var refreshExpiry = app["users"][username]["refresh_token_expiry"];
        var accessExpiry = app["users"][username]['access_token_expiry'];
        var currentTime = (new Date()).getTime();
        if (currentTime > accessExpiry || currentTime > refreshExpiry) {
            closeConnectionsForUsername(username)
            app['resetUserTokens'](username);
        } else {
            const expiry = Math.max(accessExpiry, currentTime + app["accessTokenExtensionTime"]);
            app["users"][username]['access_token_expiry'] = expiry;
            ws.send(JSON.stringify({
                "type": "access_token_expiry",
                "access_token_expiry": (expiry - currentTime)
            }));
        }
    };

    process["updateSocketServer"].on('connection', function(ws) {
        var newWebsocketConnection = {
            "websocket": ws
        };

        app["websocketConnections"].push(newWebsocketConnection);

        sendAllResults(ws);

        ws.on('close', function() {
            var connectionIndex;
            for (var i = 0; i < app["websocketConnections"].length; i++) {
                var connection = app["websocketConnections"][i];
                if (connection["websocket"] === ws) {
                    connectionIndex = i;
                    break;
                }
            }
            app["websocketConnections"].splice(connectionIndex, 1);
        });

        ws.on('message', function(message) {
            handleClientMessage(ws, message);
        });
    });
};

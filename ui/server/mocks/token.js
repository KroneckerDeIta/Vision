/*jshint node:true*/
module.exports = function(app) {
    var express = require('express');
    var bodyParser = require('body-parser');

    var tokenRouter = express.Router();

    getCurrentTimeMilliseconds = function() {
        return (new Date()).getTime();
    };

    doesUserExist = function(username) {
        return username in app["users"];
    };

    normalizeUsername = function(username) {
        return username.toLowerCase();
    };

    updateNumberOfUsersInAttributes = function() {
        numberOfUsers = Object.keys(app["users"]).length;

        for (var username in app["users"]) {
            var entries = app["users"][username]["entries"];
            for (var i = 0; i < entries.length; i++) {
                entries[i]['attributes']['number'] = numberOfUsers;
            }
        }
    };

    addUser = function(username, password) {
        app["addUser"](username, password);
        updateTokens(username);
        updateNumberOfUsersInAttributes();
    };

    checkPassword = function(username, password) {
        return app["users"][username]['password'] === password;
    };

    updateTokens = function(username) {
        var currentTime = getCurrentTimeMilliseconds();

        // The access token would usually be a UUID.
        app["users"][username]['access_token'] = username;
        app["users"][username]['access_token_expiry'] = currentTime + app["accessTokenExtensionTime"];
        // The refresh token would usually be a UUID.
        app["users"][username]['refresh_token'] = username;
        app["users"][username]['refresh_token_expiry'] = currentTime + app["refreshTokenExtenstionTime"];
        // Set the default entries for the user if they don't have any values set.
    }

    getAuthenticedJson = function(username) {
        var currentTime = getCurrentTimeMilliseconds();
        var userExpiryTime = app["users"][username]['access_token_expiry'];
        var accessTokenExpirySeconds = (userExpiryTime - currentTime);

        var tokenJson = {
            "access_token": app["users"][username]['access_token'],
            "access_token_expiry": accessTokenExpirySeconds,
            "refresh_token": app["users"][username]['refresh_token'],
            "username": username
        };
        return JSON.stringify(tokenJson);
    };

    tokenRouter.post('/token', function(req, res) {
        var username = normalizeUsername(req.body.username);
        var password = req.body.password;
        if (req.body.grant_type === 'password') {
            if ( doesUserExist(username) ) {
                if ( checkPassword(username, password) ) {
                    updateTokens(username);
                    res.status(200).send(getAuthenticedJson(username));
                } else {
                    res.status(400).send('Username/Password incorrect.');
                }
            } else {
                res.status(400).send('User does not exist, please register.');
            }
        } else {
            res.status(400).send('Bad request');
        }
    });

    tokenRouter.post('/register', function(req, res) {
        var username = normalizeUsername(req.body.username);
        var password = req.body.password;

        if (req.body.grant_type === 'password') {
            if ( doesUserExist(username) ) {
                res.status(400).send('"User already exists.');
            } else {
                addUser(username, password);
                // The access token is just the username in this mock.
                res.status(200).send(getAuthenticedJson(username));
            }
        } else {
            res.status(400).send('Bad request');
        }
    });


    // Needed the following to get it to send form data through.
    app.use(bodyParser.json());
    app.use(bodyParser.urlencoded({ extended: true }));
    app.use('/api', tokenRouter);
};

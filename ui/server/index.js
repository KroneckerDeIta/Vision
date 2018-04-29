/* eslint-env node */
'use strict';

module.exports = function(app) {
    app["users"] = {};
    app["websocketConnections"] = [];
    // Set access token to expire in 5 minutes.
    app["accessTokenExtensionTime"] = 1000 * 60 * 5;
    // Set refresh token to expire in 30 minutes.
    app["refreshTokenExtenstionTime"] = 1000 * 60 * 30;

    app["defaultEntries"] = [
        {
            "id" : "1",
            "type" : "entries",
            "attributes" : {
                "country": "Great Britain",
                "icon": "gb",
                "image": "/images/entryImages/Joe-and-Jake.jpg",
                "telephone": "(+44)8005360001",
                "link": "http://www.eurovision.tv/page/history/by-country/country?country=6",
                "score": -1,
                "order": 1,
                "number": 0,
            }
        },
        {
            "id" : "2",
            "type" : "entries",
            "attributes" : {
                "country": "France",
                "icon": "fr",
                "image": "/images/entryImages/074renaudcorlou.jpg",
                "telephone": "(+44)8005360002",
                "link": "http://www.eurovision.tv/page/history/by-country/country?country=2",
                "score": -1,
                "order": 3,
                "number": 0,
            }
        },
        {
            "id" : "3",
            "type" : "entries",
            "attributes" : {
                "country": "Greece",
                "icon": "gr",
                "image": "/images/entryImages/argo_greece_utopian_land_1.jpg",
                "telephone": "(+44)8005360003",
                "link": "http://www.eurovision.tv/page/history/by-country/country?country=19",
                "score": -1,
                "order": 2,
                "number": 0
            }
        }
    ];

    app["defaultSettings"] = [
        {
            "id" : "1",
            "type" : "settings",
            "attributes" : {
                "setting": "theme",
                "value": "ocean"
            }
        }
    ];

    app["addUser"] = function(username, password) {
        if (username in app["users"]) {
            throw "User with username already exists."
        }

        app["users"][username] = JSON.parse(JSON.stringify({
            "password": password,
            "access_token": null,
            "access_token_expiry": null,
            "refresh_token": null,
            "refresh_token_expiry": null,
            "entries": app["defaultEntries"],
            "settings": app["defaultSettings"]
        }));
    };

    // Setup default user.
    app["addUser"]("letme", "in");

    app['getUsernameFromBearer'] = function(req) {
        if (req.headers.authorization) {
            var bearer = req.headers.authorization.replace("Bearer ", "");

            for (var username in app["users"]) {
                if (app["users"][username]["access_token"] === bearer) {
                    return username;
                }
            }
        }
        return null;
    };

    app['getUsernameFromAccessToken'] = function(accessToken) {
        for (var username in app["users"]) {
            if (app["users"][username]["access_token"] === accessToken) {
                return username;
            }
        }
        return null;
    };

    app['getUsernameFromRefreshToken'] = function(refreshToken) {
        for (var username in app["users"]) {
            if (app["users"][username]["refresh_token"] === refreshToken) {
                return username;
            }
        }
        return null;
    };

    app['resetUserTokens'] = function(username) {
        app["users"][username]["access_token"] = null;
        app["users"][username]["access_token_expiry"] = null;
        app["users"][username]["refresh_token"] = null;
        app["users"][username]["refresh_token_expiry"] = null;
    };

    var globSync   = require('glob').sync;
    var mocks      = globSync('./mocks/**/*.js', { cwd: __dirname }).map(require);
    var proxies    = globSync('./proxies/**/*.js', { cwd: __dirname }).map(require);

    // Log proxy requests
    var morgan  = require('morgan');
    app.use(morgan('dev'));

    mocks.forEach(function(route) { route(app); });
    proxies.forEach(function(route) { route(app); });
};

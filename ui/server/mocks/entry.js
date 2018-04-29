/*jshint node:true*/
module.exports = function(app) {
    var express = require('express');
    var entryRouter = express.Router();

    getAllEntries = function(username) {
        return {"data": app["users"][username]["entries"]};
    };

    sendEntry = function(username, req, res) {
        const id = req.params.id;
        const entries = app["users"][username]["entries"];

        for (let i = 0; i < entries.length; i++) {
            const entry = entries[i];
            if (id === entry["id"]) {
                res.send({"data": entry});
                return;
            }
        }

        res.sendStatus(404);
    };

    updateEntry = function(username, req) {
        let entryToUpdate;
        const data = req.body;
        const id = req.params.id;

        const updateType = data["update"];
        if (updateType === "score") {
            const score = data["score"];

            for (let i = 0; i < app["users"][username]["entries"].length; i++) {
                entry = app["users"][username]["entries"][i];
                if (entry['id'] === id) {
                    entryToUpdate = entry;
                    entryToUpdate['attributes']['score'] = score;
                    sendScoreUpdateToUser(username, id, score);
                    sendResults(id);
                    return;
                }
            }

            throw "Not Found";
        } else {
            throw "Unknown update type";
        }
    }

    entryRouter.get('/entries', function(req, res) {
        var username = app['getUsernameFromBearer'](req);
        if (!username) {
            res.status(401).send('Authentication required.');
            return;
        }

        var delay = 500;
        setTimeout(function() {
            res.send(getAllEntries(username));
        }, delay);
    });

    entryRouter.get('/entries/:id', function(req, res) {
        var username = app['getUsernameFromBearer'](req);
        if (!username) {
            res.status(401).send('Authentication required.');
            return;
        }

        var delay = 500;
        setTimeout(function() {
            sendEntry(username, req, res);
        }, delay);
    });

    entryRouter.patch('/entries/:id', function(req, res) {
        var username = app['getUsernameFromBearer'](req);
        if (!username) {
            res.status(401).send('Authentication required.');
            return;
        }
        
        try {
            const entry = updateEntry(username, req);

            var delay = 500;
            setTimeout(function() {
                res.sendStatus(200);
            }, delay);
        } catch (err) {
            if (err === "Not Found") {
                res.sendStatus(404);
            } else {
                res.status(500).send(err);
            }
        }
    });

    app.use('/api', require('body-parser').json({ type: 'application/json' }), entryRouter);
};

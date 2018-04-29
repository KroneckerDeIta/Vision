/*jshint node:true*/
module.exports = function(app) {
    var express = require('express');
    var settingRouter = express.Router();

    getAllSettings = function(username) {
        return {"data": app["users"][username]["settings"]};
    };

    settingRouter.get('/settings', function(req, res) {
        var username = app['getUsernameFromBearer'](req);
        if (!username) {
            res.status(401).send('Authentication required.');
            return;
        }

        var delay = 500;
        setTimeout(function() {
            res.send(getAllSettings(username));
        }, delay);
    });

    app.use('/api', require('body-parser').json({ type: 'application/*+json' }), settingRouter);
};

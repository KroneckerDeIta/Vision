import { cancel, later } from '@ember/runloop';
import Service, { inject as service } from '@ember/service';
import config from '../config/environment';

export default Service.extend({
    authenticationService: service('authentication'),
    session: service(),
    store: service(),
    websockets: service(),
    socket: undefined,
    refreshTokenRunLaterMethod: undefined,
    updateResultsRunLaterMethod: undefined,
    reconnecting: false,

    init() {
        this._super(...arguments);
        this.setupSocket();
    },

    setupSocket() {
        if (this.get('session.isAuthenticated')) {
            if (!this.get('socket')) {
                let socket;
                if (config.environment === 'development') {
                    socket = this.get('websockets').socketFor(
                        // The mock server requires a different port number for the websocket.
                        "ws://" + window.location.hostname + ":13434/update");
                } else {
                    socket = this.get('websockets').socketFor(
                        "ws://" + window.location.host + "/update");
                }
                this.set('socket', socket);
                this.setupHandlers();
            } else if (this.get('socket').readyState() === this.get('socket.socket.CLOSED')) {
                this.get('socket').reconnect();
                this.setupHandlers();
            }
        }
    },

    willDestroy() {
        this._super(...arguments);
        this.destroySocket();
    },

    destroySocket() {
        if (this.get('socket')) {
            this.get('socket').off('open', this.openHandler);
            this.get('socket').off('message', this.messageHandler);
            this.get('socket').off('close', this.closeHandler);
            this.get('socket').close();
        }
    },

    openHandler() {
        this.set('reconnecting', false);
        this.sendRefreshToken();
    },

    setupHandlers() {
        this.get('socket').on('open', this.openHandler, this);
        this.get('socket').on('message', this.messageHandler, this);
        this.get('socket').on('close', this.closeHandler, this);
    },

    sendMessage(message) {
        if (this.get('session.isAuthenticated')) {
            // Add the access token and username to the message, as the server will check if they
            // are valid.
            message["access_token"] = this.get('session.data.authenticated.access_token')
            message["username"] = this.get('session.data.authenticated.username')
            this.get('socket').send(JSON.stringify(message));
        }
    },

    messageHandler(event) {
        if (this.get('session').get('isAuthenticated')) {
            const data = JSON.parse(event.data);

            if (data["type"] === "results") {
                this.resultsMessage(data);
            } else if (data["type"] === "scoreUpdate") {
                this.scoreUpdate(data);
            } else if (data["type"] === "access_token_expiry") {
                this.sendRefreshToken(data["access_token_expiry"]);
            }
        }
    },

    closeHandler(event) {
        if (!this.get('reconnecting')) {
            this.set('reconnecting', true);
            this.get('socket').reconnect();
        } else {
            this.set('reconnecting', false);
            let warningTitle = "Connection Lost";
            let warningMessage = "Connection to the server has been lost, please login later.";
            if (event.reason === "Session Expired") {
                warningTitle = "Session Expired";
                warningMessage = "Please login again.";
            }
            this.cancelSendRefreshToken();
            this.get('authenticationService').logoutWithWarning(warningTitle, warningMessage);
        }
    },

    updateEntries(data) {
        for (let id in data["results"]) {
            const entryResults = data["results"][id];
            const entry = this.get('store').peekRecord('entry', id);

            if (!entry) {
                this.get('store').findRecord('entry', id).then((entry) => {
                    entry.setResults(entryResults);
                });
            } else {
                entry.setResults(entryResults);
            }
        }
    },

    resultsMessage(data) {
        this.updateEntries(data);
    },

    scoreUpdate(data) {
        const entry = this.get('store').peekRecord('entry', data["scoreUpdate"]["id"]);
        entry.set('score', data["scoreUpdate"]["score"]);
    },

    cancelSendRefreshToken() {
        const refreshTokenRunLaterMethod = this.get('refreshTokenRunLaterMethod');
        if(refreshTokenRunLaterMethod) {
            cancel(refreshTokenRunLaterMethod);
            this.set('refreshTokenRunLaterMethod', undefined);
        }
    },

    sendRefreshToken(sendRefreshTokenTimeout=undefined) {
        this.cancelSendRefreshToken();

        let timeout = 0;
        if (sendRefreshTokenTimeout) {
            // Subtract 10 seconds for leeway before the access token expires. But only send the
            // refresh token at most every 10 seconds.
            timeout = Math.max(sendRefreshTokenTimeout - 10000, 10000);
        }

        const refreshTokenRunLaterMethod = later(() => {
            this.cancelSendRefreshToken();
            this.sendMessage({
                "type": "refresh_token",
                "refresh_token": this.get('session.data.authenticated.refresh_token')
            });
        }, timeout);

        this.set('refreshTokenRunLaterMethod', refreshTokenRunLaterMethod);
    }
});

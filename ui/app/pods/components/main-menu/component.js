import { inject as service } from '@ember/service';
import Component from '@ember/component';

export default Component.extend({
    authenticationService: service('authentication'),
    routing: service('-routing'),
    session: service('session'),
    sideMenu: service(),
    updateService: service('update'),
    indexMenu: "false",

    classNames: ["main-menu"],

    indexMenuBoolean: function() {
        return this.get('indexMenu') === "true";
    }.property('indexMenu'),

    actions: {
        logout() {
            this.get('authenticationService').logout();
        },

        closeMenu() {
            this.get("sideMenu").close();
        },

        navigateToEntries() {
            this.send('closeMenu');
            this.get('routing').transitionTo('routes.entries');
        },

        navigateToSettings() {
            this.send('closeMenu');
            this.get('routing').transitionTo('routes.settings');
        }
    }
});

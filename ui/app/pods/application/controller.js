import { cancel, later } from '@ember/runloop';
import { inject as service } from '@ember/service';
import Controller from '@ember/controller';

export default Controller.extend({
    authenticationService: service('authentication'),
    routing: service('-routing'),
    session: service('session'), // Needed in template.
    updateService: service('update'),
    settings: undefined,
    runLaterMethod: undefined,

    isAuthenitcatedObserver: function() {
        // If the session is over this might have been because the user logged out or the
        // session was ended in a different tab, which is covered here.
        if(!this.get('session.isAuthenticated')) {
            this.get('authenticationService').logout();
        } else {
            // If there is a problem getting the setting the user will be logged out.
            this.set('settings', this.store.findAll('setting'));
        }
    }.observes('session.isAuthenticated').on('init'),

    cancelRunLaterMethod() {
        const runLaterMethod = this.get('runLaterMethod');
        if(runLaterMethod) {
            cancel(runLaterMethod);
            this.set('runLaterMethod', undefined);
        }
    },

    isLoading: function() {
        const isIndexAndAuthenticated = this.get('isIndexAndAuthenticated');
        const isIndex = this.get('routing').get('currentRouteName') === "index";
        const isAuthenticated = this.get('session.isAuthenticated');
        return (!isIndexAndAuthenticated) && isIndex && isAuthenticated;
    }.property('isIndexAndAuthenticated', 'routing.currentRouteName', 'session.isAuthenticated'),

    isIndexAndAuthenticatedObserver: function() {
        this.cancelRunLaterMethod();

        let isIndex = this.get('routing').get('currentRouteName') === "index";
        let isAuthenticated = this.get('session.isAuthenticated');

        if (isIndex && isAuthenticated) {
            const runLaterMethod = later(() => {
                this.cancelRunLaterMethod();

                isIndex = this.get('routing').get('currentRouteName') === "index";
                isAuthenticated = this.get('session.isAuthenticated');
                this.set('isIndexAndAuthenticated', isIndex && isAuthenticated);
            }, 1000);

            this.set('runLaterMethod', runLaterMethod);
        } else {
            this.set('isIndexAndAuthenticated', false);
        }
    }.observes('routing.currentRouteName', 'session.isAuthenticated').on('init')
});

import { later } from '@ember/runloop';
import Service, { inject as service } from '@ember/service';

export default Service.extend({
    routing: service('-routing'),
    session: service('session'),
    store: service(),
    sideMenu: service(),
    updateService: service('update'),
    showModalService: service('show-modal'),

    showModalLaterTimeout: 500,

    login(type, identification, password, onSuccess, onError) {
        this.get('session').authenticate('authenticator:' + type, identification, password).then(
            () => {
                onSuccess();
            }
        ).catch(
            (reason) => {
                onError(reason);
            }
        );
    },

    logoutWithWarning(warningTitle, warningMessage) {
        this.logout();
        later(() => {
            this.get('showModalService').showInformationModal(warningTitle, warningMessage);
        }, this.get('showModalLaterTimeout'));
    },

    logout() {
        if (this.get('session.isAuthenticated')) {
            this.get('session').invalidate();
        }
        this.get('updateService').willDestroy();
        this.get("sideMenu").close();

        // Clear the store.

        this.get('store').unloadAll('entry');
        this.get('store').unloadAll('setting');

        later(() => {
            const currentRoute = this.get('routing').get('currentRouteName');
            if (currentRoute !== "index") {
                this.get('routing').transitionTo('index');
            }
        });
    }
});

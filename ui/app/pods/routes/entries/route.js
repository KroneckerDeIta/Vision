import { hash } from 'rsvp';
import { inject as service } from '@ember/service';
import Route from '@ember/routing/route';
import AuthenticatedRouteMixin from 'ember-simple-auth/mixins/authenticated-route-mixin';

export default Route.extend(AuthenticatedRouteMixin, {
    session: service('session'),
    updateService: service('update'),

    beforeModel() {
        if (!this.get('session').get('isAuthenticated')) {
            this.transitionTo('index');
        }
    },

    model() {
        return hash({
            entries: this.store.findAll('entry'),
            settings: this.store.findAll('setting')
        });
    },

    setupController(controller, models) {
        controller.set('entries', models.entries);
        controller.set('settings', models.setting);
    },

    activateSocket: function() {
        this.get('updateService').setupSocket();
    }.on('activate')
});

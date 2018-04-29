import { inject as service } from '@ember/service';
import Route from '@ember/routing/route';
import AuthenticatedRouteMixin from 'ember-simple-auth/mixins/authenticated-route-mixin';

export default Route.extend(AuthenticatedRouteMixin, {
    session: service('session'),

    beforeModel() {
        if (!this.get('session').get('isAuthenticated')) {
            this.transitionTo('index');
        }
    },

    model() {
        return this.store.findAll('setting');
    },
});

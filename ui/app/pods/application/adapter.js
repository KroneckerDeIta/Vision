import Ember from 'ember';
import DS from 'ember-data';
import DataAdapterMixin from 'ember-simple-auth/mixins/data-adapter-mixin';

export default DS.JSONAPIAdapter.extend(DataAdapterMixin, {
    namespace: window.serverNamespace,
    authorizer: 'authorizer:oauth2'
});

var inflector = Ember.Inflector.inflector;
inflector.irregular('entry', 'entries');

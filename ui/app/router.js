import EmberRouter from '@ember/routing/router';
import config from './config/environment';

const Router = EmberRouter.extend({
  location: config.locationType,
  rootURL: config.rootURL
});

Router.map(function() {
  this.route('routes', function() {
    this.route('entries');
    this.route('settings');
  });
  this.route('not-found', { path: '/*path' });  // capture route in path
});

export default Router;

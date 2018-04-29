import { inject as service } from '@ember/service';
import Route from '@ember/routing/route';

export default Route.extend({
    authenticationService: service('authentication'),

    actions: {
        error: function(err) {
            if (err["errors"] && err["errors"][0] && err["errors"][0]["status"] &&
                err["errors"][0]["status"] === "401") {
                const errorMessage = err["errors"][0]["detail"];
                this.get('authenticationService').logoutWithWarning("Authentication Error", errorMessage);
            } else {
                // Unexpected error, rethrow.
                throw err;
            }
        }
    }
});

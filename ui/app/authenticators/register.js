import Registration from 'ember-simple-auth-registration/authenticators/oauth2-password-registration';

export default Registration.extend({
    registrationEndpoint: '/api/register'
});

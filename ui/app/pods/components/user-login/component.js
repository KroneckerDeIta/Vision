import { computed } from '@ember/object';
import { inject as service } from '@ember/service';
import Component from '@ember/component';

export default Component.extend({
    authenticationService: service('authentication'),
    classNames: ["login-box"],
    routing: service('-routing'),
    session: service('session'),
    updateService: service('update'),
    loginType: 'Login',
    identification: undefined,
    password: undefined,
    confirmPassword: undefined,
    errorMessage: undefined,

    isRegister: computed('loginType', function() {
        return (this.get('loginType') === 'Register');
    }),
    isLogin: computed('loginType', function() {
        return (this.get('loginType') === 'Login');
    }),

    isInputValid: function() {
        let isError = false;
        let errorMessage = "";

        if (this.get('identification') === undefined) {
            isError = true;
            errorMessage = "You must set a username.";
        } else if (this.get('password') === undefined) {
            isError = true;
            errorMessage = "You must set a password.";
        } else if (this.get('isRegister') && this.get('password') !== this.get('confirmPassword')) {
            isError = true;
            errorMessage = "Password and confirmation password are different.";
        }

        return {isError: isError, errorMessage: errorMessage};
    },

    onSuccess: function() {
        this.get('routing').transitionTo("routes.entries");
        this.get('updateService').setupSocket();
    },

    onError: function(errorMessage) {
        this.set('errorMessage', errorMessage);
    },

    actions: {
        authenticate() {
            // Hide the soft keyboard when the user clicks enter.
            document.activeElement.blur();

            let validationCheck = this.isInputValid();
            if (validationCheck.isError) {
                this.set('errorMessage', validationCheck.errorMessage);
                return;
            }

            const authenticateType = this.get('isRegister') ? "register" : "oauth2";
            const { identification, password } = this.getProperties('identification', 'password');
            this.get('authenticationService').login(authenticateType, identification, password,
                                                    this.onSuccess.bind(this),
                                                    this.onError.bind(this));
        },

        login() {
            this.set('errorMessage', undefined);
            this.set("loginType", "Login");
        },

        register() {
            this.set('errorMessage', undefined);
            this.set("loginType", "Register");
        }
    }
});

import Controller from '@ember/controller';

export default Controller.extend({
    actions: {
        navigateToEntries() {
            this.transitionToRoute('routes.entries');
        },
    }
});

import Component from '@ember/component';

export default Component.extend({
    classNames: ['entry-container'],

    actions: {
        selectScore(score) {
            this.get('entry').updateScore(score);
        },

        switchExpanded() {
            this.set('entry.expanded', !this.get('entry.expanded'));
        },

        stopPropagation(event) {
            event.stopPropagation();
        }
    }
});

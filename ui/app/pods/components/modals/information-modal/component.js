import $ from 'jquery';
import { inject as service } from '@ember/service';
import Component from '@ember/component';

export default Component.extend({
    showModalService: service('show-modal'),
    title: undefined,
    message: undefined,
    
    setup: function() {
        this.get('showModalService').on(this.get('showModalService').get('SHOW_INFORMATION_MODAL'),
                                        this, this.setupModal);
    } .on('init'),
    
    setupModal(title, message) {
        this.set('title', title);
        this.set('message', message);
        $("#information-modal-id").modal('show');
    }
});

import Evented from '@ember/object/evented';
import Service from '@ember/service';

export default Service.extend(Evented, {
    SHOW_INFORMATION_MODAL: 'showInformationModal',
    
    showInformationModal: function(title, message) {
        this.trigger(this.get('SHOW_INFORMATION_MODAL'), title, message);
    }
});

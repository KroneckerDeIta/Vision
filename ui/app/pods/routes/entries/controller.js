import { computed } from '@ember/object';
import { sort } from '@ember/object/computed';
import Controller from '@ember/controller';

export default Controller.extend({
    sortedEntries: sort('entries', 'sortEntriesDefinition'),
    selectedSort: 'Order',
    sortTypeRange: ['Order', 'Total: Low to High', 'Total: High to Low', 'Average: Low to High',
        'Average: High to Low'],
    sortEntriesDefinition: computed('sortType', function() {
        return [this.get('sortType')];
    }),

    sortType: computed('selectedSort', function() {
        const selected = this.get('selectedSort');
        const sortTypeRange = this.get('sortTypeRange');
        if (selected === sortTypeRange[0]) {
            return 'order:asc';
        } else if (selected === sortTypeRange[1]) {
            return 'total:asc';
        } else if (selected === sortTypeRange[2]) {
            return 'total:desc';
        } else if (selected === sortTypeRange[3]) {
            return 'mean:asc';
        } else if (selected === sortTypeRange[4]) {
            return 'mean:desc';
        } else {
            throw "Unknown entry sorting type.";
        }
    }),

    actions: {
        selectEntrySorting(sortChoice) {
            this.set('selectedSort', sortChoice);
        }
    }
});

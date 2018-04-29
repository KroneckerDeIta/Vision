import { A } from '@ember/array';
import { observer, computed } from '@ember/object';
import { inject as service } from '@ember/service';
import DS from 'ember-data';

export default DS.Model.extend({
    session: service('session'),

    country: DS.attr('string'),
    icon: DS.attr('string'),
    image: DS.attr('string'),
    telephone: DS.attr('string'),
    link: DS.attr('string'),
    score: DS.attr('number'),
    order: DS.attr('number'),

    /**
     * Save method has been disabled.
     */
    save() {
        Ember.Logger.error("Saving an entry model is not allowed.");
    },

    /**
     * Update the score for the entry.
     * 
     * @param {*Number} score The new score.
     */
    updateScore(score) {
        // Convert to a number if a string.
        const newScore = Number(score);
        Ember.$.ajax({
            url: window.entriesEndpoint + '/' + this.get('id'),
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + this.get('session.data.authenticated.access_token')
            },
            type: 'PATCH',
            data: JSON.stringify({
                'update': 'score',
                'score': newScore
            }),
            success: () => {
                this.set('score', newScore);
            }
        });
    },

    // The results array that will be updated every few seconds from the server using a websocket.
    results: undefined,

    // Variables used for summary information.
    displayResults: false,
    total: undefined,
    mean: undefined,
    numberOfDecimals: 2,

    // Variables used for the chart.
    chartType: 'bar',
    chartData: undefined,
    chartOptions: undefined,

    // The range of values that can be the score for the entry.
    // TODO This should come from the server.
    // TODO All settings should come from an endpoint on the server.
    range: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],

    // True if we are showing all the information about a country, false otherwise.
    expanded: false,

    resultsObserver: observer('results.@each', function() {
        this.updateInformation();
    }),

    totalObserver: observer('total', function() {
        const totalLength = this.numberToLength(this.get('total'));
        this.set('totalClass', this.getValueClassUsingLength(totalLength));
    }),

    meanObserver: observer('mean', function() {
        const meanLength = this.numberToLength(this.get('mean'));
        this.set('meanClass', this.getValueClassUsingLength(meanLength));
    }),

    orderClass: computed('order', function() {
        const orderLength = this.numberToLength(this.get('order'));
        return this.getValueClassUsingLength(orderLength);
    }),

    telephoneClass: computed('telephone', function() {
        const telephoneLength = this.get('telephone').length;
        return this.getValueClassUsingLength(telephoneLength);
    }),

    setResults: function(results) {
        this.set('results', results);
    },

    updateInformation: function() {
        let totalScore = 0;
        let totalUsers = 0;

        // Variables for the chart.
        let labels = A();
        let data = A();

        const results = this.get('results');
        for (let score in results) {
            const numberScore = Number(score);
            const numberNumUsers = Number(results[score]);

            if (numberScore > -1) {
                totalScore += numberScore * numberNumUsers;
                totalUsers += numberNumUsers;

                labels.pushObject(numberScore);
                data.pushObject(numberNumUsers);
            }
        }

        if (totalUsers > 0) {
            const mean = totalScore / totalUsers;
            this.set('total', parseFloat(totalScore.toFixed(this.get('numberOfDecimals'))));
            this.set('mean', parseFloat(mean.toFixed(this.get('numberOfDecimals'))));
            this.constructChart(labels, data);
            this.set('displayResults', true);
        } else {
            this.set('displayResults', false);
        }
    },

    constructChart: function(labels, data, options) {
        const chartData = {
            "labels": labels,
            "datasets": [{
                "data": data,
                "backgroundColor": "white",
                "label": 'Number of selections',
            }]
        };

        let chartOptions = options;
        if (!chartOptions) {
            chartOptions = {
                "responsive": true,
                "animation": {
                    "duration": 0
                },
                "maintainAspectRatio": false,
                "legend": {
                    "display": false
                },
                "tooltips": {
                    "enabled": false
                },
                "scales": {
                    xAxes: [{
                        "ticks": {
                            "fontColor": "white",
                            callback: function(value) {if (value % 1 === 0) {return value;}},
                            maxRotation: 0,
                            minRotation: 0
                        },
                        "scaleLabel": {
                            "fontColor": "white",
                            display: true,
                            labelString: 'Score'
                        }
                    }],
                    yAxes: [{
                        "ticks": {
                            "fontColor": "white",
                            callback: function(value) {if (value % 1 === 0) {return value;}}
                        },
                        "scaleLabel": {
                            "fontColor": "white",
                            display: true,
                            labelString: 'Number of votes'
                        }
                    }]
                }
            };
        }

        this.set('chartData', chartData);
        this.set('chartOptions', chartOptions);
    },

    getValueClassUsingLength: function(valueLength) {
        if (valueLength < 5) {
            return "entry-header-column-value-body";
        } else if (valueLength < 8) {
            return "entry-header-column-value-medium";
        } else if (valueLength < 11) {
            return "entry-header-column-value-footer";
        } else {
            return "entry-header-column-value-small";
        }
    },

    numberToLength: function(number) {
        return number.toString().length;
    },
});

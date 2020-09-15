odoo.define('es_core.service.SoundService', function (require) {
"use strict";

var AbstractService = require('web.AbstractService');
var core = require('web.core');
var session = require('web.session');


var SoundService =  AbstractService.extend({
    dependencies: [],

    start: function () {
        this._super.apply(this, arguments);

        this.beep_alert = new Audio(session.url("/es_core/static/audio/ting.mp3"));
        this.beep_tips = new Audio(session.url("/es_core/static/audio/ting.mp3"));
        this.beep_concurrency = new Audio(session.url("/es_core/static/audio/ting.mp3"));
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------
    play_alert_beep: function(){
        this.beep_alert.pause();
        this.beep_alert.play();
    },

    play_tips_beep: function(){
        //this.beep_tips.pause();
        //this.beep_tips.play();
    },

    play_concurrency_beep: function(){
        //this.beep_concurrency.pause();
        //this.beep_concurrency.play();
    }
});

core.serviceRegistry.add('sound_service', SoundService);

return SoundService;

});

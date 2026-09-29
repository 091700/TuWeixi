window.StartModel = cc.Class({

    ctor: function(){
        this.state = 'HaventStarted';
    },
    onStartPressed: function(){
        this.state = 'started';
    }
})
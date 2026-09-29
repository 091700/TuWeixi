window.StartController = cc.Class({
    extends: cc.Component,
    properties: {
        StartBtn:{
            default: null,
            type: cc.Button
        },
    },

    onLoad: function(){
        this.model = new StartModel();
        this.StartBtn.node.on('click', this.onStartBtnClick, this);
    },

    onStartBtnClick: function(){
        this.model.onStartPressed();
        window.EventBus.emit('startGame');
    }
})
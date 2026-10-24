window.StartController = cc.Class({
    extends: cc.Component,
    properties: {
        StartBtn:{
            default: null,
            type: cc.Button
        },
    },

    onLoad: function(){
        window.BGM.start();
        this.StartBtn.node.on('click', this.onStartBtnClick, this);
    },

    onStartBtnClick: function(){
        window.EventBus.emit('startGame');
    }
})
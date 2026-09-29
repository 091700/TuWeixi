cc.Class({
    extends: cc.Component,

    start: function () {
        cc.tween(this.node)
            .repeatForever(
                cc.tween()
                    .to(0.7, { scaleX: 1.1, scaleY: 0.9 })  
                    .to(0.7, { scaleX: 0.9, scaleY: 1.1 })  
                    
            )
            .start();
    }
});
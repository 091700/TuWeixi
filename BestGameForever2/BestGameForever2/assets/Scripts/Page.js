cc.Class({
    extends: cc.Component,
    properties:{ 
        fromLeft:{ 
            default:false
        },
    },

    onLoad: function () {
        var page = this.node.getChildByName('Page');
        if (!page) {
            page = this.node.getChildByName('WaveSelectPage');
        }
        if (window.noSlide) { 
            window.noSlide = false; 
            page.x = 0; 
            return; 
        } 
        if(this.fromLeft){
            page.x = -720;
        }else{
            page.x = 720;
        };
        cc.tween(page)
            .to(0.27, { x: 0 })
            .start();
    }
});//预制体滑动动画
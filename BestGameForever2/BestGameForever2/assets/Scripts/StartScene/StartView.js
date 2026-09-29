window.StartView = cc.Class({
    extends: cc.Component,
    properties: { 
        levelPagePrefab: { 
            default: null, 
            type: cc.Prefab 
        }, 
    }, 
    onLoad: function () { 
        window.EventBus.on('startGame', this.onStartGame, this); 
    }, //广播开始游戏

    onDestroy: function () { 
        window.EventBus.targetOff(this); 
    }, 

    onStartGame: function () { 
        var that = this; 
        cc.director.preloadScene('LevelSelectScene', function () { 
            that.doSlideToLevel();
        }); 
    }, //预加载下一个场景

    doSlideToLevel: function () { 
        var page = cc.find('Canvas/Page');
        var levelPage = cc.instantiate(this.levelPagePrefab);
        levelPage.setPosition(720, 0);
        cc.find('Canvas').addChild(levelPage);
        cc.tween(page)
            .to(0.27,{x:-720}) 
            .start(); //start界面往左滑
        cc.tween(levelPage)
            .to(0.27,{x:0}) 
            .call(function(){ //先执行完预制体滑动动画，再加载场景逻辑
                cc.director.loadScene('LevelSelectScene');
            }) 
            .start(); 
        window.noSlide = true;
    }, 
})
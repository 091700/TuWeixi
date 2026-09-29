var WaveSelectView = require('./WaveSelectView');
window.WaveSelectController = cc.Class({
    extends:cc.Component,
    properties:{
        view:{
            default:null,type:WaveSelectView
        },
        ReturnBtn:{
            default:null,type:cc.Button
        },
        levelPagePrefab:{
            default:null,type:cc.Prefab
        },
        gamePagePrefab:{
            default:null,type:cc.Prefab
        }
    },
    onLoad: function () {
        this.model = new WaveSelectModel();
        this.view.model = this.model;
        window.EventBus.on('WaveClicked', this.onWaveClicked, this);
        window.EventBus.on('GoToPage', this.onGoToPage, this);
        this.ReturnBtn.node.on('click', this.onReturnBtnClick, this);
    },
    start: function () {
        this.view.render();
    },

    onWaveClicked: function (level) {
        var state = this.model.getState(level);
        if (state === 'locked') {
            this.view.showTip();
        } else {
            var page = cc.find('Canvas/WaveSelectPage');
            var gamePage = cc.instantiate(this.gamePagePrefab);
            gamePage.setPosition(720,0);
            cc.find('Canvas').addChild(gamePage);
            cc.tween(page)
                .to(0.27,{x:-720})
                .start();
            cc.tween(gamePage)
                .to(0.27,{x:0})
                .call(function(){
                    cc.director.loadScene('BestGameScene');
                })
                .start();
        }
    },
    onGoToPage: function (page) {
        if (this.model.setPage(page)) {
            window.EventBus.emit('WaveSelectPageChanged');
        }
    },

    onReturnBtnClick: function () {
        var page = cc.find('Canvas/WaveSelectPage');
        var levelPage = cc.instantiate(this.levelPagePrefab);
        levelPage.setPosition(-720,0);
        cc.find('Canvas').addChild(levelPage);
        cc.tween(page)
            .to(0.27,{x:720})
            .start();
        cc.tween(levelPage)
            .to(0.27,{x:0})
            .call(function () {
                cc.director.loadScene('LevelSelectScene');
            })
            .start();
        window.noSlide = true;
    },
    onDestroy: function () {
        window.EventBus.targetOff(this);
    }
});
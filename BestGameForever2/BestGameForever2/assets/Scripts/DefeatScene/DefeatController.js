var DefeatView = require('./DefeatView');
window.DefeatController = cc.Class({
    extends:cc.Component,
    properties:{
        view:{
            default:null,type:DefeatView
        },
        RestartBtn:{//返回关卡
            default:null,type:cc.Button
        },
        MenuBtn:{//返回选关
            default:null,type:cc.Button
        },
        gamePagePrefab:{
            default:null,type:cc.Prefab
        },
        WavePagePrefab:{
            default:null,type:cc.Prefab
        },
        SkipLevelBtn:{
            default:null,type:cc.Button
        }
    },

    onLoad:function(){
        this.model = new DefeatModel();
        this.view.model = this.model;
        this.RestartBtn.node.on('click',this.onRestart,this);
        this.MenuBtn.node.on('click',this.onMenu,this);
        this.SkipLevelBtn.node.on('click',this.onSkip,this);
        this.RestartBtn.node.y = 190;
        if(this.model.canSkip()){ 
            this.SkipLevelBtn.node.active = true; 
            this.SkipLevelBtn.node.y = -10; 
            this.MenuBtn.node.y = -210;
        }else{this.SkipLevelBtn.node.active = false;
            this.MenuBtn.node.y = -10;
        }
    },
    
    onSkip:function(){
        window.CurrentLevel = this.model.level+1;
        this.onRestart();
    },

    start:function(){
        this.view.render();
    },

    onRestart:function(){//跳转关卡场景
        var page = cc.find('Canvas/Page');
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
        window.noSlide = true;
    },

    onMenu:function(){//跳转玄关界面
        var page = cc.find('Canvas/Page');
        var WavePage = cc.instantiate(this.WavePagePrefab);
        WavePage.setPosition(-720,0);
        cc.find('Canvas').addChild(WavePage);
        cc.tween(page)
            .to(0.27,{x:720})
            .start();
        cc.tween(WavePage)
            .to(0.27,{x:0})
            .call(function(){
                cc.director.loadScene('WaveSelectScene');
            })
            .start();
        window.noSlide = true;
    }
})
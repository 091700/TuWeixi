cc.Class({
    extends:cc.Component,
    properties:{
        pauseBtn:{
            default:null,type:cc.Button
        },
        pauseScene:{
            default:null,type:cc.Node
        },
        resumeBtn:{
            default:null,type:cc.Button
        },
        restartBtn:{
            default:null,type:cc.Button
        },
        menuBtn:{
            default:null,type:cc.Button
        },
        wavePagePrefab:{
            default:null,type:cc.Prefab
        }
    },
    onLoad:function(){
        this.pauseBtn.node.on('click',this.onPause,this);
        this.resumeBtn.node.on('click',this.onResume,this);
        this.restartBtn.node.on('click',this.onRestart,this);
        this.menuBtn.node.on('click',this.onMenu,this);
    },
    onPause:function(){
        this.pauseScene.active = true;
    },
    onResume:function(){
        this.pauseScene.active = false;
    },
    onRestart: function(){
        cc.director.loadScene('BestGameScene');
    },
    onMenu: function () {
        this.pauseScene.active = false;
        var page = cc.find('Canvas/Page');
        var wavePage = cc.instantiate(this.wavePagePrefab);
        wavePage.setPosition(720,0);
        cc.find('Canvas').addChild(wavePage);
        cc.tween(page)
            .to(0.27,{x:-720})
            .start();
        cc.tween(wavePage)
            .to(0.27,{x:0})
            .call(function(){
                cc.director.loadScene('WaveSelectScene');
            })
            .start();
            window.noSlide = true;
    }
});
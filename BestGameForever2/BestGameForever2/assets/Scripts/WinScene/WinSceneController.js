var WinSceneView = require('./WinSceneView');
window.WinSceneController = cc.Class({
    extends:cc.Component,
    properties:{
        view:{
            default:null,type:WinSceneView
        },
        restartBtn:{
            default:null,type:cc.Button
        },
        nextLevelBtn:{
            default:null,type:cc.Button
        },
        returnMenuBtn:{
            default:null,type:cc.Button
        },
        gamePagePrefab:{
            default:null,type:cc.Prefab
        },
        wavePagePrefab:{
            default:null,type:cc.Prefab
        }
    },

    onLoad:function(){
        this.model = new WinSceneModel();
        this.view.model = this.model;
        this.restartBtn.node.on('click',this.onRestart,this);
        this.nextLevelBtn.node.on('click',this.onNextLevel,this);
        this.returnMenuBtn.node.on('click',this.onReturnMenu,this);
    },

    start:function(){
        this.view.render();
        this.view.showStars(this.model.stars);
        this.view.setScores(this.model.levelScore,this.model.timeBonus,this.model.bestScore);
        this.saveProgress();
        var that = this;
        this.scheduleOnce(function(){
            that.view.playScoreCount();
        },1.5);
    },

    saveProgress:function(){
        var model = this.model;
        var starKey = 'stars_'+model.world+'_'+model.level;
        var oldStars = parseInt(localStorage.getItem(starKey)||'0',10);
        if(model.stars>oldStars){
            localStorage.setItem(starKey,model.stars+'');
        }
        var doneKey = 'completed_'+model.world;
        var oldDone = parseInt(localStorage.getItem(doneKey)||'0',10);
        if(model.level>oldDone){
            localStorage.setItem(doneKey,model.level+'');
        }
    },

    onRestart:function(){
        this.goGame();
    },

    onNextLevel:function(){
        window.CurrentLevel = this.model.level+1;
        this.goGame();
    },

    onReturnMenu:function(){
        this.goWave();
    },

    goGame:function(){//换页
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
    goWave:function(){var page = cc.find('Canvas/Page'); 
        var wavePage = cc.instantiate(this.wavePagePrefab);
        wavePage.setPosition(-720,0);
        cc.find('Canvas').addChild(wavePage);
        cc.tween(page)
            .to(0.27,{x:720})
            .start();
        cc.tween(wavePage)
            .to(0.27,{x:0})
            .call(function(){
                cc.director.loadScene('WaveSelectScene');
            })
            .start ();
        window.noSlide = true;
    }
})
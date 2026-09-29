var LevelSelectView = require('./LevelSelectView');
window.LevelSelectController = cc.Class({
    extends:cc.Component,
    properties:{
        view:{
            default:null,
            type:LevelSelectView
        },
        ReturnBtn:{
            default:null,
            type:cc.Button
        },
        startPagePrefab:{
            default:null,
            type:cc.Prefab
        },
        wavePagePrefab:{
            default:null,
            type:cc.Prefab
        }
    },

    onLoad:function(){
        this.model = new LevelSelectModel();
        this.view.model = this.model; //把model传给view
        window.EventBus.on('WorldClicked',this.onWorldClicked,this);
        window.EventBus.on('GoToPage',this.onGoToPage,this);
        this.ReturnBtn.node.on('click',this.onReturnBtnClick,this);
    },

    start:function(){ 
        this.view.render();
    },

    onWorldClicked:function(worldNumber){
        if(this.model.worlds[worldNumber-1].unlocked){
            var page = cc.find('Canvas/Page');//当前正在显示的页面
            var wavePage = cc.instantiate(this.wavePagePrefab);
            wavePage.setPosition(720, 0);
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
            window.CurrentWorld = worldNumber;
        }else{
            this.view.showTip();
        }
    },

    onGoToPage:function(page){
        if(this.model.setPage(page)){
            window.EventBus.emit('LevelSelectPageChanged');
        }
    },

    onReturnBtnClick:function(){ 
        var page = cc.find('Canvas/Page'); 
        var startPage = cc.instantiate(this.startPagePrefab);
        startPage.setPosition(-720, 0); 
        cc.find('Canvas').addChild(startPage); 
        cc.tween(page) 
            .to(0.27,{x:720}) 
            .start(); 
        cc.tween(startPage) 
            .to(0.27,{x:0}) 
            .call(function(){ 
                cc.director.loadScene('StartScene'); 
            }) 
            .start(); 
        window.noSlide = true;  
    }, 
    onDestroy:function(){ 
        window.EventBus.targetOff(this); 
    } 
})
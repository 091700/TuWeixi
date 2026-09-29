window.LevelSelectView = cc.Class({
    extends:cc.Component,
    properties:{
        Parent:{
            default:null,type:cc.Node
        },
        unlockPrefab:{
            default:null,type:cc.Prefab
        },
        lockedPrefab:{
            default:null,type:cc.Prefab
        },
        ballPrefab:{
            default:null,type:cc.Prefab
        },
        thisPageBallImg :{ 
            default:null,type:cc.SpriteFrame
        }, 
        anotherPageBallImg:{ 
            default:null,type:cc.SpriteFrame 
        },
        tipPrefab:{
            default:null,type:cc.Prefab
        },
        model:{
            default:null
        },
    },

    onLoad:function(){ 
        this.slots = [cc.v2(-165,310),cc.v2(165,310),cc.v2(-165,-25),cc.v2(165,-25)]; //四个框框
        this.tip = null;
        this.lastPage = 1;
        this.ballParent = new cc.Node('Balls'); 
        cc.find('Canvas/Page').addChild(this.ballParent); 
        window.EventBus.on('LevelSelectPageChanged',this.onPageChanged,this); 
    }, 
    onDestroy:function(){ 
        window.EventBus.targetOff(this); 
    }, 

    render:function(){ 
        this.Parent.removeAllChildren();
        this.buildWorlds(0);
        this.buildBalls();
        this.lastPage = this.model.CurrentPage;//记住现在显示的是第几页
    }, 

    buildWorlds:function(offsetX){//渲染世界框
        var model = this.model;
        var worlds = model.getPageWorlds();
        for(var i = 0;i<worlds.length;i++){
            var world = worlds[i];
            var worldIndex = (model.CurrentPage-1)*model.PageSize+i+1; //第几个世界
            var node = cc.instantiate(world.unlocked ? this.unlockPrefab : this.lockedPrefab); 
            node.setPosition(this.slots[i].x + offsetX, this.slots[i].y);
            node.getChildByName('WorldNumberLabel').getComponent(cc.Label).string = world.name; 
            node.on('click',(function(index){ 
                return function(){
                    window.EventBus.emit('WorldClicked',index); 
                };
            })(worldIndex)); 
            node.parent = this.Parent;
        } 
    }, 

    buildBalls:function(){//换页球
        var model = this.model; 
        this.ballParent.removeAllChildren(); //先清掉上一次画的球
        var totalPages = model.getTotalPages();
        var totalBallsWidth = totalPages*50+(totalPages-1)*10;
        var centerX = -totalBallsWidth/2+50/2;
        for(var i = 0;i<totalPages;i++){ 
            var ball = cc.instantiate(this.ballPrefab); //盖一个球的新节点
            ball.setPosition(centerX+i*(50+10),-230);
            var sprite = ball.getComponent(cc.Sprite);
            if(i===model.CurrentPage-1){
                sprite.spriteFrame = this.thisPageBallImg;
            }else{
                sprite.spriteFrame = this.anotherPageBallImg;
                ball.on('click',(function(p){ 
                    return function(){
                        window.EventBus.emit('GoToPage',p);
                    };
                })(i+1)); 
            } 
            ball.parent = this.ballParent;
        } 
    }, 

    onPageChanged:function(){ 
        var model = this.model; 
        var dir;
        if(model.CurrentPage>this.lastPage){//dir=1往左滑
            dir = 1;
        }else{
            dir = -1;
        };
        this.lastPage = model.CurrentPage;
        var olds = this.Parent.children.slice(); 
        for(var i=0;i<olds.length;i++){ 
            (function(node){ 
                cc.tween(node)
                    .to(0.2, { x: node.x - dir*720 })
                    .call(function(){ node.destroy(); })
                    .start();
            })(olds[i]); 
        } 

        //造下面页的框。把x放在屏幕外,y用原来的
        var worlds = model.getPageWorlds(); 
        for(var j=0;j<worlds.length;j++){ 
            var world = worlds[j]; 
            var worldIndex = (model.CurrentPage-1)*model.PageSize+j+1; 
            var node;
            if (world.unlocked){
                node = cc.instantiate(this.unlockPrefab);
            }else{
                node = cc.instantiate(this.lockedPrefab);
            };
            node.x = this.slots[j].x + dir*720;
            node.y = this.slots[j].y; 
            node.getChildByName('WorldNumberLabel').getComponent(cc.Label).string = world.name; 
            node.on('click',(function(index){ 
                return function(){
                    window.EventBus.emit('WorldClicked',index);
                };
            })(worldIndex)); 
            cc.tween(node).to(0.2,{x:this.slots[j].x}).start();
            node.parent = this.Parent; 
        } 
        this.buildBalls(); 
    }, 

    showTip:function(){//渲染提示框，false隐藏
        var that = this;
        if(!this.tip){
            this.tip = cc.instantiate(this.tipPrefab);
            this.tip.setPosition(0,0);
            cc.find('Canvas').addChild(this.tip);
            this.tip.getChildByName('TipLabel').getChildByName('OKBtn').on('click',function(){
                that.tip.active = false;
            });
        }
        this.tip.active = true;
    }  
})
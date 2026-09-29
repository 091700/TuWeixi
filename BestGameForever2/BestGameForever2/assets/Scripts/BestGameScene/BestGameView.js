window.BestGameView = cc.Class({
    extends:cc.Component,
    //显示层:只负责把数据画出来,不做规则判断

    properties:{
        Board:{//棋盘容器
            default:null,type:cc.Node
        },
        gemFrames:{//6张宝石图,顺序:蓝绿紫红白黄(和Model的STAR_COLOR一一对应)
            default:[],type:cc.SpriteFrame
        },
        cellFrames:{
            default:[],type:cc.SpriteFrame
        },
        tip1Prefab:{
            default:null,type:cc.Prefab
        }, 
        tip2Prefab:{
            default:null,type:cc.Prefab
        }, 
        tip3Prefab:{
            default:null,type:cc.Prefab
        }, 
        handPrefab:{//手指
            default:null,type:cc.Prefab
        },
        goalGemPrefab:{//目标宝石
            default:null,type:cc.Prefab
        },  
        jinDuTiao:{
            default:null,type:cc.Sprite
        }, 
        leftTimeLabel:{//剩余时间
            default:null,type:cc.Label
        },
        scoreLabel:{//得分
            default:null,type:cc.Label
        },
        bestScoreLabel:{//最高得分
            default:null,type:cc.Label
        },
        model:{
            default:null
        }
    },

    onLoad:function(){
        this.tipNode = null;
        this.handNode = null;
        this.goalNode = null;
        if(this.jinDuTiao){
            this.jinDuTiao.type = cc.Sprite.Type.FILLED;
            this.jinDuTiao.fillType = cc.Sprite.FillType.HORIZONTAL;
            this.jinDuTiao.fillStart = 0;
            this.jinDuTiao.fillRange = 1;
        }
    },

    refresh:function(){
        if(this.Board === null)return;
        this.Board.removeAllChildren();//清空重画棋盘
        var model = this.model;
        for(var r = 0;r<model.ROW;r++){
            for(var c = 0;c < model.COL;c++){
                var cell = model.board[r][c];
                var x = model.cellX(c);
                var y = model.cellY(r);
                var bg = new cc.Node('bg');
                bg.parent = this.Board;
                bg.setPosition(x,y);
                var bgSprite = bg.addComponent(cc.Sprite);
                bgSprite.spriteFrame = this.cellFrames[cell.level];
                bg.width = 91.43;
                bg.height = 91.43;
                if(cell.gem !== ''){
                    var gem = new cc.Node('gem_'+r+'_'+c);
                    gem.parent = this.Board;
                    gem.setPosition(x,y);
                    var gemSprite = gem.addComponent(cc.Sprite);
                    gemSprite.spriteFrame = this.gemFrames[this.gemIndex(cell.gem)];
                    gem.width = 90;
                    gem.height = 90;
                }
            }
        }
    },

    //颜色名 → 数组下标
    gemIndex:function(name){
        if(name === 'blue')return 0;
        if(name === 'green')return 1;
        if(name === 'purple')return 2;
        if(name === 'red')return 3;
        if(name === 'white')return 4;
        return 5;
    },

    //显示教程:弹出弹窗,在手指标出的两格之间放手指
    //手指标(r1,c1)(r2,c2),不需要手指时传-1
    showtodorial:function(prefab,r1,c1,r2,c2){
        this.tipNode = cc.instantiate(prefab);
        this.tipNode.parent = cc.find('Canvas');
        this.tipNode.setPosition(0,0);

        if(r1 >= 0){
            this.handNode = cc.instantiate(this.handPrefab);
            this.handNode.parent = cc.find('Canvas');
            this.playHand(r1,c1,r2,c2);
        }
    },
    
    //棋子交换动画，让A和B互相滑动到对面的位置
    playChangeAnim:function(r1,c1,r2,c2,callback){
        var model = this.model;
        var x1 = model.cellX(c1);
        var y1 = model.cellY(r1);
        var x2 = model.cellX(c2);
        var y2 = model.cellY(r2);
        var gemA = this.Board.getChildByName('gem_'+r1+'_'+c1);
        var gemB = this.Board.getChildByName('gem_'+r2+'_'+c2);
        var changeTime = 0.2;
        cc.tween(gemA)
            .to(changeTime,{x:x2,y:y2})
            .start();
        cc.tween(gemB)
            .to(changeTime,{x:x1,y:y1})
            .call(function(){
                callback();//通知controller换数据
            })
            .start();

    },
    //手指在教程格子之间拖动
    playHand:function(r1,c1,r2,c2){
        var model = this.model;
        var x1 = model.cellX(c1);
        var y1 = model.cellY(r1);
        var x2 = model.cellX(c2);
        var y2 = model.cellY(r2);
        var a_x = 31;
        var a_y = -42;
        this.handNode.setPosition(x1+a_x,y1+a_y);
        cc.tween(this.handNode)
            .repeatForever(
                cc.tween()
                    .to(1.0,{x:x2+a_x,y:y2+a_y})
                    .to(1.0,{x:x1+a_x,y:y1+a_y})
                    .delay(0.4)
            )
            .start();
    },

    //收起当前教程界面(弹窗、手指)
    hidetodorial:function(){
        if(this.tipNode){
            this.tipNode.destroy();
            this.tipNode = null;
        }
        if(this.handNode){
            cc.Tween.stopAllByTarget(this.handNode);   // 先停掉手指的循环动画
            this.handNode.destroy();
            this.handNode = null;
        }
    },

    //更新倒计时,进度条用Sprite填充模式:fillRange越小,右侧越少(左侧保持不动,不碰锚点)
    updateTime:function(left){
        left = Math.floor(left);   //先取整,防止显示跑到小数点后面
        var minutes = Math.floor(left/60);
        var seconds = left%60;
        var text = minutes + ':' + (seconds < 10 ? '0'+seconds : seconds);
        this.leftTimeLabel.string = text;

        var ratio = left/this.model.TOTAL_TIME;   //剩余比例,1满→0空
        this.jinDuTiao.fillRange = ratio;
    },

    //更新分数
    updateScore:function(score,best){
        this.scoreLabel.string = score + '';
        this.bestScoreLabel.string = best + '';
    },

    //胜利:从棋盘上方掉一颗GoalGem,落到最下面一行
    showGoalGem:function(){
        var model = this.model;
        this.goalNode = cc.instantiate(this.goalGemPrefab);
        this.goalNode.parent = this.Board;

        var col = Math.floor(Math.random()*9);   // 随机选一列
        this.goalNode.setPosition(model.cellX(col), model.TOP_Y + 300);   // 从上方开始

        cc.tween(this.goalNode)
            .to(0.8,{y:model.cellY(8)})   // 0.8秒落到第8行(最下面)
            .call(function(){
                window.EventBus.emit('GameWin');   // 落地后通知控制器:胜利
            })
            .start();
    }
})
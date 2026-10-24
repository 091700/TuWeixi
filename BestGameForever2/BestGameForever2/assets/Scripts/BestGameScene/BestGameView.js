window.BestGameView = cc.Class({
    extends:cc.Component,
    properties:{
        Board:{//棋盘容器
            default:null,type:cc.Node
        },
        gemFrames:{//6个宝石
            default:[],type:cc.SpriteFrame
        },
        cellFrames:{//四个难度棋格
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
        },
        borderFrames:{
            default:[],type:cc.SpriteFrame
        },
        LevelLabel:{
            default:null,type:cc.Label
        },
        startLabelPrefab:{
            default:null,type:cc.Prefab
        },
        scoreFont:{
            default:null,type:cc.BitmapFont
        },
        bombFrame:{
            default:null,type:cc.SpriteFrame
        },
        bombFireFrame:{
            default:null,type:cc.SpriteFrame
        },
        boomFrames:{
            default:[],type:cc.SpriteFrame
        },
        fuseX:{
            default:122
        },
        fuseY:{
            default:70
        },
        fireScale:{
            default:0.72
        },
        boomSize:{
            default:1.5
        },
        boomPush:{
            default:600
        }
    },

    onLoad:function(){
        this.tipNode = null;
        this.handNode = null;
        this.goalNode = null;
        this.handFrozen = false;
        this.handRunning = false;
        this.handPosition = null;
        this.hintNodes = [];
        this.hintTime = 0;
        this.fireCheck = 0;
        //场景文件里烘焙了旧数值(boomPush=42),会在反序列化时覆盖代码默认值,
        //所以这里强制写回一个肉眼可见的冲击波强度(像素)
        this.boomPush = 150;
        if(this.jinDuTiao){
            this.jinDuTiao.type = cc.Sprite.Type.FILLED;//填充型
            this.jinDuTiao.fillType = cc.Sprite.FillType.HORIZONTAL;//水平型
            this.jinDuTiao.fillStart = 0;//从右侧开始消失
            this.jinDuTiao.fillRange = 1;
        }
    },

    refresh:function(){//数据变化时重画棋盘。先destroy再model.board
        if(this.Board === null)return;
        this.Board.removeAllChildren();
        var model = this.model;
        for(var r = 0;r<model.ROW;r++){
            for(var c = 0;c < model.COL;c++){
                var cell = model.board[r][c];
                var x = model.cellX(c);
                var y = model.cellY(r);
                if(cell.level!==-1){
                    var base = new cc.Node('bg_base_'+r+'_'+c);
                    base.parent = this.Board;
                    base.setPosition(x,y);
                    var bs = base.addComponent(cc.Sprite);
                    bs.spriteFrame = this.cellFrames[0];
                    bs.sizeMode = cc.Sprite.SizeMode.CUSTOM;
                    base.width = 91.43;
                    base.height = 91.43;
                    if(cell.level>0){
                        var lv = new cc.Node('bg_lv_'+r+'_'+c);
                        lv.parent = this.Board;
                        lv.setPosition(x,y);
                        var ls = lv.addComponent(cc.Sprite);
                        ls.spriteFrame = this.cellFrames[cell.level];
                        ls.sizeMode = cc.Sprite.SizeMode.CUSTOM;
                        lv.width = 91.43;
                        lv.height = 91.43;
                    }
                }
                if(cell.gem==='goal'){
                    var goalNode = cc.instantiate(this.goalGemPrefab);
                    goalNode.parent = this.Board;
                    goalNode.name = 'goal';
                    goalNode.setPosition(x,y);
                    this.goalNode = goalNode;
                    this.goalRollsIdle(goalNode);//重绘之后也要保持两个roll的旋转
                }
                else if (cell.gem!==''){
                    var gem = new cc.Node('gem_'+r+'_'+c);
                    gem.parent = this.Board ;
                    gem.setPosition(x,y); 
                    var gemSprite = gem.addComponent(cc.Sprite);
                    gemSprite.spriteFrame = this.gemFrames[this.gemIndex(cell.gem)];
                    gemSprite.sizeMode = cc.Sprite.SizeMode.CUSTOM;
                    gem.width = 84 ;
                    gem.height = 84 ;
                    if(cell.bomb===true){
                        gem.zIndex = 2;
                        this.addBomb(gem,false);
                    }
            }
            }
        }this.buildBorder();
    },
    
    buildBorder:function(){
        var model = this.model;
        var Thick = 10;
        var HALF = 50.715;
        var TopLeft = 0,TopRight = 1,ButtonLeft = 2,ButtonRight = 3,Horizontal = 4,Vertical = 5;
        for(var r = 0;r<model.ROW;r++){
            for(var c = 0;c<model.COL;c++){
                if(model.board[r][c].level===-1)
                    continue;
                var x = model.cellX(c);
                var y = model.cellY(r);
                var up = this.hasNeighbor(r-1,c);
                var down = this.hasNeighbor(r+1,c);
                var left = this.hasNeighbor(r,c-1);
                var right = this.hasNeighbor(r,c+1);
                //四条直边
                if(!up)this.putBorder(x,y+HALF,model.STEP,Thick,this.borderFrames[Horizontal]);
                if(!down)this.putBorder(x,y-HALF,model.STEP,Thick,this.borderFrames[Horizontal]);
                if(!left)this.putBorder(x-HALF,y,Thick,model.STEP,this.borderFrames[Vertical]);
                if(!right)this.putBorder(x+HALF,y,Thick,model.STEP,this.borderFrames[Vertical]);
                //四个转角
                if(!up&&!left)this.putBorder(x-HALF,y+HALF,Thick,Thick,this.borderFrames[TopLeft]);
                if(!up&&!right)this.putBorder(x+HALF,y+HALF,Thick,Thick,this.borderFrames[TopRight]);
                if(!down&&!left)this.putBorder(x-HALF,y-HALF,Thick,Thick,this.borderFrames[ButtonLeft]);
                if(!down&&!right)this.putBorder(x+HALF,y-HALF,Thick,Thick,this.borderFrames[ButtonRight]);
            }
        }
    },
    
    playBgChange:function(r,c,lv){
        var node = this.Board.getChildByName('bg_lv_'+r+'_'+c);
        if(!node)
            return;
        cc.Tween.stopAllByTarget(node);
        var sp = node.getComponent(cc.Sprite);
        var that = this;
        cc.tween(node)
            .to(0.25,{scaleX:0},{easing:cc.easing.quadIn})//棋格左右压缩到0
            .call(function(){
                if(lv<=0){
                    node.active = false;
                }else{
                    sp.spriteFrame = that.cellFrames[lv];
                    cc.tween(node)
                        .to(0.25,{scaleX:1},{easing:cc.easing.quadOut})
                        .start();
                }
            })
            .start();
    },

    hasNeighbor:function(r,c){
        var model = this.model;
        if(r<0||r>=model.ROW)
            return false;
        if(c<0||c>=model.COL)
            return false;
        if(model.board[r][c].level===-1)
            return false;
        return true;
    },

    putBorder:function(x,y,w,h,frame){
        var node = new cc.Node('border');
        node.parent = this.Board;
        node.setPosition(x,y);
        var sp = node.addComponent(cc.Sprite);
        sp.spriteFrame = frame;
        node.width = w;
        node.height = h;
    },

    gemIndex:function(name){//颜色编号
        if(name === 'blue')return 0;
        if(name === 'green')return 1;
        if(name === 'purple')return 2;
        if(name === 'red')return 3;
        if(name === 'white')return 4;
        return 5;
    },

    showTodo:function(prefab,r1,c1,r2,c2){//开始教程
        this.tipNode = cc.instantiate(prefab);
        this.tipNode.parent = cc.find('Canvas/Page');
        this.tipNode.setPosition(0,0);
        if(r1 >= 0){
            this.handNode = cc.instantiate(this.handPrefab);
            this.handNode.parent = cc.find('Canvas/Page');
            this.handPosition = {r1:r1,c1:c1,r2:r2,c2:c2};
            if (this.handFrozen){
                this.handRunning = false;
            }else{ 
                this.playHand (r1,c1,r2,c2);
        }
        }
    },
    
    gemNodeAt:function(r,c){//这一格上的棋子节点(goal宝石名字固定叫goal)
        var model = this.model;
        if(model.board[r][c].gem==='goal'){
            return this.Board.getChildByName('goal');
        }
        return this.Board.getChildByName('gem_'+r+'_'+c);
    },

    //棋子交换动画，让A和B互相滑动到对面的位置
    playChangeAnim:function(r1,c1,r2,c2,callback){
        var model = this.model;
        var gemA = this.gemNodeAt(r1,c1);
        var gemB = this.gemNodeAt(r2,c2);
        if(!gemA||!gemB){
            callback();
            return;
        }
        var changeTime = 0.2;
        cc.Tween.stopAllByTarget(gemA);
        cc.Tween.stopAllByTarget(gemB);
        gemA.zIndex = 11;//棋子放到最上层
        gemB.zIndex = 10;
        cc.tween(gemA)
            .to(changeTime,{x:model.cellX(c2),y:model.cellY(r2)})
            .start();
        cc.tween(gemB)
            .to(changeTime,{x:model.cellX(c1),y:model.cellY(r1)})
            .call(function(){
                gemA.zIndex = 0;
                gemB.zIndex = 0;
                if(gemA.name!=='goal'){
                    gemA.name = 'gem_'+r2+'_'+c2;
                }
                if(gemB.name!=='goal'){
                    gemB.name = 'gem_'+r1+'_'+c1;
                }
                callback();//通知controller换数据
            })
            .start();

    },
    //消除下落动画
    playClearAnim:function(callback){
        this.unscheduleAllCallbacks();
        this.clearSteps = this.model.steps;
        this.clearIndex = 0;
        this.clearEndCallback = callback;
        this.playNextStep();
    },

    playNextStep:function(){
        if(this.clearIndex>=this.clearSteps.length){
            this.clearEndCallback();
            return;
        }
        var step = this.clearSteps[this.clearIndex];
        this.clearIndex = this.clearIndex+1;
        this.playStep(step);
    },

    playStep:function(step){
        var that = this;
        var model = this.model;
        var SPEED = 1024;
        var MIN_TIME = 0.25;//宝石压缩时长
        var maxTime = 0;
        var goalIntroTime = 0;//goal宝石开场动画时长
        var spring = function(t){//棋子浮动函数
            return 1-Math.exp(-4.1*t)*Math.cos(18.5*t);
        };
        if(step.bonus>0){
            this.showComboBanner(step.bonus);
        }
        this.deadList = [];//要被消除的棋子
        this.boomDeadList = [];//被爆炸波及的棋子,先弹一下再消除
        var boomHit = [];
        for(var br0 = 0;br0<model.ROW;br0++){
            boomHit.push([]);
            for(var bc0 = 0;bc0<model.COL;bc0++){
                boomHit[br0].push(false);
            }
        }
        for(var bz = 0;bz<step.booms.length;bz++){
            for(var bzr = -1;bzr<=1;bzr++){
                for(var bzc = -1;bzc<=1;bzc++){
                    var bzrr = step.booms[bz].row+bzr;
                    var bzcc = step.booms[bz].column+bzc;
                    if(bzrr<0||bzrr>=model.ROW||bzcc<0||bzcc>=model.COL){
                        continue;
                    }
                    boomHit[bzrr][bzcc] = true;
                }
            }
        }
        for(var i = 0;i<step.cleared.length;i++){
            var clearRow = step.cleared[i][0];
            var clearColumn = step.cleared[i][1];
            var dead = this.Board.getChildByName('gem_'+clearRow+'_'+clearColumn);
            if(!dead)
                continue;
            dead.zIndex = 1;
            this.deadList.push(dead);
            cc.Tween.stopAllByTarget(dead);
            if(boomHit[clearRow][clearColumn]){
                dead.name = 'boomgem_'+clearRow+'_'+clearColumn;
                this.boomDeadList.push(dead);
            }else{
                dead.name = 'dead';
                cc.tween(dead)
                    .to(MIN_TIME,{scale:0})
                    .start();
            }
            this.showScoreNumber(clearRow,clearColumn,step.perGem+'');
        }
        for(var bb = 0;bb<step.bombs.length;bb++){
            var bombInfo = step.bombs[bb];
            var bombGem = this.Board.getChildByName('gem_'+bombInfo.row+'_'+bombInfo.column);
            if(bombGem){
                cc.Tween.stopAllByTarget(bombGem);
                bombGem.scale = 1;
                bombGem.opacity = 255;
                this.addBomb(bombGem,true);
            }
        }
        var expand = false;
        for(var d = 0;d<step.downs.length;d++){
            var down = step.downs[d];
            if(down.level>0){
                expand = true;
            }this.playBgChange(down.row,down.column,down.level);
        }
        var bgTotal = 0.25;
        if(expand){
            bgTotal = 0.5;
        }
        var FLASH_LEAD = 0.12;//爆炸火光出现的时刻,冲击波要和它同步
        var SHOCK_OUT = 0.18;//棋子被冲击波推出去
        var SHOCK_BACK = 0.28;//棋子弹回原位
        var SHOCK_TIME = SHOCK_OUT+SHOCK_BACK;
        var pushLead = 0;
        if(step.booms.length>0){
            bgTotal = 0.35;
            pushLead = FLASH_LEAD+SHOCK_TIME;//等待时间里要算上这段冲击波时长
        }
        for(var bz2 = 0;bz2<step.booms.length;bz2++){
            this.collectBoomPush(step.booms[bz2].row,step.booms[bz2].column);
        }
        for(var j = 0;j<step.falls.length;j++){//新宝石滑到格子
            var fall = step.falls[j];
            var x = model.cellX(fall.column);
            var y = model.cellY(fall.toRow);
            var node = null;
            if(fall.gem==='goal'){
                node = this.Board.getChildByName('goal');
                if(!node){//goal宝石第一次出场,播开场动画(两个roll从屏幕外飞进来再落到棋格)
                    node = cc.instantiate(this.goalGemPrefab);
                    node.parent = this.Board;
                    node.name = 'goal';
                    node.setPosition(x,y);
                    this.goalNode = node;
                    goalIntroTime = this.playGoalIntro(node,x,y);
                    continue;//自带开场动画,不走普通下落
                }
            }
            else if(fall.fromRow>=0){//宝石掉落，改名
                node = this.Board.getChildByName('gem_'+fall.fromRow+'_'+fall.column);
                if(!node)
                    continue;
                node.name = 'gem_'+fall.toRow+'_'+fall.column;
            }
            else{//新生成棋子排队出场
                node = new cc.Node('gem_'+fall.toRow+'_'+fall.column);
                node.parent = this.Board;
                node.setPosition(x,fall.spawnY);
                var sp = node.addComponent(cc.Sprite);
                sp.spriteFrame = this.gemFrames[this.gemIndex(fall.gem)];
                sp.sizeMode = cc.Sprite.SizeMode.CUSTOM;
                node.width = 84;
                node.height = 84;
            }
        
        var dist = Math.abs(y-node.y);
        var t = dist/SPEED;
        if(t<MIN_TIME){
            t = MIN_TIME;
        }
        if(t>maxTime){
            maxTime = t;
        }
        cc.Tween.stopAllByTarget(node);
        node.zIndex = 1;
        var pushX = node.pushX||0;
        var pushY = node.pushY||0;
        node.pushX = 0;
        node.pushY = 0;
        node.pushDone = true;
        var move = cc.tween(node);
        if(pushX!==0||pushY!==0){//等爆炸火光出现后,棋子被冲击波弹出去,再弹回原位,然后才开始下落
            move = move
                .delay(FLASH_LEAD)
                .to(SHOCK_OUT,{x:node.x+pushX,y:node.y+pushY},{easing:cc.easing.quadOut})
                .to(SHOCK_BACK,{x:node.x,y:node.y},{easing:cc.easing.quadIn});
        }
        move.delay(bgTotal)
            .to(t,{x:x,y:y-21},{easing:cc.easing.quadIn})
            .to(1,{y:y},{easing:spring})
            .start();
        }
        for(var bz3 = 0;bz3<step.booms.length;bz3++){
            this.playBoomPush(step.booms[bz3].row,step.booms[bz3].column);
        }
        var stepAnim = maxTime;
        if(goalIntroTime>stepAnim){//goal开场动画和其他下落同时进行,取更长的那一个
            stepAnim = goalIntroTime;
        }
        var waitTime;
        if(this.clearIndex>=this.clearSteps.length){
            waitTime = pushLead+bgTotal+stepAnim+1.02;
        }else{
            waitTime = pushLead+bgTotal+stepAnim;
        }
        if(step.booms.length>0){
            var boomPos = step.booms;
            this.scheduleOnce(function(){
                for(var bq = 0;bq<boomPos.length;bq++){
                    that.playBoom(boomPos[bq].row,boomPos[bq].column);
                }
                //被爆炸消除的3x3内圈棋子:先被冲击波弹出去,弹到最远时才缩小消失
                for(var bd = 0;bd<that.boomDeadList.length;bd++){
                    var dg = that.boomDeadList[bd];
                    if(!cc.isValid(dg)){
                        continue;
                    }
                    var dpx = dg.pushX||0;
                    var dpy = dg.pushY||0;
                    var dbx = dg.x;
                    var dby = dg.y;
                    dg.pushX = 0;
                    dg.pushY = 0;
                    dg.pushDone = true;
                    cc.tween(dg)
                        .to(SHOCK_OUT,{x:dbx+dpx,y:dby+dpy},{easing:cc.easing.quadOut})
                        .to(0.1,{scale:0})
                        .start();
                }
            },FLASH_LEAD);
        }

        this.scheduleOnce(function(){
            for(var k = 0;k<that.deadList.length;k++){
                that.deadList[k].destroy();
            }
            that.playNextStep();
        },waitTime);
    },
    
    showScoreNumber:function(row,column,text){
        var model = this.model;
        var node = new cc.Node('score');
        node.parent = this.Board;
        node.setPosition(model.cellX(column),model.cellY(row));
        node.zIndex = 5;
        var label = node.addComponent(cc.Label);
        label.font = this.scoreFont;
        label.fontSize = 42;
        label.string = text;
        var upY = node.y+model.STEP;
        cc.tween(node)//向上消失
            .to(0.9,{y:upY})
            .to(0.2,{y:upY,opacity:0})
            .call(function(){
                node.destroy();
            })
            .start();
    },

    playHand:function(r1,c1,r2,c2){//手指在教程格子之间拖动
        var model = this.model;
        var x1 = model.cellX(c1);
        var y1 = model.cellY(r1);
        var x2 = model.cellX(c2);
        var y2 = model.cellY(r2);
        var a_x = 31;
        var a_y = -42;
        cc.Tween.stopAllByTarget(this.handNode);
        this.handNode.setPosition(x1+a_x,y1+a_y);
        cc.tween(this.handNode)
            .repeatForever(
                cc.tween()
                    .to(1.0,{x:x2+a_x,y:y2+a_y})
                    .to(1.0,{x:x1+a_x,y:y1+a_y})
                    .delay(0.4)
            )
            .start();
            this.handRunning = true;
    },

    pauseHand:function(){
        this.handFrozen = true;
        if(this.handNode){
            cc.director.getActionManager().pauseTarget(this.handNode);
        }
    },

    resumeHand:function(){
        this.handFrozen = false;
        if(!this.handNode)
            return;
        if(this.handRunning){
            cc.director.getActionManager().resumeTarget(this.handNode);
        }else{
            this.playHand(this.handPosition.r1,this.handPosition.c1,this.handPosition.r2,this.handPosition.c2);
        }
    },

    pauseBoard:function(){//暂停把棋盘冻结
        cc.director.getScheduler().pauseTarget(this);
        var gm = cc.director.getActionManager();
        var list = this.Board.children;
        for(var i = 0;i<list.length;i++){
            gm.pauseTarget(list[i]);
            var kids = list[i].children;
            for(var k = 0;k<kids.length;k++){
                gm.pauseTarget(kids[k]);
            }
        }
    },

    resumeBoard:function(){
        cc.director.getScheduler().resumeTarget(this);
        var gm = cc.director.getActionManager();
        var list = this.Board.children;
        for(var i = 0;i<list.length;i++){
            gm.resumeTarget(list[i]);
            var kids = list[i].children;
            for(var k = 0;k<kids.length;k++){
                gm.resumeTarget(kids[k]);
            }
        }
    },

    hideTodo:function(){//消除教程
        if(this.tipNode){
            this.tipNode.destroy();
            this.tipNode = null;
        }
        if(this.handNode){
            cc.Tween.stopAllByTarget(this.handNode);
            this.handNode.destroy();
            this.handNode = null;
        }
    },

    updateTime:function(left){//更新进度条
        left = Math.floor(left);
        var minutes = Math.floor(left/60);
        var seconds = left%60;
        var text;
        if (seconds<10){
            text = minutes+':'+'0'+seconds;
        }else {
            text = minutes+':'+seconds;
        }
        this.leftTimeLabel.string = text;
        var leftJinDuTiao = left/this.model.TOTAL_TIME;
        this.jinDuTiao.fillRange = leftJinDuTiao;
    },

    updateScore:function(score,best){//更新分数
        this.scoreLabel.string = score + '';
        this.bestScoreLabel.string = best + '';
    },

    setLevelLabel:function(text){//关卡号
        if(this.LevelLabel){
            this.LevelLabel.string = text;
        }
    },

    showStartLabel:function(text,callback){//显示开局文字
        var node = cc.instantiate(this.startLabelPrefab);
        this.startLabelNode = node;
        node.parent = cc.find('Canvas/Page');
        node.setPosition(0,0);
        var label = node.getComponent(cc.Label);
        if(label){
            label.string = text;
        }
        this.scheduleOnce(function(){
            cc.tween(node)
                .to(0.3,{x:900},{easing:cc.easing.quadOut})
                .call(function(){
                    node.destroy();
                    callback();
                }).start();
        },1.4);
    },

    hideStartLabel:function(){
        if(this.startLabelNode){
            this.startLabelNode.destroy();
            this.startLabelNode = null;
        }
    },

    showNotice:function(text,hold,callback){
        var node = cc.instantiate(this.startLabelPrefab);
        this.noticeNode = node;
        node.parent = cc.find('Canvas/Page');
        node.setPosition(0,0);
        node.zIndex = 9;
        var label = node.getComponent(cc.Label);
        if(label){
            label.string = text;
        }
        var that = this;
        this.scheduleOnce(function(){
            cc.tween(node)
                .to(0.3,{x:900},{easing:cc.easing.quadOut})
                .call(function(){
                    node.destroy();
                    that.noticeNode = null;
                    callback();
                })
                .start();
        },hold);
    },

    playShuffle:function(callback){
        var model = this.model;
        var moves = model.shuffleMoves;
        var list = [];
        for(var i = 0;i<moves.length;i++){
            var mv = moves[i];
            var node = this.Board.getChildByName('gem_'+mv.fromRow+'_'+mv.fromColumn);
            if(!node)
                continue;
            list.push({node:node,toRow:mv.toRow,toColumn:mv.toColumn});
        }
        for(var j = 0;j<list.length;j++){
            var item = list[j];
            cc.Tween.stopAllByTarget(item.node);
            item.node.zIndex = 1;
            cc.tween(item.node)
                .to(0.5,{x:model.cellX(item.toColumn),y:model.cellY(item.toRow)},{easing:cc.easing.quadInOut})
                .start();
        }
        this.scheduleOnce(function(){
            for(var k = 0;k<list.length;k++){
                list[k].node.name = 'gem_'+list[k].toRow+'_'+list[k].toColumn;
            }
            callback();
        },0.55);
    },

    playBoardDropOut:function(callback){//刷新棋盘掉出屏幕
        var list = this.Board.children;
        for(var i = 0;i<list.length;i++){
            var node = list[i];
            cc.Tween.stopAllByTarget(node);
            cc.tween(node)
                .to(0.34,{y:node.y-1100},{easing:cc.easing.quadIn})
                .start();
        }
        this.scheduleOnce(function(){
            callback();
        },0.6);
    },

    playBoardDropIn:function(callback){//新棋盘掉进屏幕
        var spring = function(t){
            return 1-Math.exp(-4.1*t)*Math.cos(18.5*t);
    };
        var RISE = 1100;
        var SPEED = 3235.29;
        var dropTime = RISE/SPEED;//下落时长
        var BOUNCE = 1;//弹反时长
        var list = this.Board.children;
        for(var i = 0;i<list.length;i++){
            var node = list[i];
            var y = node.y;
            node.y = y+RISE;
            cc.Tween.stopAllByTarget(node);
            cc.tween(node)
                .to(dropTime,{y:y-144},{easing:cc.easing.quadIn})
                .to(1,{y:y},{easing:spring})
                .to(0.1,{y:y})
                .start();
        }
        this.scheduleOnce(function(){
            callback();
        },dropTime+BOUNCE);
    },

    fusePosition:function(w,h){//引线末端(火花)在炸弹贴图里的位置
        //bomb1.png 原图 160x160,编辑器裁剪后内容区是 x 44~137 / y 59~157
        //fuseX,fuseY 是原图坐标(左上角为原点,y向下)
        var trimX = 44;
        var trimY = 59;
        var trimW = 93;
        var trimH = 98;
        var u = (this.fuseX-trimX)/trimW;
        //trim 区域内从底部算起的比例:引线在 y=70,trim 顶部 y=59,底部 y=157
        //引线距顶部 70-59=11px,距底部 98-11=87px,所以 v=87/98≈0.888(偏上)
        var v = (trimY+trimH-this.fuseY)/trimH;
        return cc.v2((u-0.5)*w,(v-0.5)*h);
    },

    addFire:function(bomb,size){
        var fire = new cc.Node('fire');
        fire.parent = bomb;
        fire.zIndex = 5;
        var fs = fire.addComponent(cc.Sprite);
        fs.spriteFrame = this.bombFireFrame;
        fs.sizeMode = cc.Sprite.SizeMode.CUSTOM;
        var fireSize = size*this.fireScale;
        if(fireSize<36){
            fireSize = 36;
        }
        fire.width = fireSize;
        fire.height = fireSize;
        var pos = this.fusePosition(size,size);
        fire.setPosition(pos.x,pos.y);
        fire.__t = 0;
        fire.scale = 0;
        fire.opacity = 255;
        fire.angle = 0;
    },

    stepFire:function(dt){
        //火花:先从小变大(这一段不变淡),快长到最大时才开始变淡消失,然后新的火花从零重新开始
        if(!this.bombFireFrame||!this.Board){
            return;
        }
        var CYCLE = 1.1;//一个火花从生到灭的周期
        var GROW_END = 0.8;//长到最大点的时间
        var FADE_START = 0.7;//开始变淡的时间(比最大点稍早一点)
        var FADE_END = 1.1;//完全消失的时间
        var list = this.Board.children;
        for(var i = 0;i<list.length;i++){
            var bomb = list[i].getChildByName('bomb');
            if(!bomb){
                continue;
            }
            var fire = bomb.getChildByName('fire');
            if(!fire){
                this.addFire(bomb,bomb.width);
                continue;
            }
            if(fire.__t===undefined){
                fire.__t = 0;
            }
            fire.__t = fire.__t+dt;
            if(fire.__t>=CYCLE){
                fire.__t = fire.__t-CYCLE;
            }
            var gp = fire.__t/GROW_END;//长大进度
            if(gp>1){
                gp = 1;
            }
            var e = 1-(1-gp)*(1-gp);//长大先快后慢
            fire.scale = e;
            fire.angle = -360*e;//顺势转一圈
            if(fire.__t<=FADE_START){
                fire.opacity = 255;//第一段只长大,不变淡
            }else{
                var fp = (fire.__t-FADE_START)/(FADE_END-FADE_START);//变淡进度
                if(fp>1){
                    fp = 1;
                }
                fire.opacity = Math.round(255*(1-fp));//第二段才变淡消失
            }
        }
    },

    addBomb:function(gem,pop){
        if(!this.bombFrame){
            return;
        }
        if(gem.getChildByName('bomb')){
            return;
        }
        var size = gem.height*2/3;
        var bomb = new cc.Node('bomb');
        bomb.parent = gem;
        bomb.zIndex = 2;
        var bs = bomb.addComponent(cc.Sprite);
        bs.spriteFrame = this.bombFrame;
        bs.sizeMode = cc.Sprite.SizeMode.CUSTOM;
        bomb.width = size;
        bomb.height = size;
        bomb.setPosition(5,-gem.height/2+size/2);
        if(pop){
            bomb.scale = 0.25;
            cc.tween(bomb)
                .to(0.18,{scale:1.18})
                .to(0.1,{scale:1})
                .start();
        }
        if(this.bombFireFrame){
            this.addFire(bomb,size);
        }
    },

    checkFire:function(){//场上带炸弹的棋子必须有火花,少了就补
        if(!this.bombFireFrame||!this.Board){
            return;
        }
        var list = this.Board.children;
        for(var i = 0;i<list.length;i++){
            var bomb = list[i].getChildByName('bomb');
            if(bomb&&!bomb.getChildByName('fire')){
                this.addFire(bomb,bomb.width);
            }
        }
    },

    playBoom:function(row,column){//炸弹爆炸特效
        if(!this.boomFrames||this.boomFrames.length===0){
            return;
        }
        var model = this.model;
        var size = model.STEP*this.boomSize*2;
        for(var i = 0;i<this.boomFrames.length;i++){
            var node = new cc.Node('boom');
            node.parent = this.Board;
            node.setPosition(model.cellX(column),model.cellY(row));
            node.zIndex = 20+i;
            var sp = node.addComponent(cc.Sprite);
            sp.spriteFrame = this.boomFrames[i];
            sp.sizeMode = cc.Sprite.SizeMode.CUSTOM;
            node.width = size;
            node.height = size;
            node.opacity = 185+i*35;
            node.scale = 0;
            cc.tween(node)
                .to(0.15,{scale:0.55},{easing:cc.easing.quadOut})
                .to(0.25,{scale:1},{easing:cc.easing.quadOut})
                .to(0.1,{scale:1.06,opacity:0})
                .call(function(){
                    node.destroy();
                })
                .start();
        }
    },

    collectBoomPush:function(row,column){//先记下冲击波要把哪些棋子推出去,推的动画等会拼进棋子的下落动画里
        var model = this.model;
        var cx = model.cellX(column);
        var cy = model.cellY(row);
        var reach = model.STEP*3.4;
        for(var r = row-2;r<=row+2;r++){
            for(var c = column-2;c<=column+2;c++){
                if(r<0||r>=model.ROW||c<0||c>=model.COL){
                    continue;
                }
                if(r===row&&c===column){
                    continue;
                }
                var gem = this.Board.getChildByName('gem_'+r+'_'+c);
                if(!gem){
                    gem = this.Board.getChildByName('boomgem_'+r+'_'+c);
                }
                if(!gem){
                    continue;
                }
                var dx = gem.x-cx;
                var dy = gem.y-cy;
                var d = Math.sqrt(dx*dx+dy*dy);
                if(d<1){
                    continue;
                }
                var far = 1-d/reach;
                if(far<0){
                    far = 0;
                }
                if(far>0.45){//紧挨炸弹那一圈别弹得太夸张,幅度和外面那圈差不多就好
                    far = 0.45;
                }
                if(gem.pushX===undefined){
                    gem.pushX = 0;
                    gem.pushY = 0;
                }
                gem.pushDone = false;
                gem.pushX = gem.pushX+dx/d*this.boomPush*far;
                gem.pushY = gem.pushY+dy/d*this.boomPush*far;
            }
        }
    },

    playBoomPush:function(row,column){//没有下落的那些棋子(还没走的),自己播弹出去再弹回来
        var model = this.model;
        var FLASH_LEAD = 0.12;//和爆炸火光同步
        var SHOCK_OUT = 0.18;
        var SHOCK_BACK = 0.28;
        for(var r = row-2;r<=row+2;r++){
            for(var c = column-2;c<=column+2;c++){
                if(r<0||r>=model.ROW||c<0||c>=model.COL){
                    continue;
                }
                var gem = this.Board.getChildByName('gem_'+r+'_'+c);
                if(!gem){
                    continue;//被打爆的棋子(boomgem)交给爆炸流程处理,这里跳过
                }
                if(gem.pushDone===true){
                    continue;
                }
                var px = gem.pushX||0;
                var py = gem.pushY||0;
                gem.pushX = 0;
                gem.pushY = 0;
                gem.pushDone = true;
                if(px===0&&py===0){
                    continue;
                }
                var bx = gem.x;
                var by = gem.y;
                cc.tween(gem)
                    .delay(FLASH_LEAD)
                    .to(SHOCK_OUT,{x:bx+px,y:by+py},{easing:cc.easing.quadOut})
                    .to(SHOCK_BACK,{x:bx,y:by},{easing:cc.easing.quadIn})
                    .start();
            }
        }
    },

    prepareGoalRolls:function(node){
        //把roll2从roll1里拆出来,再把两个roll放进同一个旋转容器goalSpin,
        //容器原点放在两个roll的公共圆心(整体包围盒中心),这样整体旋转时两个roll永远不散架
        var cover = node.getChildByName('transparent cover');
        var spin = node.getChildByName('goalSpin');
        if(spin){
            return {roll1:spin.getChildByName('roll1'),roll2:spin.getChildByName('roll2'),cover:cover,spin:spin};
        }
        var roll1 = node.getChildByName('roll1');
        var roll2 = roll1?roll1.getChildByName('roll2'):null;
        if(!roll1){
            return {roll1:null,roll2:null,cover:cover,spin:null};
        }
        if(roll2){//保持世界位置不变地把roll2从roll1里拆出来
            var wp = roll1.convertToWorldSpaceAR(roll2.position);
            roll2.parent = node;
            roll2.setPosition(node.convertToNodeSpaceAR(wp));
        }
        var p1 = cc.v2(roll1.x,roll1.y);//组装状态下两个roll相对goal节点的位置
        var p2 = roll2?cc.v2(roll2.x,roll2.y):cc.v2(roll1.x,roll1.y);
        //公共圆心:两个roll整体包围盒的中心
        var minX = 1e9,maxX = -1e9,minY = 1e9,maxY = -1e9;
        var list = [roll1,roll2];
        for(var i = 0;i<list.length;i++){
            var rr = list[i];
            if(!rr){
                continue;
            }
            var hw = rr.width/2;
            var hh = rr.height/2;
            if(rr.x-hw<minX)minX = rr.x-hw;
            if(rr.x+hw>maxX)maxX = rr.x+hw;
            if(rr.y-hh<minY)minY = rr.y-hh;
            if(rr.y+hh>maxY)maxY = rr.y+hh;
        }
        var px = (minX+maxX)/2;
        var py = (minY+maxY)/2;
        spin = new cc.Node('goalSpin');
        spin.parent = node;
        spin.setPosition(px,py);
        node.__pivot = cc.v2(px,py);
        node.__roll1Local = cc.v2(p1.x-px,p1.y-py);//组装态下roll在容器里的位置
        node.__roll2Local = cc.v2(p2.x-px,p2.y-py);
        if(roll2){
            roll2.parent = spin;
            roll2.setPosition(p2.x-px,p2.y-py);
        }
        roll1.parent = spin;
        roll1.setPosition(p1.x-px,p1.y-py);
        if(cover){//遮罩留在容器外面,不跟着转
            cover.setSiblingIndex(node.childrenCount-1);
        }
        return {roll1:roll1,roll2:roll2,cover:cover,spin:spin};
    },

    spinAssemblyForever:function(spin){//整体绕公共圆心逆时针旋转(angle正数=逆时针)
        if(!spin){
            return;
        }
        cc.Tween.stopAllByTarget(spin);
        cc.tween(spin)
            .repeatForever(
                cc.tween().by(2.0,{angle:360},{easing:cc.easing.linear})
            )
            .start();
    },

    goalRollsIdle:function(node){//goal宝石已经在棋格上:整体保持嵌套关系一直旋转
        var r = this.prepareGoalRolls(node);
        if(r.cover){
            r.cover.opacity = 255;
        }
        this.spinAssemblyForever(r.spin);
    },

    playGoalIntro:function(node,x,y){//goal宝石开场动画
        var r = this.prepareGoalRolls(node);
        var roll1 = r.roll1;
        var roll2 = r.roll2;
        var cover = r.cover;
        var spin = r.spin;
        if(!roll1||!spin){
            return 0;
        }
        var px = node.__pivot.x;
        var py = node.__pivot.y;
        var l1 = node.__roll1Local;//组装态下两个roll在容器里的位置
        var l2 = node.__roll2Local;
        var big = this.model.STEP*2/roll1.width;//出场时放大到"两个棋格的直径"
        var ccx = -x-px;//屏幕中心在容器坐标系里的位置
        var ccy = -y-py;
        var mx = cc.winSize.width*0.5+200;//屏宽/屏高一半再往外200,确保在屏幕外
        var my = cc.winSize.height*0.5+200;
        var out1 = cc.v2(-mx-x-px,my-y-py);//左上角以外
        var out2 = cc.v2( mx-x-px,my-y-py);//右上角以外
        var c1 = cc.v2(ccx+l1.x,ccy+l1.y);//飞到中心时的组装位置
        var c2 = cc.v2(ccx+l2.x,ccy+l2.y);
        var A_TIME = 0.55, HOLD = 0.08, B_TIME = 0.55;
        var total = A_TIME+HOLD+B_TIME;
        node.zIndex = 12;
        if(cover){
            cover.opacity = 0;
        }
        cc.Tween.stopAllByTarget(spin);
        spin.angle = 0;//飞行期间不转,落地后才开始转
        cc.Tween.stopAllByTarget(roll1);
        roll1.setPosition(out1.x,out1.y);
        roll1.scale = big;
        cc.tween(roll1)
            .to(A_TIME,{x:c1.x,y:c1.y},{easing:cc.easing.quadOut})
            .delay(HOLD)
            .to(B_TIME,{x:l1.x,y:l1.y,scale:1},{easing:cc.easing.quadIn})
            .start();
        if(roll2){
            cc.Tween.stopAllByTarget(roll2);
            roll2.setPosition(out2.x,out2.y);
            roll2.scale = big;
            cc.tween(roll2)
                .to(A_TIME,{x:c2.x,y:c2.y},{easing:cc.easing.quadOut})
                .delay(HOLD)
                .to(B_TIME,{x:l2.x,y:l2.y,scale:1},{easing:cc.easing.quadIn})
                .start();
        }
        var that = this;
        this.scheduleOnce(function(){//落到棋格后整个组装体开始旋转
            node.zIndex = 1;
            that.spinAssemblyForever(spin);
        },total);
        if(cover){//到位置时盖上透明遮罩
            this.scheduleOnce(function(){
                cc.tween(cover).to(0.2,{opacity:255}).start();
            },total);
        }
        return total;
    },

    showHint:function(r1,c1,r2,c2){//提示:两颗棋子一起左右摆动
        this.hintNodes = [];
        var a = this.Board.getChildByName('gem_'+r1+'_'+c1);
        var b = this.Board.getChildByName('gem_'+r2+'_'+c2);
        if(a){
            this.hintNodes.push(a);
        }
        if(b){
            this.hintNodes.push(b);
        }
        this.hintTime = 0;
    },

    hideHint:function(){
        for(var i = 0;i<this.hintNodes.length;i++){
            if(cc.isValid(this.hintNodes[i])){
                this.hintNodes[i].angle = 0;
            }
        }
        this.hintNodes = [];
        this.hintTime = 0;
    },

    update:function(dt){
        this.stepFire(dt);
        this.fireCheck = this.fireCheck+dt;
        if(this.fireCheck>0.5){
            this.fireCheck = 0;
            this.checkFire();
        }
        if(this.hintNodes.length===0){
            return;
        }
        this.hintTime = this.hintTime+dt;
        var a = Math.sin(this.hintTime*5)*30;
        for(var i = 0;i<this.hintNodes.length;i++){
            if(cc.isValid(this.hintNodes[i])){
                this.hintNodes[i].angle = a;
            }else{
                this.hintNodes = [];
                return;
            }
        }
    },

    showComboBanner:function(bonus){
        var node = new cc.Node('combo');
        node.parent = cc.find('Canvas/Page');
        node.setPosition(0,0);
        node.zIndex = 9;
        var label = node.addComponent(cc.Label);
        label.font = this.scoreFont;
        label.fontSize = 74;
        label.string = 'COMBO BONUS '+bonus;
        var upY = node.y+this.model.STEP*2;
        cc.tween(node)
            .to(1.4,{y:upY})
            .to(0.2,{y:upY,opacity:0})
            .call(function(){
                node.destroy();
            })
            .start();
    }
})
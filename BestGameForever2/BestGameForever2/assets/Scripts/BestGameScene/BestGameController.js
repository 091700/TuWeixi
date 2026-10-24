var BestGameView = require('./BestGameView');

window.BestGameController = cc.Class({
    extends:cc.Component,
    properties:{
        view:{ default:null,type:BestGameView }
    },
    onLoad:function(){
        this.model = new BestGameModel();
        this.view.model = this.model;
        window.EventBus.on('GamePause',this.onGamePause,this);
        window.EventBus.on('GameResume',this.onGameResume,this);
        window.EventBus.on('GameRestart',this.onGameRestart,this);
        this.pressCell = null;
        this.paused = false;
        this.hintTimer = 0;
        this.hintOn = false;
        this.hintCells = null;
        var board = cc.find('Canvas/Page/Board');
        if(board){
            this.touchboard(board);
        }
        this.view.setLevelLabel(this.model.getLevelText());
        this.view.updateTime(this.model.time);
        var best = parseInt(localStorage.getItem(this.model.bestKey ())||'0',10);
        this.view.updateScore(0,best);
        this.view.refresh();
        this.startLevelIntro();
        var that = this;
        window.cheatAddScore = function(bonus){
            that.doCheatScore(bonus);
        };
        window.cheatDropGoal = function(column){
            that.doCheatGoal(column);
        };

    },
    
    startOpening:function(){//开局进行一次消除
        var that = this;
        if(!this.isFirstLevel()&&this.model.hasMatch()){
            this.model.busy = true;
            var cleared =this.model.clearAndFall();
            this.view.playClearAnim(function(){
                that.view.refresh();
                that.updateScoreDisplay();
                that.model.busy = false;
                that.startPlay();
            });
        }else{
            this.model.busy = false;
            this.startPlay();
        }
    },

    isFirstLevel:function(){
        return this.model.world===1&&this.model.level===1;
    },

    startLevelIntro:function(){//显示Level
        var that = this;
        this.model.busy = true;
        this.view.showStartLabel(this.model.getStartLabelText(),function(){
            that.model.busy = false;
            if(that.isFirstLevel()){
                that.startTodo(1);
            }else{
                that.startOpening();
            }
        });
    },

    onGameRestart:function(){//重开
        var that = this;
        this.view.unscheduleAllCallbacks();
        this.view.hideStartLabel();
        this.paused = false;
        this._winDone = false;
        this.resetHint();
        this.view.resumeHand();
        this.view.resumeBoard();
        this.view.hideTodo();
        this.model.busy = true;
        this.view.playBoardDropOut(function(){
            that.model = new BestGameModel();
            that.model.busy = true;
            that.view.model = that.model;
            that.view.refresh();
            that.view.setLevelLabel(that.model.getLevelText());
            that.view.updateTime(that.model.time);
            var best = parseInt(localStorage.getItem(that.model.bestKey())||'0',10);
            that.view.updateScore(0,best);
            that.view.playBoardDropIn(function(){
                that.startLevelIntro();
            });
        });
    },

    updateScoreDisplay:function(){
        var model =this.model;
        var best = parseInt(localStorage.getItem(model.bestKey())||'0',10);
        if(model.score>best){
            localStorage.setItem(model.bestKey(),model.score+'');
            best = model.score;
        }
        this.view.updateScore(model.score,best);
    },

    touchboard:function(node){//棋子拖动交换
        var that = this;
        node.on('touchstart',function(e){
            if(that.model.busy)return;   //正在处理,别连点
            var pos = node.convertToNodeSpaceAR(e.getLocation());
            that.pressCell = that.posToCell(pos);
        },node,true);
        node.on('touchmove',function(e){
            if(!that.pressCell)return;
            if(that.model.busy)return;
            var pos = node.convertToNodeSpaceAR(e.getLocation());
            var cell = that.posToCell(pos);
            if(!cell)return;//拖到相邻格子交换
            var dr = Math.abs(cell.r-that.pressCell.r);
            var dc = Math.abs(cell.c-that.pressCell.c);
            if(dr + dc === 1){
                var a = that.pressCell;
                that.pressCell = null;
                that.doChange(a.r,a.c,cell.r,cell.c);
            }
        },node,true);
        node.on('touchend',function(){
            that.pressCell = null;
        },node,true);
    },

    posToCell:function(pos){
        var col = Math.round(pos.x/this.model.STEP) + 3;
        var row = Math.round((this.model.TOP_Y - pos.y)/this.model.STEP);
        if(col<0||col>=this.model.COL)return null;
        if(row<0||row>=this.model.ROW)return null;
        if(this.model.board[row][col].gem==='')return null;
        return {r:row,c:col};
    },

    //交换棋子
    doChange:function(r1,c1,r2,c2){
        var model = this.model;
        var view = this.view;
        model.busy = true;//动画期间防止玩家多次点击
        var that = this;
        this.scheduleOnce(function(){//防止动画卡死
            model.busy = false;
        },0.3);
        view.playChangeAnim(r1,c1,r2,c2,function(){
            if(model.tryChange(r1,c1,r2,c2)){
                that.resetHint();
                var cleared = model.clearAndFall(r2,c2);
                that.updateScoreDisplay();//消失的瞬间就刷新分数
                if (cleared>0&&(model.state==='todo1'||model.state==='todo2')){
                view. hideTodo (); //教程消失
                }
            view.playClearAnim(function(){
                that.refreshBoard(cleared);
            });    
            model.busy = false;  
        }else{
            view.playChangeAnim(r1,c1,r2,c2,function(){//消除失败，划回来
                that.refreshBoard(0);
                model.busy = false;
            });
            model.busy = false;
        }}
    );
    },

    refreshBoard:function(cleared){//刷新棋盘
        var model = this.model;
        this.view.refresh();
        this.updateScoreDisplay();
        if(cleared>0){
            this.resetHint();
            if(model.state==='todo1'){
                this.startTodo(2);
                return;
            }
            if(model.state==='todo2'){
                this.startPlay();
                return;
            }
        }else if(this.hintOn){
            this.view.showHint(this.hintCells[0],this.hintCells[1],this.hintCells[2],this.hintCells[3]);
        }
        if(model.state==='playing'&&model.allDisabled()){
            if(!model.goalSpawned){
                model.spawnGoal();
            }
            this.startTodo(3);
            return;
        }
        if(model.goalSpawned&&model.goalAtBottom()&&!this._winDone){
            this._winDone = true;
            model.state='win';
            window.lastLevelScore = model.score;//存通关时间分数
            window.lastTimeBonus = model.getTimeBonus();
            this.scheduleOnce(this.finishLevel,0.6);
            return;
        }
        if((model.state==='playing'||model.goalSpawned)&&!model.hasMove()){
            this.doNoMoves();
        }
    },

    finishLevel:function(){//糖果掉到底了,去结算界面
        window.noSlide = false;
        cc.director.loadScene('WinScene');
    },

    resetHint:function(){
        this.hintTimer = 0;
        this.hintOn = false;
        this.hintCells = null;
        this.view.hideHint();
    },

    updateHint:function(dt){
        if(this.hintOn){
            return;
        }
        this.hintTimer = this.hintTimer+dt;
        if(this.hintTimer<7){
            return;
        }
        var move = this.model.findMove();
        if(!move){
            return;
        }
        this.hintCells = move;
        this.hintOn = true;
        this.view.showHint(move[0],move[1],move[2],move[3]);
    },

    doNoMoves:function(){//没有可以消的一步了,提示后重新洗位置
        var that = this;
        var model = this.model;
        model.busy = true;
        this.resetHint();
        this.view.showNotice('NO MOVES',0.9,function(){
            that.view.showNotice('REFRESHING',0.9,function(){
                model.shuffleBoard();
                that.view.playShuffle(function(){
                    model.busy = false;
                });
            });
        });
    },

    //教程，
    startTodo:function(num){
        var view = this.view;
        if(num === 1){
            this.model.state = 'todo1';
            view.refresh(); 
            view.showTodo(view.tip1Prefab,1,3,1,4);
        }else if(num === 2){
            this.model.state = 'todo2';
            view.refresh();
            view.showTodo(view.tip2Prefab,6,2,6,3); 
        }else{
            this.model.state = 'win';
            view.showTodo(view.tip3Prefab,-1,-1,-1,-1);
            this.bindConfirm();
        }
    },

    //教程二结束开始计时
    startPlay:function(){
        this.model.state = 'playing';
        this.model.time = this.model.TOTAL_TIME;
        this.view.updateTime(this.model.time);
        if(!this.model.hasMove()){
            this.doNoMoves();
        }
    },

    //教程3的确认按钮
    //Tip3结构:Tip3→Tip3Backet→[Tip3Label,OkBtn],先找Backet再找OkBtn
    bindConfirm:function(){
        var that = this;
        var tip = this.view.tipNode;
        if(!tip)return;
        var backet = tip.getChildByName('Tip3Backet');
        if(!backet){
            cc.log('Tip3里没有Tip3Backet节点');
            return;
        }
        var confirmBtn = backet.getChildByName('OkBtn');
        if(!confirmBtn){
            cc.log('Tip3Backet里没有OkBtn节点');
            return;
        }
        confirmBtn.on('click',function(){
            //存档解锁当前关卡
            var world = parseInt(localStorage.getItem('currentWorld')||'1',10);
            var key = 'wave_' + world + '_bestLevel';
            localStorage.setItem(key,'1');
            that.view.hideTodo();
        },confirmBtn);
    },

    onGamePause:function(){//暂停:冻结棋盘动画和连锁,停住时间
        this.paused = true;
        this.view.pauseHand();
        this.view.pauseBoard();
    },

    onGameResume:function(){//继续:恢复棋盘动画和连锁,恢复时间
        this.paused = false;
        this.view.resumeHand();
        this.view.resumeBoard();
    },

    update:function(dt){//计时
        var model = this.model;
        if(model.state!=='playing')return;
        if(this.paused)return;//暂停时不走时间

        model.time = model.time - dt;
        if(model.time<=0){
            model.time = 0;
            window.noSlide = false;
            cc.director.loadScene('DefeatScene');
            return;
        }
        this.view.updateTime(model.time);
        if(!model.busy){
            this.updateHint(dt);
        }
    },

    doCheatScore:function(bonus){//单击消除
        var model = this.model;
        this.view.hideTodo();//清教程
        model.score = model.score+bonus;
        this.updateScoreDisplay();
    },

    doCheatGoal:function(column){//双击按钮弹goal宝石
        var model = this.model;
        var view = this.view;
        this.view.hideTodo();
        this._winDone = true;
        if(column<0){
            column = Math.floor(Math.random()*model.COL);
        }
        if(view.goalNode&&cc.isValid(view.goalNode)){
            view.goalNode.destroy();//上一颗还没消就换一颗
        }
        view.goalNode = cc.instantiate(view.goalGemPrefab);
        view.goalNode.parent = view.Board;
        view.goalNode.setPosition(model.cellX(column),model.TOP_Y+300);
        var columnRows = model.colRows[column];
        var lastRow = columnRows[columnRows.length-1];
        cc.tween(view.goalNode)
            .to(0.85,{y:model.cellY(lastRow)},{easing:cc.easing.quadIn})
            .to(0.12,{y:model.cellY(lastRow)-14},{easing:cc.easing.quadOut})
            .to(0.12,{y:model.cellY(lastRow)+8},{easing:cc.easing.quadIn})
            .to(0.12,{y:model.cellY(lastRow)},{easing:cc.easing.quadOut})
            .start();
        this.unschedule(this.finishCheatGoal);
        this.scheduleOnce(this.finishCheatGoal,1.6);
                },

    finishCheatGoal:function(){
        var model = this.model;
        model.state = 'win';
        window.lastLevelScore = model.score;
        window.lastTimeBonus = model.getTimeBonus();
        cc.director.loadScene('WinScene');
    },

    onDestroy:function(){
        window.EventBus.targetOff(this);
        window.cheatAddScore = null;
        window.cheatDropGoal = null;
    }
})
//先加载View,否则properties的type报BestGameView not defined
var BestGameView = require('./BestGameView');

window.BestGameController = cc.Class({
    extends:cc.Component,
    //控制层:收输入,指挥Model算、View画

    properties:{
        view:{ default:null,type:BestGameView }  //挂View的节点
    },

    onLoad:function(){
        //造模型交给View
        this.model = new BestGameModel();
        this.view.model = this.model;

        //监听胜利消息(GoalGem落地时View会发)
        window.EventBus.on('GameWin',this.onGameWin,this);

        //触摸绑在棋盘容器Board上:命中宝石会冒泡到Board,不需要给Board设尺寸
        this.pressCell = null;                       //手指按下时的格子
        var board = cc.find('Canvas/Page/Board');
        if(board){
            this.bindBoard(board);
        }
        this.starttodorial(1);//显示教程一，初始化时间分数
        this.view.updateTime(this.model.time);
        var best = parseInt(localStorage.getItem('bestScore')||'0',10);
        this.view.updateScore(0,best);
    },

    //把触摸绑到棋盘容器上:捕获阶段(true)保证命中宝石时Board也能先收到
    bindBoard:function(node){
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
            if(!cell)return;
            //拖到相邻格就交换(上下左右,坐标差相加=1)
            var dr = Math.abs(cell.r-that.pressCell.r);
            var dc = Math.abs(cell.c-that.pressCell.c);
            if(dr + dc === 1){
                var a = that.pressCell;
                that.pressCell = null;   //清掉,防重复触发
                that.doChange(a.r,a.c,cell.r,cell.c);
            }
        },node,true);

        node.on('touchend',function(){
            that.pressCell = null;
        },node,true);
    },

    //像素坐标→棋盘格子(和cellX/cellY互逆),点界外返回null
    posToCell:function(pos){
        var col = Math.round(pos.x/this.model.STEP) + 3;
        var row = Math.round((this.model.TOP_Y - pos.y)/this.model.STEP);
        if(col<0||col>=this.model.COL)return null;
        if(row<0||row>=this.model.ROW)return null;
        return {r:row,c:col};
    },

    //交换棋子
    doChange:function(r1,c1,r2,c2){
        var model = this.model;
        var view = this.view;
        model.busy = true;//动画期间防止玩家多次点击
        var that = this;
        view.playChangeAnim(r1,c1,r2,c2,function(){
            if(model.tryChange(r1,c1,r2,c2)){
                var cleared = model.clearAndFall();
                model.score = model.score + cleared*10;
            
            view.playClearAnim(function(){
                that.refreshBoard(cleared);
            model.busy = false;
            });      
        }else{
            //如果没消除，两颗棋子划回来
            view.playChangeAnim(r1,c1,r2,c2,function(){
                that.refreshBoard(0);
                model.busy = false;
            });
        }}
    );
    },

    //棋盘变了的统一处理:刷新分数+推进教程+胜利判断
    //cleared>0=真的消掉了;cleared=0=无效交换(不推教程)
    refreshBoard:function(cleared){
        var model = this.model;
        this.view.refresh();      //重画棋盘

        //保存最高分
        var best = parseInt(localStorage.getItem('bestScore')||'0',10);
        if(model.score>best){
            localStorage.setItem('bestScore',model.score+'');
            best = model.score;
        }
        this.view.updateScore(model.score,best);

        //只有真消除才推进教程,无效交换不跳下一步
        if(cleared>0){
            if(model.state==='todo1'){              //教程1完成→教程2(棋盘不动)
                this.view.hidetodorial();
                this.starttodorial(2);
                return;
            }
            if(model.state==='todo2'){              //教程2完成→正式开始(重新随机棋盘)
                this.view.hidetodorial();
                this.startPlay();
                return;
            }
        }
        //正式游戏:所有背景都降到disabled→胜利,掉GoalGem
        if(model.state==='playing'&&model.allDisabled()){
            model.state='win';
            this.view.showGoalGem();
        }
    },

    //教程流程:两个教程共用一个棋盘,切教程棋盘不动,只切换提示和手指
    starttodorial:function(num){
        var view = this.view;
        if(num === 1){
            this.model.state = 'todo1';
            view.refresh();                                    //开局画一次棋盘(固定棋已全在)
            view.showtodorial(view.tip1Prefab,1,3,1,4);        //手指在黄(r1c3)和绿3(r1c4)之间
        }else if(num === 2){
            this.model.state = 'todo2';
            view.refresh();                                    //棋盘保持教程1消完的样子,只重画(棋不变)
            view.showtodorial(view.tip2Prefab,6,2,6,3);        //手指在白(r6c2)和紫2(r6c3)之间
        }else{
            //教程3:胜利说明弹窗,没有手指,等玩家点确认
            this.model.state = 'win';
            view.showtodorial(view.tip3Prefab,-1,-1,-1,-1);
            this.bindConfirm();
        }
    },

    //教程二结束开始计时
    startPlay:function(){
        this.model.state = 'playing';
        this.model.time = this.model.TOTAL_TIME;
        this.view.updateTime(this.model.time);
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

            that.view.hidetodorial();
            cc.director.loadScene('WaveSelectScene');
        },confirmBtn);
    },

    //收到GameWin→弹第三个教程
    onGameWin:function(){
        if(this._winDone)return;   //防止重复弹
        this._winDone = true;
        this.starttodorial(3);
    },

    //计时:只有正式游戏才扣时间,教程阶段不扣
    update:function(dt){
        var model = this.model;
        if(model.state!=='playing')return;

        model.time = model.time - dt;
        if(model.time<=0){
            model.time = 0;
            cc.director.loadScene('WaveSelectScene');  //超时先简单处理:回选关
            return;
        }
        this.view.updateTime(model.time);
    },

    onDestroy:function(){
        window.EventBus.targetOff(this);   //离开场景清理监听
    }
})
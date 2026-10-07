window.BestGameModel = cc.Class({
    ctor:function(){
        this.COL = 7;//列
        this.ROW = 9;//行
        this.STEP = 92.43;
        this.TOP_Y = 407;//最顶上一格中心坐标
        this.TOTAL_TIME = 420;
        this.STAR_COLOR = ['blue','green','purple','red','white','yellow'];
        this.state = 'todo1';//教程
        this.score = 0;
        this.time = 420;
        this.board = [];
        this.busy = false;
        this.initTodoAll();
        this.busy = false;
        this.steps = [];
    },

    cellX:function(col){//第几列坐标
        return (col-3)*this.STEP;
    },
    cellY:function(row){
        return this.TOP_Y - row * this.STEP;
    },

    makeBoard:function(){
        this.board = [];
        for(var r = 0;r<this.ROW;r++){
            this.board.push([]);
            for(var c = 0;c<this.COL;c++){
                this.board[r].push({gem:'',level:3});
            }
        }
    },

    setGem:function(r,c,name){
        this.board[r][c].gem = name;
    },

    initTodoAll:function(){//教程
        this.makeBoard();
        //教程1固定棋子
        this.setGem(1,1,'green');
        this.setGem(1,2,'green');
        this.setGem(1,3,'yellow');
        this.setGem(1,4,'green');
        //教程2固定棋子
        this.setGem(5,2,'purple');
        this.setGem(6,2,'white');
        this.setGem(6,3,'purple');
        this.setGem(7,2,'purple');
        this.fillEmptyRandom();
        while(this.hasMatch()){
            this.fillEmptyRandom();
        }
    },

    //正式棋盘
    initRandom:function(){//随机生成棋子,并保证无三连
        this.makeBoard();
        this.fillEmptyRandom();
        while(this.hasMatch()){
            this.fillEmptyRandom();
        }
    },

    //填充空格子:填的时候检查左边两个、上边两个,避免填出三连(防死循环)
    fillEmptyRandom:function(){
        for(var r = 0;r<this.ROW;r++){
            for(var c = 0;c<this.COL;c++){
                var cell = this.board[r][c];
                if(cell.gem !== '')continue;   // 固定格子不覆盖
                var pick = [];
                for(var i = 0;i<this.STAR_COLOR.length;i++){
                    var color = this.STAR_COLOR[i];
                    //水平:左边两格同色就跳过这个颜色
                    if(c >= 2 && this.board[r][c-1].gem === color && this.board[r][c-2].gem === color){
                        continue;
                    }
                    //垂直:上边两格同色就跳过
                    if(r >= 2 && this.board[r-1][c].gem === color && this.board[r-2][c].gem === color){
                        continue;
                    }
                    pick.push(color);
                }
                if(pick.length === 0){//极端情况:全被排除,随便选一个兜底
                    pick = this.STAR_COLOR.slice();
                }
                var idx = Math.floor(Math.random() * pick.length);
                cell.gem = pick[idx];
            }
        }
    },

    //规则判断:检查是否有三连
    hasMatch:function(){
        for(var r = 0;r<this.ROW;r++){
            for(var c = 0;c<this.COL;c++){
                var g = this.board[r][c].gem;
                if(g === '')continue;              // 空格跳过
                if(c+2 < this.COL && this.board[r][c+1].gem===g && this.board[r][c+2].gem===g){
                    return true;                   // 横向三连
                }
                if(r+2 < this.ROW && this.board[r+1][c].gem===g && this.board[r+2][c].gem===g){
                    return true;                   // 纵向三连
                }
            }
        }
        return false;
    },

    //把三连格子收集成list(可能重复,不影响)
    collectMatches:function(){
        var list = [];
        for(var r = 0;r<this.ROW;r++){
            for(var c = 0;c<this.COL;c++){
                var g = this.board[r][c].gem;
                if(g === '')continue;
                if(c+2 < this.COL && this.board[r][c+1].gem===g && this.board[r][c+2].gem===g){
                    list.push([r,c]);list.push([r,c+1]);list.push([r,c+2]);
                }
                if(r+2 < this.ROW && this.board[r+1][c].gem===g && this.board[r+2][c].gem===g){
                    list.push([r,c]);list.push([r+1,c]);list.push([r+2,c]);
                }
            }
        }
        return list;
    },

    //消除下落，背景降级，返回消除的总数
    clearAndFall:function(){
        var totalCleared = 0;
        this.steps = [];
        for(;;){//有连锁反应循环
            var list = this.collectMatches();
            if(list.length===0)break;//没有三连了就结束
            totalCleared = totalCleared + list.length;
            var step = {cleared:[],falls:[]};//宝石分为消除的和掉落的
            //清空宝石，背景降一级
            for(var i = 0;i<list.length;i++){
                var r = list[i][0];
                var c = list[i][1];
                var cell = this.board[r][c];
                cell.gem = '';
                if(cell.level > 0){
                    cell.level--;
                }
                var already = false;
                for(var k = 0;k<step.cleared.length;k++){
                    if(step.cleared[k][0]===r&&step.cleared[k][1]===c){
                        already = true;
                        break;
                    }

                }
                if(already===false){
                    step.cleared.push([r,c]);
                }
            }

            //棋子下落
            for(var col = 0;col<this.COL;col++){
                for(var row = this.ROW-1;row>=0;row--){
                    var cell2 = this.board[row][col];
                    if(cell2.gem!=='')continue;//有宝石就不管
                    //找上方最近的宝石掉下来
                    for(var up = row-1;up>=0;up--){
                        var cellUp = this.board[up][col];
                        if(cellUp.gem === '')continue;
                        cell2.gem = cellUp.gem;
                        cellUp.gem = '';
                        step.falls.push({c:col,fromR:up,toR:row,gem:cell2.gem})
                        break;
                    }
                    //上方没有了就随机生成一颗
                    if(cell2.gem === ''){
                        var index = Math.floor(Math.random()*6);
                        cell2.gem = this.STAR_COLOR[index];
                        step.falls.push({c:col,fromR:-1,toR:row,gem:cell2.gem});
                    }
                }
            }this.steps.push(step);
        }
        return totalCleared;
    },

    //交换:有匹配就保留返回true;没匹配就换回去返回false
    tryChange:function(r1,c1,r2,c2){
        var a = this.board[r1][c1];
        var b = this.board[r2][c2];
        var temp = a.gem;
        a.gem = b.gem;
        b.gem = temp;
        if(this.hasMatch()){
            return true;
        }
        temp = a.gem;
        a.gem = b.gem;
        b.gem = temp;
        return false;
    },

    //胜利判断:所有背景都降到0(cell_disabled)即胜利
    allDisabled:function(){
        for(var r = 0;r<this.ROW;r++){
            for(var c = 0;c<this.COL;c++){
                if(this.board[r][c].level > 0){
                    return false;
                }
            }
        }
        return true;
    }
})
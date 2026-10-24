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
        this.steps = [];
        this.comboCount = 0;//连击数
        this.lastClearTime = 0;//上一次消除的时间
        this.COMBO_WINDOW =3;//连击时间
        this.world = window.CurrentWorld||1;
        this.level = window.CurrentLevel||1;
        this.levelData = window.LevelData.get(this.world,this.level);
        this.TOTAL_TIME = this.levelData.time;
        this.time = this.TOTAL_TIME;
        this.noMatch = (this.world===1&&this.level===1);//防止第一关出现三连
        this.goalColumn = 3;//最后一颗被消除的背景所在的列,goalgem就生成在这一列
        this.goalSpawned = false;
        this.goalPending = false;
        if(this.world===1&&this.level===1){
            this.initTodoAll();
        }else{
            this.initRandom();
        }
    },

    cellX:function(col){//第几列坐标
        return (col-3)*this.STEP;
    },
    cellY:function(row){
        return this.TOP_Y - row * this.STEP;
    },

    getLevelText:function(){
        var roman = ['','I','II','III','IV','V'];
        return roman[this.world]+'-'+this.level;
    },

    getStartLabelText:function(){
        return'LEVEL '+this.getLevelText();
    },

    goalCell:function(){//goal宝石现在在哪一格
        for(var r = 0;r<this.ROW;r++){
            for(var c = 0;c<this.COL;c++){
                if(this.board[r][c].gem==='goal'){
                    return [r,c];
                }
            }
        }
        return null;
    },

    spawnGoal:function(){//背景全消完之后,goal宝石落在这一列最上面那一格
        var rows = this.colRows[this.goalColumn];
        var row = rows[0];
        this.board[row][this.goalColumn].gem = 'goal';
        this.board[row][this.goalColumn].bomb = false;
        this.goalSpawned = true;
    },

    goalAtBottom:function(){//goal宝石掉到这一列最底下一格就算通关
        var cell = this.goalCell();
        if(!cell){
            return false;
        }
        var rows = this.colRows[cell[1]];
        return cell[0]===rows[rows.length-1];
    },

    makeBoard:function(){
        this.board = [];
        this.colRows = [];
        var map = this.levelData.map;
        for(var c = 0;c<this.COL;c++){
            this.colRows.push([]);
        }
        for(var r = 0;r<this.ROW;r++){
            this.board.push([]);
            for(var c = 0;c<this.COL;c++){
                if(map[r].charAt(c)==='-'){
                    this.board[r].push({gem:'',level:-1,bomb:false});
                }else{
                    this.board[r].push({gem:'',level:parseInt(map[r].charAt(c),10),bomb:false});
                    this.colRows[c].push(r);
                }
            }
        }
        var best = -1;
        for(var c2 = 0;c2<this.COL;c2++){
            if(this.colRows[c2].length>0&&(best<0||this.colRows[c2].length>this.colRows[best].length)){
                best = c2;
            }
        }
        this.goalColumn = best;
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
        var guard = 0;
        while(this.hasMatch()&&guard<30){
            this.fillEmptyRandom();
            guard = guard+1;
        }
    },

    initRandom:function(){//随机生成棋子,并保证无三连
        this.makeBoard();
        this.fillEmptyRandom();
        var guard = 0;
        while(this.noMatch&&this.hasMatch()&&guard<30){
            this.fillEmptyRandom();
            guard = guard+1;
        }
    },

    //填充空格子
    fillEmptyRandom:function(){
        for(var r = 0;r<this.ROW;r++){
            for(var c = 0;c<this.COL;c++){
                var cell = this.board[r][c];
                if(cell.level===-1)continue;//空洞里不放棋子
                if(cell.gem !== '')continue;//固定的格子
                var pick = [];
                for(var i = 0;i<this.STAR_COLOR.length;i++){
                    var color = this.STAR_COLOR[i];//防止垂直相同
                    if(this.noMatch){
                    if(c>= 2&&this.board[r][c-1].gem===color&&this.board[r][c-2].gem===color){
                        continue;
                    }
                    if(r>= 2&&this.board[r-1][c].gem===color&&this.board[r-2][c].gem===color){
                        continue;
                    }}//防止水平相同
                    pick.push(color);
                }
                var idx = Math.floor(Math.random()*pick.length);
                cell.gem = pick[idx];
            }
        }
    },

    hasMatch:function(){//检查是否有三连
        for(var r = 0;r<this.ROW;r++){
            for(var c = 0;c<this.COL;c++){
                var g = this.board[r][c].gem;
                if(g==='')continue;//跳过空格
                if(c+2 < this.COL && this.board[r][c+1].gem===g && this.board[r][c+2].gem===g){
                    return true;//横向
                }
                if(r+2 < this.ROW && this.board[r+1][c].gem===g && this.board[r+2][c].gem===g){
                    return true;//纵向
                }
            }
        }
        return false;
    },

    collectGroups:function(){//把三连及以上的每一组收成list
        var groups = [];
        for(var r = 0;r<this.ROW;r++){
            var run = 1;
            for(var c = 1;c<=this.COL;c++){//横向
                var same = false;
                if(c<this.COL){
                    same = this.board[r][c].gem!==''&&this.board[r][c].gem===this.board[r][c-1].gem;
                }
                if(same){
                    run = run+1;
                }else{
                    if(run>=3){
                        var cells = [];
                        for(var k = c-run;k<c;k++){
                            cells.push([r,k]);
                        }
                        groups.push({cells:cells});
                    }
                    run = 1;
                }
            }
        }
        for(var c2 = 0;c2<this.COL;c2++){//纵向
            var run2 = 1;
            for(var r2 = 1;r2<=this.ROW;r2++){
                var same2 = false;
                if(r2<this.ROW){
                    same2 = this.board[r2][c2].gem!==''&&this.board[r2][c2].gem===this.board[r2-1][c2].gem;
                }
                if(same2){
                    run2 = run2+1;
                }else{
                    if(run2>=3){
                        var cells2 = [];
                        for(var k2 = r2-run2;k2<r2;k2++){
                            cells2.push([k2,c2]);
                        }
                        groups.push({cells:cells2});
                    }
                    run2 = 1;
                }
            }
        }
        return groups;
    },

    downCell:function(r,c,step,downed){
        if(downed[r][c]===1){
            return;
        }
        downed[r][c] = 1;
        var cell = this.board[r][c];
        if(cell.level>0){
            cell.level--;
            step.downs.push({row:r,column:c,level:cell.level});//记录背景降级后的等级
            if(cell.level===0){
                this.goalColumn = c;
            }
        }
    },

    pickBombCell:function(group,prefRow,prefColumn){
        var mid = group.cells[Math.floor(group.cells.length/2)];
        if(this.board[mid[0]][mid[1]].bomb!==true){
            return mid;
        }
        if(prefRow>=0){
            var best = null;
            var bestD = 0;
            for(var i = 0;i<group.cells.length;i++){
                var cell = group.cells[i];
                if(this.board[cell[0]][cell[1]].bomb===true){
                    continue;
                }
                var dr = cell[0]-prefRow;
                var dc = cell[1]-prefColumn;
                var d = dr*dr+dc*dc;
                if(best===null||d<bestD){
                    best = cell;
                    bestD = d;
                }
            }
            if(best){
                return best;
            }
        }
        for(var j = 0;j<group.cells.length;j++){
            if(this.board[group.cells[j][0]][group.cells[j][1]].bomb!==true){
                return group.cells[j];
            }
        }
        return mid;
    },

    pushBackgroundCell:function(mark,queue,skip){
        var list = [];
        for(var r = 0;r<this.ROW;r++){
            for(var c = 0;c<this.COL;c++){
                if(mark[r][c]!==0){
                    continue;
                }
                if(this.board[r][c].gem===''){
                    continue;
                }
                if(this.board[r][c].level<=0){
                    continue;
                }
                if(this.board[r][c].gem==='goal'){
                    continue;
                }
                if(skip&&skip[0]===r&&skip[1]===c){
                    continue;
                }
                list.push([r,c]);
            }
        }
        if(list.length===0){
            var goal = this.goalCell();//场上没有带背景的棋子了,就消goal宝石下面那一颗
            if(goal){
                var gr = goal[0]+1;
                var gc = goal[1];
                if(gr<this.ROW&&mark[gr][gc]===0&&this.board[gr][gc].gem!==''&&this.board[gr][gc].gem!=='goal'){
                    mark[gr][gc] = 1;
                    queue.push([gr,gc]);
                }
            }
            return;
        }
        var pick = list[Math.floor(Math.random()*list.length)];
        mark[pick[0]][pick[1]] = 1;
        queue.push(pick);
    },

    clearAndFall:function(prefRow,prefColumn){//棋子消除，填充空白，连锁反应，记录得分动作，返回总共消除了多少棋子
        var now = cc.director.getTotalTime()/1000;
        if(now-this.lastClearTime>this.COMBO_WINDOW){
            this.comboCount = 0;
        }//超过三秒连击清零
        this.lastClearTime =now;
        var totalCleared = 0;
        this.steps = [];
        if(prefRow===undefined){
            prefRow = -1;
        }
        if(prefColumn===undefined){
            prefColumn = -1;
        }
        var waveIndex = 0;//第几次消除
        for(;;){//有连锁反应循环
            var groups = this.collectGroups();
            if(groups.length===0)
                break;//没有三连了就结束
            waveIndex = waveIndex+1;//判断waveinde大于一连锁反应就加奖励分
            this.comboCount = this.comboCount+1;//三秒内连续快速消除加分
            var perGem = 10*(this.comboCount+groups.length-1);//每颗棋子的得分
            var bonus = 0;
            if(waveIndex>1){
                bonus = 100*(waveIndex-1)*groups.length;//连锁消除得分
            }
            var step = {cleared:[],falls:[],downs:[],bombs:[],booms:[],perGem:perGem,bonus:bonus,points:0};//宝石分为消除的和掉落的
            var mark = [];
            var downed = [];
            for(var r0 = 0;r0<this.ROW;r0++){
                mark.push([]);
                downed.push([]);
                for(var c0 = 0;c0<this.COL;c0++){
                    mark[r0].push(0);
                    downed[r0].push(0);
                }
            }
            var queue = [];
            //清空宝石，背景降一级
            for(var i = 0;i<groups.length;i++){
                var group = groups[i];
                var bombCell = null;
                if(group.cells.length>=4){
                    bombCell = this.pickBombCell(group,prefRow,prefColumn);
                    mark[bombCell[0]][bombCell[1]] = 2;
                    step.bombs.push({row:bombCell[0],column:bombCell[1],gem:this.board[bombCell[0]][bombCell[1]].gem});
                }
                for(var j = 0;j<group.cells.length;j++){
                    var r = group.cells[j][0];
                    var c = group.cells[j][1];
                    this.downCell(r,c,step,downed);
                    if(mark[r][c]===0){
                        mark[r][c] = 1;
                        queue.push([r,c]);
                    }
                }
                if(bombCell){
                    this.pushBackgroundCell(mark,queue,bombCell);
                }
            }
            var qi = 0;
            while(qi<queue.length){
                var cur = queue[qi];
                qi = qi+1;
                if(mark[cur[0]][cur[1]]===2){
                    continue;
                }
                if(this.board[cur[0]][cur[1]].bomb!==true){
                    continue;
                }
                step.booms.push({row:cur[0],column:cur[1]});
                for(var dr = -1;dr<=1;dr++){
                    for(var dc = -1;dc<=1;dc++){
                        var br = cur[0]+dr;
                        var bc = cur[1]+dc;
                        if(br<0||br>=this.ROW||bc<0||bc>=this.COL){
                            continue;
                        }
                        if(this.board[br][bc].gem==='goal'){
                            continue;//goal宝石炸不掉
                        }
                        if(mark[br][bc]===0){
                            mark[br][bc] = 1;
                            queue.push([br,bc]);
                        }
                    }
                }
                this.pushBackgroundCell(mark,queue,null);
            }
            for(var q1 = 0;q1<queue.length;q1++){
                this.downCell(queue[q1][0],queue[q1][1],step,downed);
            }
            for(var q2 = 0;q2<queue.length;q2++){
                var cr = queue[q2][0];
                var cq = queue[q2][1];
                if(mark[cr][cq]===2){
                    continue;
                }
                this.board[cr][cq].gem = '';
                this.board[cr][cq].bomb = false;
                step.cleared.push([cr,cq]);
            }
            for(var b2 = 0;b2<step.bombs.length;b2++){
                this.board[step.bombs[b2].row][step.bombs[b2].column].bomb = true;
            }
            totalCleared = totalCleared + step.cleared.length;

            if(!this.goalSpawned&&!this.goalPending&&this.allDisabled()){
                this.goalPending = true;//背景全消完了,goal宝石这一波跟着新棋子一起生出来
            }

            //棋子下落
            for(var col = 0;col<this.COL;col++){
                var colRowList = this.colRows[col];
                var newCount = 0;
                var topSpawn = -1;
                for(var ri = colRowList.length-1;ri>=0;ri--){
                    var row = colRowList[ri];
                    var cell2 = this.board[row][col];
                    if(cell2.gem!=='')continue;//有宝石就不管
                    //找上方最近的宝石掉下来
                    for(var up = row-1;up>=0;up--){
                        var cellUp = this.board[up][col];
                        if(cellUp.gem === '')continue;
                        cell2.gem = cellUp.gem;
                        cell2.bomb = cellUp.bomb;
                        cellUp.gem = '';
                        cellUp.bomb = false;
                        step.falls.push({column:col,fromRow:up,toRow:row,gem:cell2.gem})
                        break;
                    }
                    //上方没有了就随机生成一颗
                    if(cell2.gem === ''){
                        var index = Math.floor(Math.random()*6);
                        cell2.gem = this.STAR_COLOR[index];
                        cell2.bomb = false;
                        var spawnY = this.TOP_Y+300+newCount*this.STEP;
                        step.falls.push({column:col,fromRow:-1,toRow:row,gem:cell2.gem,spawnY:spawnY});
                        newCount = newCount+1;
                        topSpawn = step.falls.length-1;
                    }
                }
                if(this.goalPending&&col===this.goalColumn&&topSpawn>=0){
                    var topRec = step.falls[topSpawn];
                    this.board[topRec.toRow][col].gem = 'goal';
                    this.board[topRec.toRow][col].bomb = false;
                    topRec.gem = 'goal';
                    this.goalSpawned = true;
                    this.goalPending = false;
                }
            }
            step.points = step.cleared.length*perGem+bonus;
            this.score = this.score+step.points;
            this.steps.push(step);
        }
        return totalCleared;
    },

    getTimeBonus:function(){
        return Math.floor(this.time)*300;
    },

    bestKey:function(){
        return'best_'+this.world+'_'+this.level;
    },
    //交换:有匹配就保留返回true;没匹配就换回去返回false
    tryChange:function(r1,c1,r2,c2){
        var a = this.board[r1][c1];
        var b = this.board[r2][c2];
        if(a.gem===''||b.gem===''){
            return false;//空洞换不了
        }
        var temp = a.gem;
        a.gem = b.gem;
        b.gem = temp;
        var tempBomb = a.bomb;
        a.bomb = b.bomb;
        b.bomb = tempBomb;
        if(this.hasMatch()){
            return true;
        }
        temp = a.gem;
        a.gem = b.gem;
        b.gem = temp;
        tempBomb = a.bomb;
        a.bomb = b.bomb;
        b.bomb = tempBomb;
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
    },

    wouldMatch:function(r1,c1,r2,c2){//试换两格,看会不会消,试完换回来
        var a = this.board[r1][c1];
        var b = this.board[r2][c2];
        var temp = a.gem;
        a.gem = b.gem;
        b.gem = temp;
        var ok = this.hasMatch();
        temp = a.gem;
        a.gem = b.gem;
        b.gem = temp;
        return ok;
    },

    findMove:function(){//找一组能消的交换
        for(var r = 0;r<this.ROW;r++){
            for(var c = 0;c<this.COL;c++){
                if(this.board[r][c].gem==='')continue;//空洞换不了
                if(c+1<this.COL&&this.board[r][c+1].gem!==''&&this.wouldMatch(r,c,r,c+1)){
                    return [r,c,r,c+1];
                }
                if(r+1<this.ROW&&this.board[r+1][c].gem!==''&&this.wouldMatch(r,c,r+1,c)){
                    return [r,c,r+1,c];
                }
            }
        }
        return null;
    },

    hasMove:function(){//盘上还有没有能消的一步
        return this.findMove()!==null;
    },

    permuteGems:function(){//只把棋子的位置重排,颜色数量都不变
        var cells = [];
        var gems = [];
        var bombs = [];
        for(var r = 0;r<this.ROW;r++){
            for(var c = 0;c<this.COL;c++){
                if(this.board[r][c].gem===''||this.board[r][c].gem==='goal'){
                    continue;//空洞和goal宝石不参与重排
                }
                cells.push([r,c]);
                gems.push(this.board[r][c].gem);
                bombs.push(this.board[r][c].bomb);
            }
        }
        var total = cells.length;
        var perm = [];
        for(var i = 0;i<total;i++){
            perm.push(i);
        }
        for(var p = total-1;p>0;p--){//打乱位置顺序
            var q = Math.floor(Math.random()*(p+1));
            var t = perm[p];
            perm[p] = perm[q];
            perm[q] = t;
        }
        for(var m = 0;m<total;m++){//没挪窝的那颗跟旁边换一下
            if(perm[m]===m){
                var n = (m+1)%total;
                var t2 = perm[m];
                perm[m] = perm[n];
                perm[n] = t2;
            }
        }
        this.shuffleMoves = [];
        for(var k = 0;k<total;k++){
            this.shuffleMoves.push({
                fromRow:cells[k][0],fromColumn:cells[k][1],
                toRow:cells[perm[k]][0],toColumn:cells[perm[k]][1]
            });
        }
        for(var k2 = 0;k2<total;k2++){
            var tr = cells[perm[k2]][0];
            var tc = cells[perm[k2]][1];
            this.board[tr][tc].gem = gems[k2];
            this.board[tr][tc].bomb = bombs[k2];
        }
    },

    shuffleBoard:function(){//洗到没有三连、但又还有得消为止
        var guard = 0;
        do{
            this.permuteGems();
            guard = guard+1;
        }while((this.hasMatch()||!this.hasMove())&&guard<200);
    }
})
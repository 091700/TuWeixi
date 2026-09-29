cc.Class({
    extends: cc.Component,
    start: function () {
        this.schedule(this.ChangeTwo, 7);
    },
    ChangeTwo: function () {
        var gems = this.node.children;
        var i = Math.floor(Math.random() * gems.length);
        var j;
        do {
            j = Math.floor(Math.random() * gems.length);
        } while (j === i);//截取两个不同的棋子的坐标
        var ax = gems[i].x, ay = gems[i].y;
        var bx = gems[j].x, by = gems[j].y;

        cc.tween(gems[i]).to(0.5,{x:bx,y:by}).start();
        cc.tween(gems[j]).to(0.5,{x:ax,y:ay}).start();
    }
});
window.LevelSelectModel = cc.Class({
    ctor:function(){
        this.worlds = [];
        var romanNumber = ['I','II','III','IV','V','VI','VII','VIII'];
        for(var i = 0;i<romanNumber.length;i++){ 
            this.worlds.push({
                name:'WORLD'+romanNumber[i], 
                unlocked:(i===0)
            });
        }//生成八个世界名
        this.PageSize = 4;//页面里框框数量
        this.CurrentPage = 1; //开始在第一页
    },
    getTotalPages:function(){
        return Math.ceil(this.worlds.length/this.PageSize);//向上取整总页数
    },
    getPageWorlds:function(){//获取数组位置截取数组，页面显示哪几个世界
        var start = (this.CurrentPage-1)*this.PageSize;
        return this.worlds.slice(start,start+4);
    },

    setPage:function(page){
        this.CurrentPage = page;
        return true;
    }
});
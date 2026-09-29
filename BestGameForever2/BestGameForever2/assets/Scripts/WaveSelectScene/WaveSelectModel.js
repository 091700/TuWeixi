window.WaveSelectModel = cc.Class({
    ctor: function () {
        this.world = window.currentWorld || 1;//从LevelSelect传出的序号
        this.TotalLevel = 99;                    
        this.Completed = 0;
        this.PageSize = 9;
        this.CurrentPage = 1;// 当前页
        this.stars = [];
        for (var i = 0; i < this.TotalLevel; i++) {
            this.stars.push(0);
        }
        this.stars[0] = 3;
        this.stars[1] = 2;
        this.stars[2] = 1;
    },

    getState: function (level) {
        if (level <= this.Completed) {
            return 'played';
        }
        if (level <= this.Completed+3) {
            return 'new';
        }
        return 'locked';
    },
    getTotalPages: function () {
        return Math.ceil(this.TotalLevel / this.PageSize);
    },
    getPageLevels: function () {
        var list = [];
        var start = (this.CurrentPage-1)*this.PageSize;
        for (var i = 0; i<this.PageSize;i++) {
            list.push(start+i+1);
        }
        return list;
    },
    setPage: function (page) {
        if (page < 1 || page > this.getTotalPages()) {
            return false;
        }
        this.CurrentPage = page;
        return true;
    }
});
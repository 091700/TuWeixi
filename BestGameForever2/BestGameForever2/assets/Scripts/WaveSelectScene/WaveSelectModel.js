window.WaveSelectModel = cc.Class({
    ctor: function () {
        this.world = window.CurrentWorld || 1;//从LevelSelect传出的序号
        this.TotalLevel = 99;                    
        this.Completed = parseInt(localStorage.getItem('completed_'+this.world)||'0',10);
        this.PageSize = 9;
        this.CurrentPage = 1;// 当前页
        this.stars = [];
        for (var i = 0; i < this.TotalLevel; i++) {
            this.stars.push(parseInt(localStorage.getItem('stars_'+this.world+'_'+(i+1))||'0',10));
        }
        this.DoneCount = 0;
        for (var j = 0; j < this.TotalLevel; j++) {
            if (this.stars[j] > 0) {
                this.DoneCount = this.DoneCount+1;
            }
        }
        if (this.DoneCount === 0 && this.Completed > 0) {
            this.DoneCount = this.Completed;
        }
        this.MaxUnlocked = this.DoneCount+3;
    },

    getState: function (level) {
        if (this.stars[level-1] > 0) {
            return 'played';
        }
        if (level <= this.MaxUnlocked) {
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
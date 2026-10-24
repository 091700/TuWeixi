window.WinSceneModel = cc.Class({
    ctor:function(){
        this.world = window.CurrentWorld||1;
        this.level = window.CurrentLevel||1;
        this.levelScore = window.lastLevelScore||0;
        this.timeBonus = window.lastTimeBonus||0;
        this.bestScore = parseInt(localStorage.getItem('best_'+this.world+'_'+this.level)||'0',10);
        this.totalScore = this.levelScore+this.timeBonus;
        this.stars = this.getStarCount();
    },

    getStarCount:function(){
        if(this.totalScore>=90000){
            return 3;
        }
        if(this.totalScore>=60000){
            return 2;
        }
        return 1;
    },

    getTitle:function(){
        var roman = ['','I','II','III','IV','V'];
        return 'LEVEL '+roman[this.world]+'-'+this.level+' COMPLETE!';
    }
})
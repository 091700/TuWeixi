window.DefeatModel = cc.Class({
    ctor:function(){
        this.world = window.CurrentWorld||1;
        this.level = window.CurrentLevel||1;
    },

    getTitle:function(){
        return 'LEVEL '+this.world+'-'+this.level+' FAILED';
    },

    canSkip:function(){
        var completed = parseInt(localStorage.getItem('completed_'+this.world)||'0',10);
        return(this.level+1)<=completed+3;
    },
})
window.DefeatView = cc.Class({
    extends:cc.Component,
    properties:{
        titleLabel:{
            default:null,type:cc.Label
        },
        model:{
            default:null
        }
    },

    render:function(){//显示标题
        this.titleLabel.string = this.model.getTitle();
    }
});
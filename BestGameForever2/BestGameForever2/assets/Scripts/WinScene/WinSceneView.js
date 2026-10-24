window.WinSceneView = cc.Class({
    extends:cc.Component,
    properties:{
        titleLabel:{
            default:null,type:cc.Label
        },
        noStar1:{//中间
            default:null,type:cc.Node
        },
        noStar2:{//左边
            default:null,type:cc.Node
        },
        noStar3:{
            default:null,type:cc.Node
        },
        haveStar:{
            default:null,type:cc.Node
        },
        model:{
            default:null
        },
        levelScoreLabel:{
            default:null,type:cc.Label
        },
        timeBonusLabel:{
            default:null,type:cc.Label
        },
        totalScoreLabel:{
            default:null,type:cc.Label
        },
        bestScoreLabel:{
            default:null,type:cc.Label
        }
    },

    render:function(){
        if(this.titleLabel){
            this.titleLabel.string = this.model.getTitle();
        }
    },

    setScores:function(levelScore,timeBonus,bestScore){//显示分数
        this.levelScoreLabel.string = levelScore+'';
        this.timeBonusLabel.string = timeBonus+'';
        this.totalScoreLabel.string = '0';
        this.bestScoreLabel.string = bestScore+'';
    },

    countLabel:function(label,from,to,duration){//分数变小
        var node = label.node;
        var gap = from-to;
        cc.tween(node)
            .to(duration,{x:node.x},{progress:function(start,end,current,t){
                label.string = Math.floor(from-gap*t)+'';
                return current;
            }})
            .call(function(){
                label.string = to+'';
            })
            .start();
    },

    playScoreCount:function(){
        var model = this.model;
        this.countLabel(this.levelScoreLabel,model.levelScore,0,2);
        this.countLabel(this.timeBonusLabel,model.timeBonus,0,2);
        this.countLabel(this.totalScoreLabel,0,model.levelScore+model.timeBonus,2);
    },

    showStars:function(count){//点亮星星
        this.haveStar.active = false;//开始隐藏星星
        var grayList = [this.noStar1,this.noStar2,this.noStar3];
        for(var i = 0;i<grayList.length;i++){
            if(i<count){//星星挂到灰星上面
                var star = cc.instantiate(this.haveStar);
                star.parent = grayList[i];
                star.setPosition(-8,15);
                star.active = true;
            }
        }
    }
})
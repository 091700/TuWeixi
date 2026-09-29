window.WaveSelectView = cc.Class({
    extends:cc.Component,
    properties:{
        Parent:{default: null, type:cc.Node},          // 9 个框的容器
        newPrefab:{default: null, type:cc.Prefab},     // 解锁未玩(New)
        lockedPrefab:{default: null, type:cc.Prefab},  // 锁定
        playedPrefab:{default: null, type:cc.Prefab},  // 玩过
        ballPrefab:{default: null, type:cc.Prefab},
        thisPageBallImg:{default: null, type:cc.SpriteFrame},
        anotherPageImg:{default: null, type:cc.SpriteFrame},
        tipPrefab:{default: null, type:cc.Prefab},
        titleLabel:{default: null, type:cc.Label},
        model:{default: null }
    },
    onLoad:function(){
        this.slots = [
            cc.v2(-220, 380), cc.v2(0, 380), cc.v2(220, 380),
            cc.v2(-220, 160), cc.v2(0, 160), cc.v2(220, 160),
            cc.v2(-220, -60), cc.v2(0, -60), cc.v2(220, -60)
        ];
        this.tip = null;
        this.lastPage = 1;
        this.ballParent = new cc.Node('Balls');
        cc.find('Canvas/WaveSelectPage').addChild(this.ballParent);
        window.EventBus.on('WaveSelectPageChanged', this.onPageChanged, this);
        var roman = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII'];
        this.titleLabel.string = 'WORLD ' + roman[this.model.world - 1] + ': SELECT LEVEL';
    },
    onDestroy:function () {
        window.EventBus.targetOff(this);
    },
    render: function () {
        this.Parent.removeAllChildren();
        this.buildWaves(0);
        this.buildBalls();
        this.lastPage = this.model.CurrentPage;
    },
    buildWaves:function(offsetX){
        var model = this.model;
        var levels = model.getPageLevels();
        for (var i = 0; i < levels.length; i++) {
            var level = levels[i];
            var node = this.makeWave(level, i, offsetX);
            node.parent = this.Parent;
        }
    },
    makeWave:function(level, index, offsetX){
        var model = this.model;
        var state = model.getState(level);
        var node;
        if (state === 'new'){
            node = cc.instantiate(this.newPrefab);
        }else if(state === 'locked'){
            node = cc.instantiate(this.lockedPrefab);
        }else {
            node = cc.instantiate(this.playedPrefab);
        }
        node.setPosition(this.slots[index].x + offsetX,this.slots[index].y);
        node.getChildByName('WaveNumber').getComponent(cc.Label).string = level+'';
        if(state === 'played'){
            var starCount = model.stars[level-1];
            if (starCount < 1){
                starCount = 1;
            }
            node.getChildByName('1Star').active = starCount >= 1;
            node.getChildByName('2Star').active = starCount >= 2;
            node.getChildByName('3Star').active = starCount >= 3;
        }
        node.on('click',(function(lv){
            return function () {
                window.EventBus.emit('WaveClicked', lv);
            };
        })(level));
        return node;
    },

    buildBalls: function () {
        var model = this.model;
        this.ballParent.removeAllChildren();
        var totalPages = model.getTotalPages();
        var totalBallsWidth = totalPages * 50 + (totalPages - 1) * 10;
        var centerX = -totalBallsWidth / 2 + 50 / 2;
        for (var i = 0; i < totalPages; i++) {
            var ball = cc.instantiate(this.ballPrefab);
            ball.setPosition(centerX + i * (50 + 10), -230);
            var sprite = ball.getComponent(cc.Sprite);
            if (i === model.CurrentPage - 1) {
                sprite.spriteFrame = this.thisPageBallImg;
            } else {
                sprite.spriteFrame = this.anotherPageImg;
                ball.on('click', (function (p) {
                    return function () {
                        window.EventBus.emit('GoToPage', p);
                    };
                })(i + 1));
            }
            ball.parent = this.ballParent;
        }
    },

    onPageChanged: function () {
        var model = this.model;
        var dir;
        if (model.CurrentPage > this.lastPage){
            dir = 1;
        } else {
            dir = -1;
        }
        this.lastPage = model.CurrentPage;
        var olds = this.Parent.children.slice();
        for (var i = 0; i < olds.length; i++) {
            (function (node) {
                cc.tween(node)
                    .to(0.3, { x: node.x - dir * 720 })
                    .call(function () { node.destroy(); })
                    .start();
            })(olds[i]);
        }

        var levels = model.getPageLevels();
        for (var j = 0; j < levels.length; j++) {
            var node2 = this.makeWave(levels[j], j, dir * 720);
            cc.tween(node2).to(0.3, { x: this.slots[j].x }).start();
            node2.parent = this.Parent;
        }
        this.buildBalls();
    },

    showTip: function () {
        var that = this;
        if (!this.tip) {
            this.tip = cc.instantiate(this.tipPrefab);
            this.tip.setPosition(0, 0);
            cc.find('Canvas').addChild(this.tip);
            this.tip.getChildByName('TipLabel').getChildByName('OKBtn').on('click', function () {
                that.tip.active = false;
            });
        }
        this.tip.active = true;
    }
});
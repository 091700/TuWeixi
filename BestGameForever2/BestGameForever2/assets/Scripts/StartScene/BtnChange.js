cc.Class({
    extends: cc.Component,
    properties: {
        iconNode: { default: null, type: cc.Node }, 
        iconA:    { default: null, type: cc.SpriteFrame }, 
        iconB:    { default: null, type: cc.SpriteFrame }, 
    },
    onLoad: function () {
        this.toggleOn = true;  
        this.node.on('click', this.onClick, this);
    },
    onClick: function () {
        var sprite = this.iconNode.getComponent(cc.Sprite);

        if (this.toggleOn) {
            sprite.spriteFrame = this.iconB;  
            this.toggleOn = false;
        } else {
            sprite.spriteFrame = this.iconA; 
            this.toggleOn = true;
        }
    }
});
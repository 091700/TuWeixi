cc.Class({
    extends:cc.Component,
    properties:{
        iconNode:{
            default:null,type:cc.Node}, 
        iconA:{
            default:null,type:cc.SpriteFrame}, 
        iconB:{
            default:null,type:cc.SpriteFrame}, 
        isMusic:{
            default:false
        },
    },
    onLoad: function () {
        this.toggleOn = true;
        if(this.isMusic){
            this.toggleOn = window.BGM.on;
            if(!this.toggleOn){
                this.iconNode.getComponent(cc.Sprite).spriteFrame = this.iconB;
            }
        }
        this.node.on('click',this.onClick,this);
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
        if(this.isMusic){
            window.BGM.toggle();
        }
    }
});
window.BGM = {
    tracks:['Music/BGM/Fantastic_Adventures_my_mix','Music/BGM/Magic_Land_060_sec'],
    index:0,
    started:false,
    on:(localStorage.getItem('bgmOn')||'1')==='1',//开关
    start:function(){
        if(this.started)
            return;
        this.started = true;
        if(this.on){
            this.playIndex(0);
        }
    },

    playIndex:function(i){
        this.index = i;
        var that = this;
        cc.resources.load(this.tracks[i],cc.AudioClip,function(err,clip){
            if(!that.on)
                return;
            var id = cc.audioEngine.playMusic(clip,false);
            cc.audioEngine.setFinishCallback(id,function(){
                if(that.on){
                    that.playIndex((that.index+1)%that.tracks.length);//换下一首
                }
            });
        });
    },

    toggle:function(){
        this.on = !this.on;
        localStorage.setItem('bgmOn',this.on?'1':'0');
        if(this.on){
            this.playIndex(this.index);
        }else{
            cc.audioEngine.stopMusic();
        }
    }
};
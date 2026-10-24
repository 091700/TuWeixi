window.LevelData = {
    HAND:{
        1:[
            "1111111",
            "1111111",
            "1111111",
            "1111111",
            "1111111",
            "1111111",
            "1111111",
            "1111111",
            "1111111"
        ],
        2:[
            "-11111-",
            "1111111",
            "1111111",
            "1111111",
            "1111111",
            "1111111",
            "1111111",
            "1111111",
            "-11111-"
        ],
        3:[
            "11---11",
            "1111111",
            "1111111",
            "2222222",
            "2222222",
            "2222222",
            "1111111",
            "1111111",
            "11---11"
        ],
        4:[
            "1111111",
            "1222221",
            "1233321",
            "1233321",
            "1233321",
            "1233321",
            "1233321",
            "1222221",
            "1111111"
        ],
        5:[
            "-11111-",
            "1222221",
            "1233321",
            "1233321",
            "12---21",
            "1233321",
            "1233321",
            "1222221",
            "-11111-"
        ],
        6:[
            "1111111",
            "1222221",
            "1233321",
            "12---21",
            "12---21",
            "12---21",
            "1233321",
            "1222221",
            "1111111"
        ]
    },

    ROW:9,
    COL:7,
    MAX_HOLES:16,

    getTime:function(world,level){
        if(world===1&&level===1){
            return 420;
        }
        if(world===1){
            return 302-level;
        }
        return 301-level;
    },

    getMap:function(level){
        var hand = this.HAND[level];
        if(hand){
            return hand;
        }
        return this.makeMap(level);
    },

    get:function(world,level){
        return {time:this.getTime(world,level),map:this.getMap(level)};
    },

    makeRandom:function(seed){
        var s = seed>>>0;
        return function(){
            s = (s*1664525+1013904223)>>>0;
            return s/4294967296;
        };
    },

    shuffleList:function(list,rng){
        for(var i = list.length-1;i>0;i--){
            var j = Math.floor(rng()*(i+1));
            var t = list[i];
            list[i] = list[j];
            list[j] = t;
        }
    },

    makeOrbits:function(mode){
        var orbits = [];
        for(var r = 0;r<this.ROW;r++){
            for(var c = 0;c<this.COL;c++){
                var cells = [];
                if(mode===0){
                    if(r>this.ROW-1-r){
                        continue;
                    }
                    cells.push([r,c]);
                    if(this.ROW-1-r!==r){
                        cells.push([this.ROW-1-r,c]);
                    }
                }else if(mode===1){
                    if(c>this.COL-1-c){
                        continue;
                    }
                    cells.push([r,c]);
                    if(this.COL-1-c!==c){
                        cells.push([r,this.COL-1-c]);
                    }
                }else{
                    if(r>this.ROW-1-r||c>this.COL-1-c){
                        continue;
                    }
                    cells.push([r,c]);
                    if(this.COL-1-c!==c){
                        cells.push([r,this.COL-1-c]);
                    }
                    if(this.ROW-1-r!==r){
                        cells.push([this.ROW-1-r,c]);
                        if(this.COL-1-c!==c){
                            cells.push([this.ROW-1-r,this.COL-1-c]);
                        }
                    }
                }
                orbits.push(cells);
            }
        }
        return orbits;
    },

    tryMap:function(level,target,attempt){
        var rng = this.makeRandom(level*7919+attempt*104729+17);
        var mode = Math.floor(rng()*3);
        var hole = [];
        for(var r = 0;r<this.ROW;r++){
            hole.push([]);
            for(var c = 0;c<this.COL;c++){
                hole[r].push(false);
            }
        }
        var orbits = this.makeOrbits(mode);
        this.shuffleList(orbits,rng);
        var count = 0;
        for(var i = 0;i<orbits.length;i++){
            if(count>=target){
                break;
            }
            var o = orbits[i];
            if(count+o.length>this.MAX_HOLES){
                continue;
            }
            for(var j = 0;j<o.length;j++){
                hole[o[j][0]][o[j][1]] = true;
            }
            count = count+o.length;
        }
        if(!this.canPlay(hole)){
            return null;
        }
        var w3 = Math.min(35,8+(level-4)*0.35);
        var w2 = 35;
        var tier = [];
        for(var rt = 0;rt<this.ROW;rt++){
            tier.push([]);
            for(var ct = 0;ct<this.COL;ct++){
                tier[rt].push(1);
            }
        }
        var tierOrbits = this.makeOrbits(mode);
        for(var k = 0;k<tierOrbits.length;k++){
            var t = 1;
            var roll = rng()*100;
            if(roll<w3){
                t = 3;
            }else if(roll<w3+w2){
                t = 2;
            }
            for(var n = 0;n<tierOrbits[k].length;n++){
                tier[tierOrbits[k][n][0]][tierOrbits[k][n][1]] = t;
            }
        }
        var map = [];
        for(var rm = 0;rm<this.ROW;rm++){
            var line = '';
            for(var cm = 0;cm<this.COL;cm++){
                if(hole[rm][cm]){
                    line = line+'-';
                }else{
                    line = line+tier[rm][cm];
                }
            }
            map.push(line);
        }
        return map;
    },

    canPlay:function(hole){
        for(var rr = 0;rr<this.ROW;rr++){
            for(var cc = 0;cc<this.COL;cc++){
                if(hole[rr][cc]){
                    continue;
                }
                var h = 1;
                var x = cc-1;
                while(x>=0&&!hole[rr][x]){
                    h = h+1;
                    x = x-1;
                }
                x = cc+1;
                while(x<this.COL&&!hole[rr][x]){
                    h = h+1;
                    x = x+1;
                }
                var v = 1;
                var y = rr-1;
                while(y>=0&&!hole[y][cc]){
                    v = v+1;
                    y = y-1;
                }
                y = rr+1;
                while(y<this.ROW&&!hole[y][cc]){
                    v = v+1;
                    y = y+1;
                }
                if(h<3&&v<3){
                    return false;
                }
            }
        }
        return true;
    },

    makeMap:function(level){
        var target = Math.min(this.MAX_HOLES,8+Math.floor((level-7)*0.22));
        for(var attempt = 0;attempt<40;attempt++){
            var map = this.tryMap(level,target,attempt);
            if(map){
                return map;
            }
        }
        return this.HAND[5];
    }
};

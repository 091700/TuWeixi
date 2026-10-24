// ============================================================================
// CheatButton.js —— 小黄人测试按钮
// ----------------------------------------------------------------------------
// 这是一个**完全独立**的模块:不 require 项目里任何脚本,也不改任何现有代码。
// 它只通过"约定好的钩子"和游戏通信(见文件末尾的说明)。
//
// 它能做什么:
//   1. 点击 = 按 dropGoal 决定功能:
//        dropGoal 不勾 = 加 scoreBonus 分 + 清掉场上所有教程
//        dropGoal 勾上 = 清教程 + 让 goal 宝石直接落到最底下一行
//   2. 桌宠手感:按住能拖、松手能甩飞、有重力、会撞墙反弹、QQ 弹弹地回正
//   3. 点击特效:脉冲光环 + 爆裂粒子 + 飘字 + 自己蹦一下 + 高速拖尾
//   4. 只在暂停界面出现,每次出现的位置随机
//
// 怎么用:
//   1. 新建节点,加 cc.Sprite 组件,把 YellowManBtn.png 拖到 SpriteFrame 上
//      (想做"掉 goal"的第二个按钮就复制一份,换成 RedManBtn.png,并勾上 dropGoal)
//   2. 把这个节点放到 Canvas 正下方(和 Page 同级),这样坐标就是屏幕坐标系
//   3. 给这个节点挂上本脚本
//   4. (想真的作弊)在游戏侧接两个钩子,见文件最末尾注释
// ============================================================================

// 所有按钮的登记簿:每个按钮 onLoad 时把自己登记进来,销毁时注销
// 有了它,按钮之间才能互相知道对方在哪,进而互相碰撞
var allButtons = [];

window.CheatButton = cc.Class({
    extends:cc.Component,

    properties:{
        // ---------- 作弊参数 ----------
        scoreBonus:{// 加多少分
            default:10000
        },
        dropGoal:{// 勾上 = 这个按钮改成"掉 goal 宝石"
            default:false
        },
        goalColumn:{// 掉 goal 时放在第几列(-1 = 随机)
            default:-1
        },

        // ---------- 手感参数(这些就是"调手感"的旋钮) ----------
        size:{// 按钮在屏幕上的边长(像素)
            default:130
        },
        tapJump:{// 点击时往上弹的初速度(想弹得更猛就加大)
            default:1250
        },
        gravity:{// 重力加速度:数字越大掉得越急
            default:2400
        },
        airFriction:{// 空气阻力:每秒衰减掉多少比例
            default:1.15
        },
        bounciness:{// 撞墙反弹:保留多少速度(0.62 = 弹回 62%)
            default:0.62
        },
        maxSpeed:{// 速度上限,防止甩出一个瞬移
            default:3200
        },
        groundFriction:{// 落地后的地面摩擦
            default:3.2
        },
        rotateFactor:{// 横向速度转成旋转的系数(甩得越快转得越猛)
            default:0.035
        },
        grabScale:{// 被抓住时放大多少倍
            default:1.14
        },
        tapDistance:{// 手指移动小于这个像素数,才算"点击"而不是"拖动"
            default:16
        },
        tapTime:{// 按住时间小于这个秒数,才算"点击"
            default:0.42
        },

        // ---------- 位置/边界 ----------
        groundTrim:{// 底部留白补偿:贴图下方透明留白的像素量(我的图填0)
            default:0
        },
        spawnRangeX:{// 出场时 x 的随机范围(±这个数;想满屏就调到 300 左右)
            default:260
        },
        spawnBandH:{// 出场"出生带"的高度:随机落在屏幕上方带或下方带里(避开中间的面板)
            default:200
        },
        spawnDrift:{// 出场时横向漂移+旋转的随机量(0 = 乖乖原地落下)
            default:260
        },

        // ---------- 外观参数 ----------
        ringColor:{// 点击光环/粒子的颜色(红按钮就换成红色)
            default:cc.color(255,232,90,255)
        },
        squashStiffness:{// 挤压弹簧的硬度(越大回弹越快)
            default:170
        },
        squashDamping:{// 挤压弹簧的阻尼(越大越快停)
            default:11
        },
        breatheAmp:{// 待机呼吸的幅度
            default:0.035
        },
        breatheSpeed:{// 待机呼吸的快慢
            default:2.4
        },
        trailOn:{// 高速时是否拖尾
            default:true
        },
        collideEachOther:{// 按钮之间是否互相碰撞弹开
            default:true
        }
    },

    // ==========================================================================
    // 生命周期
    // ==========================================================================
    onLoad:function(){
        // ---- 外观初始化:固定尺寸,不然 Sprite 会按贴图原尺寸(300x300)显示 ----
        var sprite = this.node.getComponent(cc.Sprite);
        if(sprite){
            sprite.sizeMode = cc.Sprite.SizeMode.CUSTOM;
        }
        // 尺寸以编辑器里设的为准:节点内容尺寸 × 缩放,才是屏幕上真正看到的像素大小
        // (以前这里硬把 contentSize 设成 this.size,会和编辑器的缩放打架:
        //  碰撞按方框算,角色却缩在小方框里,于是悬空一大截)
        if(this.node.width<=0||this.node.height<=0){
            this.node.width = this.size;
            this.node.height = this.size;
        }
        this.node.zIndex = 50;// 站在所有界面之上,免得被棋盘/遮罩挡住点不到

        // ---- 运动状态 ----
        this.vel = cc.v2(0,0);// 速度(像素/秒)
        this.angle = 0;// 当前旋转角(度)
        this.spin = 0;// 旋转角速度(度/秒)
        this.t = 0;// 累计时间,给呼吸动画用

        // ---- 挤压弹簧:QQ弹弹的来源 ----
        // squash < 0 = 被压扁, squash > 0 = 被拉长;它会自己弹回 0
        this.squash = 0;
        this.squashVel = 0;
        this.squashAxis = 'y';// 往哪条轴压扁

        // ---- 输入状态 ----
        this.dragging = false;
        this.pressPos = cc.v2(0,0);// 按下时的位置
        this.grabOffset = cc.v2(0,0);// 抓取点与按钮中心的偏移,防止一抓就"跳"
        this.pressTime = 0;
        this.moved = 0;// 本次按下累计移动了多少
        this.history = [];// 最近几帧的位置采样,用来算甩出去的初速度

        // ---- 特效节流 ----
        this.trailTimer = 0;

        // ---- 出场缩放(暂停时"弹"出来的效果) ----
        this.spawn = 1;// 1 = 正常大小
        this.spawnVel = 0;

        // ---- 屏幕边界 ----
        // 用设计分辨率当活动范围。按钮放在 Canvas 下时,局部坐标原点=屏幕中心
        this.halfW = cc.winSize.width/2;
        this.halfH = cc.winSize.height/2;

        // ---- 记录基准缩放,后面所有缩放都在它上面乘 ----
        this.baseScaleX = this.node.scaleX;
        this.baseScaleY = this.node.scaleY;

        // ---- 屏幕上真正看到的宽高 = 内容尺寸 × 缩放 ----
        // 碰撞边界、光环半径、飘字位置全都按这个算,不然就会和实际画面错开
        this.vW = this.node.width*this.baseScaleX;
        this.vH = this.node.height*this.baseScaleY;

        // ---- 绑触摸 ----
        this.node.on('touchstart',this.onTouchStart,this);
        this.node.on('touchmove',this.onTouchMove,this);
        this.node.on('touchend',this.onTouchEnd,this);
        this.node.on('touchcancel',this.onTouchEnd,this);

        // ---- 登记到全局按钮簿,这样才能和其他按钮互相碰撞 ----
        if(allButtons.indexOf(this)<0){
            allButtons.push(this);
        }

        // ---- 只在暂停界面出现 ----
        // 用游戏里现成的事件总线,不需要改任何别的文件
        window.EventBus.on('GamePause',this.onShow,this);
        window.EventBus.on('GameResume',this.onHide,this);
        window.EventBus.on('GameRestart',this.onHide,this);
        this.node.active = false;
    },

    // 暂停了:弹出来,并换一个随机位置重新开始
    onShow:function(){
        var x = (Math.random()*2-1)*this.spawnRangeX;
        // y:在"上方带"和"下方带"里随机挑一个,中间那条留给暂停面板,不会挡住按钮
        var y;
        if(Math.random()<0.5){
            y = this.halfH-this.vH-Math.random()*this.spawnBandH;// 上方带
        }else{
            y = -this.halfH+this.vH+Math.random()*this.spawnBandH;// 下方带
        }
        // 别让随机位置把按钮怼到屏幕外(按"实际看到的大小"和锚点算)
        var aw = this.vW*this.node.anchorX;
        var ah = this.vH*this.node.anchorY;
        x = Math.max(-this.halfW+aw,Math.min(this.halfW-this.vW*(1-this.node.anchorX),x));
        y = Math.max(-this.halfH+ah,Math.min(this.halfH-this.vH*(1-this.node.anchorY),y));
        this.node.setPosition(x,y);

        // 一出生就带一点随机漂移和随机旋转,每次出现的轨迹都不一样
        this.vel = cc.v2((Math.random()*2-1)*this.spawnDrift,0);
        this.spin = (Math.random()*2-1)*420;
        this.angle = 0;
        this.squash = 0;
        this.squashVel = 0;
        this.trailTimer = 0;
        this.dragging = false;
        this.spawn = 0.2;// 从很小开始,靠弹簧弹回原大小
        this.spawnVel = 0;
        this.node.zIndex = 200;// 必须高过暂停面板(zIndex 100),不然点不到
        this.node.active = true;
    },

    // 不暂停了:立刻收起来(不做动画,免得露出半截)
    onHide:function(){
        this.node.active = false;
        this.dragging = false;
    },

    // 出场弹簧:像 squash 一样,过冲一点再收回 1
    stepSpawn:function(dt){
        if(Math.abs(this.spawn-1)<0.001&&Math.abs(this.spawnVel)<0.01){
            this.spawn = 1;
            this.spawnVel = 0;
            return;
        }
        var acc = (1-this.spawn)*this.squashStiffness*0.55-this.spawnVel*this.squashDamping;
        this.spawnVel = this.spawnVel+acc*dt;
        this.spawn = this.spawn+this.spawnVel*dt;
    },

    onDestroy:function(){
        this.node.off('touchstart',this.onTouchStart,this);
        this.node.off('touchmove',this.onTouchMove,this);
        this.node.off('touchend',this.onTouchEnd,this);
        this.node.off('touchcancel',this.onTouchEnd,this);
        var idx = allButtons.indexOf(this);
        if(idx>=0){
            allButtons.splice(idx,1);// 从按钮簿里注销,不然场景切了还留着幽灵按钮
        }
        window.EventBus.targetOff(this);
    },

    // ==========================================================================
    // 输入:拖 / 甩 / 点
    // ==========================================================================

    // 屏幕坐标 -> 本按钮父节点的坐标(和 this.node.x/y 同一套)
    toLocal:function(screenPos){
        var parent = this.node.parent;
        if(parent){
            return parent.convertToNodeSpaceAR(screenPos);
        }
        return screenPos;
    },

    onTouchStart:function(e){
        var p = this.toLocal(e.getLocation());
        this.dragging = true;
        this.pressPos = p;
        this.grabOffset = cc.v2(this.node.x-p.x,this.node.y-p.y);// 抓哪儿就是哪儿
        this.pressTime = cc.director.getTotalTime()/1000;
        this.moved = 0;
        this.history = [];
        this.vel = cc.v2(0,0);// 一抓住,之前的飞行惯性立刻清掉
        this.spin = 0;
        this.pushHistory(this.node.x,this.node.y);
    },

    onTouchMove:function(e){
        if(!this.dragging)return;
        var p = this.toLocal(e.getLocation());
        var nx = p.x+this.grabOffset.x;
        var ny = p.y+this.grabOffset.y;

        // 累计位移:用来区分"点击"还是"拖动"
        var dx = nx-this.pressPos.x;
        var dy = ny-this.pressPos.y;
        var dist = Math.sqrt(dx*dx+dy*dy);
        if(dist>this.moved){
            this.moved = dist;
        }

        this.node.setPosition(nx,ny);
        this.pushHistory(nx,ny);

        // 抓在手里时,顺着拖动方向轻微倾斜,像拎着一个东西
        this.angle = Math.max(-28,Math.min(28,dx*0.12));
    },

    onTouchEnd:function(e){
        if(!this.dragging)return;
        this.dragging = false;

        var now = cc.director.getTotalTime()/1000;
        var held = now-this.pressTime;

        // 没怎么动 + 时间短 = 这是一次"点击"
        if(this.moved<this.tapDistance&&held<this.tapTime){
            this.angle = 0;
            this.onTap();
            return;
        }

        // 否则当作"甩出去"
        this.vel = this.computeThrowVelocity();
        // 甩得越快转得越猛;往右甩顺时针,往左甩逆时针(再叠一点随机,每次都不一样)
        this.spin = -this.vel.x*this.rotateFactor*(0.7+Math.random()*0.7);
        // 甩出去的一瞬间拉长一下,像被扯出去的
        this.squash = 0.3;
        this.squashVel = 0;
        this.squashAxis = 'y';
    },

    // 把当前位置和时间记进采样表
    pushHistory:function(x,y){
        this.history.push({x:x,y:y,t:cc.director.getTotalTime()/1000});
        // 只留最近 0.25 秒的采样,太多没必要
        while(this.history.length>2&&this.history[this.history.length-1].t-this.history[0].t>0.25){
            this.history.shift();
        }
    },

    // 用最近一段采样的平均速度当作松手瞬间的速度
    // 这就是"甩"的核心:不取最后一帧(抖动大),而是取一小段时间的平均
    computeThrowVelocity:function(){
        var n = this.history.length;
        if(n<2){
            return cc.v2(0,0);
        }
        var last = this.history[n-1];
        var ref = this.history[0];
        // 找 0.05 秒之前的那个采样,保证时间差不至于太小(太小会把抖动放大)
        for(var i = n-2;i>=0;i--){
            if(last.t-this.history[i].t>=0.05){
                ref = this.history[i];
                break;
            }
        }
        var dt = last.t-ref.t;
        if(dt<=0){
            return cc.v2(0,0);
        }
        var v = cc.v2((last.x-ref.x)/dt,(last.y-ref.y)/dt);
        var speed = Math.sqrt(v.x*v.x+v.y*v.y);
        if(speed>this.maxSpeed){// 限速:不然轻轻一甩就飞出宇宙
            var k = this.maxSpeed/speed;
            v.x = v.x*k;
            v.y = v.y*k;
        }
        return v;
    },

    // ==========================================================================
    // 物理:每帧算一次
    // ==========================================================================
    update:function(dt){
        this.t = this.t+dt;
        this.stepSpawn(dt);

        if(this.dragging){
            // 被抓住时不参与物理,只做"被拎起来"的视觉
            this.spin = 0;
            this.stepSquash(dt);
            this.collideButtons();// 手抓着的时候也要能把别的按钮撞开
            this.applyTransform();
            return;
        }

        // ---- 1. 重力 ----
        this.vel.y = this.vel.y-this.gravity*dt;

        // ---- 2. 空气阻力 ----
        // 每帧把速度乘一个略小于 1 的系数,时间越久剩下的越少
        // (写成乘 dt 的形式,是为了不管帧率高低,衰减速度都一样)
        var damp = 1-this.airFriction*dt;
        if(damp<0){
            damp = 0;
        }
        this.vel.x = this.vel.x*damp;
        this.vel.y = this.vel.y*damp;

        // ---- 3. 限速 ----
        var speed = Math.sqrt(this.vel.x*this.vel.x+this.vel.y*this.vel.y);
        if(speed>this.maxSpeed){
            var k = this.maxSpeed/speed;
            this.vel.x = this.vel.x*k;
            this.vel.y = this.vel.y*k;
        }

        // ---- 4. 位移 ----
        this.node.x = this.node.x+this.vel.x*dt;
        this.node.y = this.node.y+this.vel.y*dt;

        // ---- 5. 和其他按钮互相碰撞(撞完再贴墙,免得被顶出屏幕) ----
        this.collideButtons();

        // ---- 6. 撞墙 ----
        this.collideBounds(dt);

        // ---- 7. 旋转 ----
        this.angle = this.angle+this.spin*dt;
        this.spin = this.spin*(1-1.8*dt);// 旋转慢慢停

        // ---- 8. 挤压弹簧回正 ----
        this.stepSquash(dt);

        // ---- 9. 应用视觉 ----
        this.applyTransform();

        // ---- 10. 高速拖尾 ----
        if(this.trailOn){
            this.trailTimer = this.trailTimer+dt;
            var sp = Math.sqrt(this.vel.x*this.vel.x+this.vel.y*this.vel.y);
            if(sp>700&&this.trailTimer>0.045){
                this.trailTimer = 0;
                this.spawnTrail();
            }
        }
    },

    // 和其他按钮互相碰撞:把两个按钮都近似成圆,撞上就互相弹开
    // 被手抓着的那只不吃反弹(不然会从手里溜走),只负责把对方撞飞
    collideButtons:function(){
        if(!this.collideEachOther){
            return;
        }
        var n = allButtons.length;
        if(n<2){
            return;
        }
        // 自己的半径:取宽高里小的那个的一半,再留一点余量,免得贴图透明的四角也算进碰撞
        var ra = Math.min(this.vW,this.vH)*0.5*0.92;
        for(var i = 0;i<n;i++){
            var other = allButtons[i];
            if(other===this){
                continue;
            }
            if(!other.node||!other.node.parent||!other.node.activeInHierarchy){
                continue;// 对方没在场上就跳过
            }
            if(other.node.parent!==this.node.parent){
                continue;// 不在同一个父节点下,坐标不是同一套,没法算
            }

            var dx = other.node.x-this.node.x;
            var dy = other.node.y-this.node.y;
            var d = Math.sqrt(dx*dx+dy*dy);
            var rsum = ra+Math.min(other.vW,other.vH)*0.5*0.92;
            if(d>=rsum||d<0.001){
                continue;// 没碰上
            }

            // 从自己指向对方的单位向量,以及两者重叠了多少
            var nx = dx/d;
            var ny = dy/d;
            var overlap = rsum-d;

            if(this.dragging){
                // 我正被手抓着:我是"铁块",只把对方整根推开并给它一点速度
                other.node.x = other.node.x+nx*overlap;
                other.node.y = other.node.y+ny*overlap;
                other.vel = cc.v2(other.vel.x+nx*60,other.vel.y+ny*60);
                other.onHitWall('y',200);// 给对方一点被撞的效果
            }else if(other.dragging){
                // 对方被手抓着:我只负责被推开
                this.node.x = this.node.x-nx*overlap;
                this.node.y = this.node.y-ny*overlap;
                this.vel = cc.v2(this.vel.x-nx*60,this.vel.y-ny*60);
                this.onHitWall('y',200);
            }else{
                // 都不在手上:两个都弹开一半,再按等质量弹性碰撞交换一下速度
                this.node.x = this.node.x-nx*overlap*0.5;
                this.node.y = this.node.y-ny*overlap*0.5;
                other.node.x = other.node.x+nx*overlap*0.5;
                other.node.y = other.node.y+ny*overlap*0.5;

                // vn = 相对速度在"从我这指向对方"方向上的投影,大于 0 表示正在分开,不用管
                var vn = (other.vel.x-this.vel.x)*nx+(other.vel.y-this.vel.y)*ny;
                if(vn<0){
                    var j = -(1+this.bounciness)*vn*0.5;// 冲量大小(两个球质量一样,所以各分一半)
                    this.vel = cc.v2(this.vel.x-nx*j,this.vel.y-ny*j);
                    other.vel = cc.v2(other.vel.x+nx*j,other.vel.y+ny*j);
                    if(Math.abs(vn)>100){// 撞得够猛就压扁一下
                        this.onHitWall('y',Math.abs(vn));
                        other.onHitWall('y',Math.abs(vn));
                    }
                }
            }
        }
    },

    // 撞到屏幕四条边的处理
    collideBounds:function(dt){
        // 只看 contentSize 会忽略缩放,锚点不居中时还会把原点当成方框中心,两种情况都会凭空留出空隙
        var aw = this.vW*this.node.anchorX;
        var ah = this.vH*this.node.anchorY;
        var left = -this.halfW+aw;
        var right = this.halfW-this.vW*(1-this.node.anchorX);
        // 地面:再减掉贴图下方的透明留白,角色才能真的踩在屏幕底边
        var bottom = -this.halfH+ah-this.groundTrim;
        var top = this.halfH-this.vH*(1-this.node.anchorY);
        var hit = false;

        // 左右墙
        if(this.node.x<left){
            this.node.x = left;
            if(this.vel.x<0){
                this.vel.x = -this.vel.x*this.bounciness;
                this.onHitWall('x',Math.abs(this.vel.x));
            }
            hit = true;
        }else if(this.node.x>right){
            this.node.x = right;
            if(this.vel.x>0){
                this.vel.x = -this.vel.x*this.bounciness;
                this.onHitWall('x',Math.abs(this.vel.x));
            }
            hit = true;
        }

        // 天花板
        if(this.node.y>top){
            this.node.y = top;
            if(this.vel.y>0){
                this.vel.y = -this.vel.y*this.bounciness;
                this.onHitWall('y',Math.abs(this.vel.y));
            }
            hit = true;
        }

        // 地面:弹跳 + 摩擦
        if(this.node.y<bottom){
            this.node.y = bottom;
            if(this.vel.y<0){
                var impact = Math.abs(this.vel.y);
                this.vel.y = impact*this.bounciness;
                this.onHitWall('y',impact);
                // 弹得太小就别弹了,免得一直抖
                if(this.vel.y<60){
                    this.vel.y = 0;
                }
            }
            // 地面摩擦:贴地滑行时横向速度慢慢磨掉
            // (乘 dt 是为了不受帧率影响:60帧和30帧的磨擦量一致)
            var gdamp = 1-Math.min(0.95,this.groundFriction*dt);
            this.vel.x = this.vel.x*gdamp;
        }

        return hit;
    },

    // 撞墙时:按撞击强度给一个"压扁",并把旋转往静止方向拉
    onHitWall:function(axis,speed){
        var power = Math.min(1,speed/1600);
        if(power<0.06){
            return;
        }
        this.squashAxis = axis;
        this.squash = -0.45*power;// 负值 = 压扁
        this.squashVel = 0;
        this.spin = this.spin+speed*this.rotateFactor*(axis==='y'?1:-1)*0.5;
    },

    // 挤压弹簧:一个"从压缩回到 0"的弹簧运动
    // 弹簧公式:加速度 = -硬度*位移 - 阻尼*速度 (经典阻尼弹簧)
    stepSquash:function(dt){
        var acc = -this.squash*this.squashStiffness-this.squashVel*this.squashDamping;
        this.squashVel = this.squashVel+acc*dt;
        this.squash = this.squash+this.squashVel*dt;
    },

    // 把所有状态合成到节点的 scale / angle 上
    applyTransform:function(){
        var sx = this.baseScaleX;
        var sy = this.baseScaleY;

        // 挤压:压扁时"矮胖",拉长时"高瘦"
        if(this.squashAxis==='y'){
            sy = sy*(1+this.squash);
            sx = sx*(1-this.squash*0.75);
        }else{
            sx = sx*(1+this.squash);
            sy = sy*(1-this.squash*0.75);
        }

        // 待机呼吸:停下来的时候轻轻一鼓一鼓,像在喘气
        var sp = Math.sqrt(this.vel.x*this.vel.x+this.vel.y*this.vel.y);
        if(!this.dragging&&sp<120){
            var b = 1+Math.sin(this.t*this.breatheSpeed)*this.breatheAmp;
            sx = sx*b;
            sy = sy*b;
        }

        // 被抓住时放大一点,像"拎起来了"
        if(this.dragging){
            sx = sx*this.grabScale;
            sy = sy*this.grabScale;
        }

        this.node.scaleX = sx*this.spawn;
        this.node.scaleY = sy*this.spawn;
        this.node.angle = this.angle;
    },

    // --------------------------------------------------------------------------
    // 点击:立刻给反馈 + 立刻执行功能
    // --------------------------------------------------------------------------
    onTap:function(){
        this.playTapFeedback();
        if(this.dropGoal){
            this.doDropGoal();
        }else{
            this.doAddScore();
        }
    },

    // 点击的即时反馈:蹦起来 + 转一圈 + 光环
    playTapFeedback:function(){
        this.spawnRing();
        this.vel = cc.v2(0,this.tapJump);// 往上弹
        // 旋转量随机:大小和方向都随机,落地后停住的倾角才不会每次都一样
        // (旋转是按指数衰减的,总转过的角度约等于 初速度/衰减系数;
        //  原来初速度固定 620,总转过 620/1.8 ≈ 344°,几乎正好一整圈,
        //  所以每次停下来都像没转,看着完全一样)
        this.spin = (500+Math.random()*900)*(Math.random()<0.5?-1:1);
    },

    // 加分数
    doAddScore:function(){
        this.callHook('cheatAddScore',this.scoreBonus);
        this.spawnFloatText('+'+this.scoreBonus,cc.color(255,238,120,255));
    },

    // 让 goal 宝石落到最底下一行
    doDropGoal:function(){
        this.callHook('cheatDropGoal',this.goalColumn);
        this.spawnBurst();
        this.spawnFloatText('GOAL!',cc.color(255,150,150,255));
    },

    // 调用游戏侧提供的钩子。没有也绝不崩,只打一行日志
    callHook:function(name,arg){
        var fn = window[name];
        if(typeof fn==='function'){
            fn(arg);
            return true;
        }
        cc.log('[CheatButton] 没找到 '+name+',只播动画不作弊(见文件末尾注释)');
        return false;
    },

    // 脉冲光环:一个圆环从按钮中心扩散出去
    spawnRing:function(){
        var node = new cc.Node('ring');
        node.parent = this.node.parent;
        node.setPosition(this.node.x,this.node.y);
        node.zIndex = 49;
        var g = node.addComponent(cc.Graphics);
        g.lineWidth = 7;
        g.strokeColor = this.ringColor;
        g.circle(0,0,this.vW*0.5);// 在中心画个半径=按钮实际半径的圆
        g.stroke();
        node.scale = 0.5;
        cc.tween(node)
            .to(0.45,{scale:2.3,opacity:0},{easing:cc.easing.quadOut})
            .call(function(){
                node.destroy();
            })
            .start();
    },

    // 爆裂粒子:一圈小圆点飞出去
    // 注意这里用 for + 立即执行函数把每个 node"锁"住,
    // 否则闭包里拿到的永远是最后那一个(这个坑我们之前踩过)
    spawnBurst:function(){
        var count = 16;
        var that = this;
        for(var i = 0;i<count;i++){
            (function(index){
                var node = new cc.Node('spark');
                node.parent = that.node.parent;
                node.setPosition(that.node.x,that.node.y);
                node.zIndex = 49;
                var g = node.addComponent(cc.Graphics);
                var radius = 4+Math.random()*5;
                var c = that.ringColor;
                g.fillColor = cc.color(c.r,Math.max(0,c.g-30),Math.max(0,c.b-20),255);
                g.circle(0,0,radius);
                g.fill();

                // 均匀分布一圈角度,再叠一点随机,看着更自然
                var ang = (Math.PI*2/count)*index+Math.random()*0.35;
                var dist = 110+Math.random()*130;
                var tx = that.node.x+Math.cos(ang)*dist;
                var ty = that.node.y+Math.sin(ang)*dist;

                cc.tween(node)
                    .to(0.6,{x:tx,y:ty,opacity:0,scale:0.3},{easing:cc.easing.quadOut})
                    .call(function(){
                        node.destroy();
                    })
                    .start();
            })(i);
        }
    },

    // 飘字:在按钮上方冒出文字,弹出来 -> 停一下 -> 上飘淡出
    spawnFloatText:function(text,color){
        var node = new cc.Node('talk');
        node.parent = this.node.parent;
        node.setPosition(this.node.x,this.node.y+this.vH*0.7);
        node.zIndex = 51;
        var label = node.addComponent(cc.Label);
        label.useSystemFont = true;// 用系统字体,不依赖项目里的位图字体
        label.fontSize = 46;
        label.lineHeight = 46;
        label.string = text;
        node.color = color||cc.color(255,238,120,255);
        label.enableBold = true;
        node.scale = 0.4;
        cc.tween(node)
            .to(0.16,{scale:1.25})// 先"啪"地弹出来
            .to(0.1,{scale:1})
            .delay(0.25)
            .to(0.75,{y:node.y+200,opacity:0},{easing:cc.easing.quadOut})
            .call(function(){
                node.destroy();
            })
            .start();
    },

    // 拖尾:高速飞行时留下一串淡淡的重影
    spawnTrail:function(){
        var sprite = this.node.getComponent(cc.Sprite);
        if(!sprite||!sprite.spriteFrame){
            return;
        }
        var node = new cc.Node('trail');
        node.parent = this.node.parent;
        node.setPosition(this.node.x,this.node.y);
        node.zIndex = this.node.zIndex-1;
        var s = node.addComponent(cc.Sprite);
        s.spriteFrame = sprite.spriteFrame;
        s.sizeMode = cc.Sprite.SizeMode.CUSTOM;
        node.width = this.node.width;
        node.height = this.node.height;
        node.scaleX = this.node.scaleX;
        node.scaleY = this.node.scaleY;
        node.angle = this.node.angle;
        node.opacity = 70;
        cc.tween(node)
            .to(0.3,{opacity:0,scaleX:this.node.scaleX*0.6,scaleY:this.node.scaleY*0.6})
            .call(function(){
                node.destroy();
            })
            .start();
    }
});

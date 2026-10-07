# AGENTS.md — 交接说明（消消乐项目）

> 给 AI 编码助手的上下文交接单。**换电脑 / 开新会话后，请先读完这份文件再动手。**
> 这份文件由用户与上一个会话共同整理，记录了项目结构、用户要求、当前进度和踩过的坑。

---

## 0. 这是什么项目

用 **Cocos Creator 2.4.2** 开发的三消游戏「Smart 消消乐」，它是 GitHub 仓库 **TuWeixi** 里的一个子项目。

---

## 1. 位置与仓库

| 项 | 值 |
|---|---|
| GitHub 仓库 | https://github.com/091700/TuWeixi.git （分支 main） |
| 仓库根目录 | `D:\all task`（里面按文件夹放了多个项目） |
| 本项目目录 | `BestGameForever2/` |
| Cocos 工程根 | `BestGameForever2/BestGameForever2/`（用 Cocos Creator 2.4.2 打开**这一层**） |
| 脚本目录 | `BestGameForever2/BestGameForever2/assets/Scripts/` |
| 场景目录 | `BestGameForever2/BestGameForever2/assets/Scences/` |
| 截图目录 | `BestGameForever2/BestGameForever2/screenshot/` |
| 项目 README | `BestGameForever2/README.md` |

### 推送（重要）

本机直连 github.com:443 **不通**，必须走本机代理（上次是 7897 端口）：

```
git -c http.proxy=http://127.0.0.1:7897 push origin main
```

- **不要改 git 全局配置**，用 `-c` 临时传参
- 提交身份与仓库历史保持一致：
  `git -c user.name="TuWeixi" -c user.email="091700@users.noreply.github.com"`
- 换电脑后代理端口可能不同，先用
  `Test-NetConnection -ComputerName 127.0.0.1 -Port 7897` 确认，不通就问用户端口
- `.gitignore` 已排除 `library/`、`temp/`、`build/`、`local/`，以及 `settings/` 下的临时工程缓存

---

## 2. 用户的要求（每次都要遵守）

1. 用户是**代码新手**，语法薄弱 → 只写**最简单、最直白**的代码
2. **不要**防错漏 / 报错处理 / 防呆设计；**不要用** `? :` 三元表达式，一律写 `if/else`
3. 注释要**详尽**（中文），关键行都要有注释
4. 延续项目已有的 **MVC 架构**：Model 算数据、View 画画面、Controller 收输入
5. **默认不要直接改用户的代码文件**：把完整代码发给用户，用户自己抄进去；只有用户明确说"你帮我改"时才动文件
6. 场景和属性（预制体引用、节点位置等）由用户在 Cocos 编辑器里操作，AI 只给步骤
7. 界面偏好：QQ 气泡框风格；美术资源与主体形象一致；README 截图区只保留标题 + 图片 + 简短功能名，不写尺寸标注

---

## 3. 项目结构与已完成功能

- 设计分辨率 720×1280，纯 JavaScript，4 个场景：

| 场景 | 脚本 | 说明 |
|---|---|---|
| StartScene | StartController / StartView / StartModel + BtnMove / BtnChange / DimondChange | 开始界面 |
| LevelSelectScene | LevelSelectController / LevelSelectView / LevelSelectModel | 世界选择（8 个 WORLD，每页 4 个） |
| WaveSelectScene | WaveSelectController / WaveSelectView / WaveSelectModel | 关卡选择（每世界 99 关，每页 9 关） |
| BestGameScene | BestGameController / BestGameView / BestGameModel + GamePause | 三消主场景 |

- 核心玩法脚本在 `assets/Scripts/BestGameScene/`：
  - **BestGameModel.js**：7×9 棋盘、6 种宝石、三连判定 `hasMatch`、收集 `collectMatches`、消除下落 `clearAndFall`、交换 `tryChange`；格子有 0~3 级耐久，全降到 0 即胜利
  - **BestGameView.js**：`refresh` 重画棋盘；`playChangeAnim` 交换动画；`playClearAnim`/`playNextStep`/`playStep` 消消+下落动画；`playHand` 手指提示；`showGoalGem` 胜利宝石
  - **BestGameController.js**：`bindBoard` 触摸；`doChange` 交换流程；`refreshBoard` 刷新+推进教程；倒计时在 `update`
- 已完成：交换动画、无效交换滑回、消除 + 下落 + 连锁动画、三步新手引导（Tip1/Tip2 共用一张棋盘，Tip3 胜利弹窗）、420 秒倒计时 + 进度条、计分与 localStorage 存档、暂停面板
- **节点命名约定**（动画全靠名字找节点）：宝石节点 `gem_行_列`，背景节点 `bg`，正在消失的宝石临时改名 `dead`

---

## 4. 当前进度与下一步

**已完成到**：消除 + 下落动画跑通（Model 把每一步记录进 `this.steps`，View 用 `playStep` 逐步回放）。

**待做（用户还没抄进去）**：把 `BestGameView.js` 的 `playStep` 换成下面这版。
要解决的问题：下落时宝石被棋盘（后面的行/格子背景）盖住、看着像瞬移。原理：Cocos 里**后添加的节点画在上面**，而 `refresh()` 是从上往下一行行创建的，所以上排的宝石层级最低。修法是给"正在动的宝石"设 `zIndex = 1`（比静止的 0 大），并让动画时长按距离计算。

```js
    //演一步:该消的宝石缩小消失,该掉的宝石同时往下掉
    playStep:function(step){
        var that = this;
        var model = this.model;
        var SPEED = 1200;              //下落速度:每秒掉多少像素(数字越大掉得越快)
        var MIN_TIME = 0.15;           //每段动画最少演0.15秒,免得快得看不清
        var DROP_Y = model.TOP_Y+150;  //新宝石从棋盘上方这个高度开始掉
        var stepTime = MIN_TIME;       //这一步一共演多久,先按最短时间算

        //(1)消掉的宝石:先记到一个数组里,等这一步演完再统一删
        this.deadList = [];
        for(var i = 0;i<step.cleared.length;i++){
            var cr = step.cleared[i][0];
            var cl = step.cleared[i][1];
            var dead = this.Board.getChildByName('gem_'+cr+'_'+cl);
            dead.name = 'dead';        //马上改名,免得和掉下来的宝石重名
            dead.zIndex = 1;           //正在动的宝石,画在静止的宝石上面
            this.deadList.push(dead);  //先记下来
            cc.tween(dead)
                .to(MIN_TIME,{scale:0})
                .start();
        }

        //(2)要掉的宝石:滑到新格子
        for(var j = 0;j<step.falls.length;j++){
            var f = step.falls[j];
            var x = model.cellX(f.c);
            var y = model.cellY(f.toR);
            var node = null;

            if(f.fromR>=0){
                //本来就在棋盘上的宝石:改名,等下滑下去
                node = this.Board.getChildByName('gem_'+f.fromR+'_'+f.c);
                node.name = 'gem_'+f.toR+'_'+f.c;
            }
            else{
                //新生成的宝石:先放在棋盘上方
                node = new cc.Node('gem_'+f.toR+'_'+f.c);
                node.parent = this.Board;
                node.setPosition(x,DROP_Y);
                var sp = node.addComponent(cc.Sprite);
                sp.spriteFrame = this.gemFrames[this.gemIndex(f.gem)];
                node.width = 90;
                node.height = 90;
            }

            //掉得远就多花点时间,这样才像真的在"掉",而不是一下子闪过去
            var dist = Math.abs(y - node.y);
            var t = dist / SPEED;
            if(t < MIN_TIME){
                t = MIN_TIME;
            }
            if(t > stepTime){
                stepTime = t;              //记住最久的那一颗,整步要等它演完
            }

            node.zIndex = 1;               //正在动的宝石,画在静止的宝石上面
            cc.tween(node)
                .to(t,{x:x,y:y})
                .start();
        }

        //(3)这一步演完(按最久的那颗算):删掉消失的宝石,再演下一步
        this.scheduleOnce(function(){
            for(var k = 0;k<that.deadList.length;k++){
                that.deadList[k].destroy();
            }
            that.playNextStep();
        },stepTime);
    },
```

判断有没有抄进去：在 BestGameView.js 里搜 `zIndex`，搜不到就是还没应用。

---

## 5. 踩过的坑（新会话务必先看）

1. **用户手抄代码极易拼错单词**。给完代码后主动提醒自查这几个词：
   `destory`→`destroy`、`geet`→`get`、`cleaered`→`cleared`、`callX`→`cellX`、`thst`→`that`、`plst`→`play`、`feomR`→`fromR`
2. **报错定位规律**：
   - `xxx is not a function` → 名字对不上（拼错 or 函数不存在）
   - `Cannot read properties of null/undefined (reading 'yyy')` → 那个东西不存在/没赋值，去报错行看用到的变量
   - 控制台**第一条**错误往往才是真正的源头，后面的多是连锁反应
3. **`var` 在 for 循环里 + 回调函数**是经典坑：所有回调共用同一个变量，循环结束后它已经是最后一个值。要删的节点先塞进数组，最后统一处理（`playStep` 就是这么改的）
4. **场景里的资源引用会失效**：若点击某按钮后场景加载不了、控制台报 `assets/main/import/xx/xxxx.json 404`，说明场景里引用了**被重建过、UUID 变了**的资源。在编辑器里找到那个属性重新拖一次资源即可。
   已修过一次：`WaveSelectScene` 的 `gamePagePrefab` → `assets/resources/YuZhijian/GameScene/Page.prefab`（旧 UUID `67bd5961-...` 失效，新 UUID `516ff12d-...`）
5. `collectMatches` 对 **L 形 / T 形**会把拐角格子记两次，所以 `clearAndFall` 里往 `step.cleared` 存之前要去重
6. `creator.d.ts` 是 Cocos 自动生成的类型声明（3 万多行），只给编辑器做提示用，**不参与运行，也不要手改**

---

## 6. 常用自查命令

```powershell
# 扫拼写错误（无输出就是干净）
Select-String -Path "assets\Scripts\BestGameScene\*.js" -Pattern "destory|geet|cleaered|callX|thst|plst|feomR"

# 看有没有未提交的改动
git status --short

# 提交并推送
git add BestGameForever2
git -c user.name="TuWeixi" -c user.email="091700@users.noreply.github.com" commit -m "说明"
git -c http.proxy=http://127.0.0.1:7897 push origin main
```
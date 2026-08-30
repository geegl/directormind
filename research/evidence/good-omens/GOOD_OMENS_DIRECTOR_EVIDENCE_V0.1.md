# Good Omens导演参考证据 v0.1

用途：为通用 Director Grammar 提供第一批候选迁移证据。它不是对参考剧导演意图的断言，也不是复制镜头的许可。

## 证据层级

- `OBSERVED`：用户上传视频的分析报告给出了可见/可听镜头事实与Shot ID。
- `INFERRED`：从镜头组合推断的叙事功能。
- `METHOD_REFERENCE`：DirectorSkills教材方法提供决策语言，不证明参考剧有意使用该方法。
- `UNKNOWN`：没有原视频或真实关键帧供本任务逐帧复核的项目。

## 已接受主证据

### GO-S2E1-BOOKSHOP

来源：用户合法提供的本地片段分析报告 `GO-S2E1-BOOKSHOP`。原视频、关键帧和本地附件不进入公开仓库。

实际作品是`Good Omens S02E01`，不是报告标题中的S02E02。可用区段包括：

- S36–S39：道歉舞的准备、完整动作和观察者反应；
- S46–S56：Jim进入后，双人联盟与第三人的两加一调度；
- S57–S63：三人仪式站位与高/俯角奇迹镜头；
- S70–S72：Jim称两人为朋友后，Crowley否认与Aziraphale反应。

审计修正：

- 提出隐藏Jim和“一人一半奇迹”的推动者是Aziraphale；报告部分Shot把主动者写成Crowley。
- `Top-Down`是角度，不是摄影机运动。
- 报告中的三个高/俯角镜头来自同一仪式序列，不能证明“所有魔法必然俯拍”。
- 室内静止镜头按表格应为71/75；Pan 2/75，Tilt 2/75。

### GO-S1E3-BANDSTAND

来源：用户合法提供的本地片段分析报告 `GO-S1E3-BANDSTAND`。原视频、关键帧和本地附件不进入公开仓库。

可用区段包括：

- S27–S30：从谈崩、转身到“一起离开”的邀请；
- S31–S34：邀请、拒绝和受伤反应的Clean Single；
- S35–S40：接受决裂、离场和留守空间。

审计修正：

- 原报告的三处说话人归属已按视频顺序纠正；公开版本不保留连续对白。
- 总时长是153.2秒；平均3.83秒；中位数3.5秒。
- Static为35/40；含Pan/Tilt/Dolly的运镜镜头为4/40；Rack Focus报告为1/40。
- S39是否真有焦点转换尚未逐帧验证。若焦点始终锁在后景Aziraphale，它只是前景穿行与后景持焦。
- 决裂后仍有OTS，不能写成“全面停止OTS”。

## 支持证据

### GO-S2E1-MAGGIE-BENCH

来源：用户合法提供的本地片段分析报告 `GO-S2E1-MAGGIE-BENCH`。原视频、关键帧和本地附件不进入公开仓库。

接受：并排I型调度、稳定机位、荒谬台词后的延迟反应、日常环境声。拒绝：把普通静止场面映射为`shot-still-vs-motion-decision`；该方法只用于决定性动静转换。

### GO-S1E4-THREAT

来源：用户合法提供的本地片段分析报告 `GO-S1E4-THREAT`。原视频、关键帧和本地附件不进入公开仓库。

接受：轴线外日常人物打断、全员视线转移、固定 aftermath、受压者反应。拒绝：原报告的移动比例和“100% OTS”泛化；该序列包含全景、群体反应与Clean Single。

## DirectorSkills方法边界

采用的少量方法ID：

- `shot-design-axis-of-action`
- `shot-design-dialogue-staging`
- `shot-design-sightline-cut`
- `shot-design-continuity-composition`
- `shot-design-pov-spectrum`
- `directing-reaction-over-action`
- `directing-dramatic-irony`（仅在观众确实知道角色不知道的信息时）
- `shot-camera-choreography`
- `shot-still-vs-motion-decision`（仅在决定性动静转换时）

DirectorSkills仓库自身的路由测试报告对多项Skill标记为FAIL；这反映自动路由质量，不自动否定教材内容，但要求本项目只把它们当作`METHOD_REFERENCE`，不作为镜头事实或权威评分。

## UNKNOWN

- 本任务没有直接读取用户上传的视频或真实逐镜关键帧，无法独立确认运镜、焦点变化和音乐进入的每个时间点。
- 参考报告中的摄影机设备、焦距、实体Dolly与数码推近均不可确认。
- 所有跨剧迁移规则都必须经过原创锁定剧本的前向测试；在测试前不得升级为生产定律。

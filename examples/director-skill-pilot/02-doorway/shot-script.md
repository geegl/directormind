# EP32 导演分镜 v0.2

- 来源：`examples/director-skill-pilot/02-doorway/locked-script.md`
- 状态：`HUMAN_REVIEW_PENDING`
- 规格：16:9｜目标 48 秒
- 执行媒介：`AI_PHOTOREAL_HUMAN`
- 生成授权：`false`
- 视觉风格包：`None`

> 本文由Director IR确定性渲染；JSON是单一事实源。原剧本对白和可见文字保持锁定。

## EP32-SC01｜门还开着｜48秒

**场景目标：** 先让争执由两人的可见反应交接，再让一次走向门口的行动改变谈话关系。

**POV：** MEI / 靠近梅，但同时保留余是否离开的可见选择。

**空间：** 两椅隔1.4米，梅左余右，北墙门在右后方；梅的椅子处在通往门口的直线上。；轴线：开场两椅连线，摄影机在南侧；门口全景可见移动全过程，在新端点后才恢复单人机位。

| 镜头 | 秒 | 叙事功能 | 景别/机位/运动 | 调度与表演 | 锁定对白/文字 | 声音与衔接 | 执行/参考 | 规则 | AI风险/降级 |
|---|---:|---|---|---|---|---|---|---|---|
| EP32-SC01-SH01 | 7 | 先交代椅子为什么会成为之后的障碍，让后面的挪椅子有意义。 | 双人中景<br>START: 南侧35mm等效，镜头高1.2米，平视。<br>PATH: LOCKED / NONE / NONE / NONE<br>END: 南侧35mm等效，镜头高1.2米，平视。 | 梅手抓椅背；余双手合拢，身体朝梅。<br>0–2秒：建立坐姿与门。；2–6秒：梅质问。；6–7秒：余手开始松开。 | MEI: 你把钥匙留下，就算说完了？ | AUDIO: PROJECT_ORIGINAL_ONLY: 按锁定原文收录对白；保留现场动作声，不用新增音乐提示人物结论。<br>AUDIO REF: locked-script.md#BEAT-01<br>IN: 直接开在二人坐定的关系里。<br>OUT: 余掌心开始松开时切她。 | BASE: AI_VIDEO<br>POST: —<br>STATE: —<br>REF: SHOT_GOLDEN/PLANNED | — | 摄LOW/表MEDIUM/连MEDIUM |
| EP32-SC01-SH02 | 8 | 按可见状态接话，不在每个短句上改机位；摊手从防守变成让对方听。 | 余的中近景<br>START: 南侧50mm等效，保持门在背景右边。<br>PATH: LOCKED / NONE / NONE / NONE<br>END: 南侧50mm等效，保持门在背景右边。 | 余摊手后说话，坐姿保持。<br>0–2秒：摊手完成。；2–6秒：回答。；6–8秒：看着梅。 | YU: 你每次都先替我说完。 | AUDIO: PROJECT_ORIGINAL_ONLY: 按锁定原文收录对白；保留现场动作声，不用新增音乐提示人物结论。<br>AUDIO REF: locked-script.md#BEAT-01<br>IN: 接同一个摊手动作。<br>OUT: 话后眼神落稳，切梅的手与脸。 | BASE: AI_VIDEO<br>POST: —<br>STATE: —<br>REF: NONE/NOT_REQUIRED | DR-STABLE-AXIS-STATE-LED-HOLDS | 摄LOW/表MEDIUM/连MEDIUM |
| EP32-SC01-SH03 | 7 | 宁可让松手占三秒，也不插门口空镜；这里权力变化发生在梅放弃代答。 | 梅的中近景<br>START: 南侧相对机位50mm等效，保持开场左右关系。<br>PATH: LOCKED / NONE / NONE / NONE<br>END: 南侧相对机位50mm等效，保持开场左右关系。 | 梅放开椅背，再改口。<br>0–3秒：松手。；3–5秒：短句。；5–7秒：等余。 | MEI: 那你说。 | AUDIO: PROJECT_ORIGINAL_ONLY: 按锁定原文收录对白；保留现场动作声，不用新增音乐提示人物结论。<br>AUDIO REF: locked-script.md#BEAT-02<br>IN: 余的状态完成后接梅。<br>OUT: 余在画外起身发出衣料响动时转共享全景，起身仍要在下一镜看见。 | BASE: AI_VIDEO<br>POST: —<br>STATE: —<br>REF: NONE/NOT_REQUIRED | DR-STABLE-AXIS-STATE-LED-HOLDS | 摄LOW/表MEDIUM/连MEDIUM |
| EP32-SC01-SH04 | 15 | 人物从可争论的距离走到可离开的距离；全景重建这个事实，不能靠两个新特写让观众猜位置。 | 门、两人和路径的双人全景<br>START: 同南侧后退约1.5米，28–35mm等效，预留门口端点。<br>PATH: LOCKED / NONE / NONE / NONE<br>END: 同南侧后退约1.5米，28–35mm等效，预留门口端点。 | 余在镜内起身、绕椅、走到门内停；梅留在原椅旁。<br>0–3秒：余起身。；3–8秒：绕椅走向门。；8–10秒：门内停。；10–13秒：说话。；13–15秒：两人端点停住。 | YU: 我今天没有力气了。 | AUDIO: PROJECT_ORIGINAL_ONLY: 按锁定原文收录对白；保留现场动作声，不用新增音乐提示人物结论。<br>AUDIO REF: locked-script.md#BEAT-03<br>IN: 切在起身开始前，完整保留移动。<br>OUT: 余停稳且一句说完后，同机位不中断进入下一叙事段，注意力转向梅挪椅子。 | BASE: AI_VIDEO<br>POST: —<br>STATE: —<br>REF: NONE/NOT_REQUIRED | DR-RELATION-RESET-AFTER-SPATIAL-CHANGE | 摄LOW/表MEDIUM/连HIGH<br>降级：改为固定侧面宽双人镜头，缩短原场景内两椅到门的拍摄布局但保留先绕椅、再到门口的顺序和端点；整段不使用跟拍或跨轴拼接。 |
| EP32-SC01-SH05 | 11 | 用让出通道给余真正选择；不切余的孤立眼泪，把出口和梅同时留在画中。 | 同侧宽双人镜头<br>START: 复用上一镜机位；通过表演节奏承接，不换到反面。<br>PATH: LOCKED / NONE / NONE / NONE<br>END: 复用上一镜机位；通过表演节奏承接，不换到反面。 | 梅把椅子挪到左墙，说话；余回头，仍在门内。<br>0–4秒：梅起身挪椅。；4–7秒：梅说话。；7–9秒：余回头。；9–11秒：留出畅通出口与未作的决定。 | MEI: 我没要你今天留下。 | AUDIO: PROJECT_ORIGINAL_ONLY: 按锁定原文收录对白；保留现场动作声，不用新增音乐提示人物结论。<br>AUDIO REF: locked-script.md#BEAT-04<br>IN: 同一空间连续承接，实际拍摄可连拍与上一镜合成26秒段，剪辑保留决策端点。<br>OUT: 余回头停两秒，硬切；不补走回去。 | BASE: AI_VIDEO<br>POST: —<br>STATE: —<br>REF: NONE/NOT_REQUIRED | DR-RELATION-RESET-AFTER-SPATIAL-CHANGE | 摄LOW/表MEDIUM/连MEDIUM |

**场景结束状态：** 梅把椅子移开，余在敞开的门内停住；两人间距约3米，路径畅通。

## 待人工确认

- 本样例为原创作者固定文本，尚未获用户导演审看批准。
- 时长为剪辑设计预算，未做真人围读或实拍测试。
- 焦段与机位是本原创场景的设计选择，不是参考影片摄影参数。

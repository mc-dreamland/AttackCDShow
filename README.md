# AttackCDShow

网易基岩版 ModSDK（Python 2.7）的服务端触发式攻击 CD 显示组件。正式行为包为 `attackcdshow_behavior_pack`，资源包为 `attackcdshow_resource_pack`；`AttackCoolDown/` 只作为原型参考。

## 用途

服务端业务在特殊情况中指定一个冷却时长，客户端模拟 Java 风格的攻击充能显示。**这不是原版攻击冷却机制的移植**：

- 没有原版物品攻速表或默认 CD。
- 普通攻击、空挥、换手、破坏方块、死亡及重生不会自动触发或重置显示。
- 客户端不监听攻击输入，也不向服务端请求 CD 状态。
- 服务端不维护本组件的计时状态，不逐帧下发进度。
- 不改变伤害、攻击权限、横扫或基岩版引擎攻速。实际战斗规则由调用方控制。

## 服务端调用

两端系统的 `Setup` 已注册模块。特殊业务明确调用以下接口，时长单位为**秒**：

```python
import mod.server.extraServerApi as serverApi

system = serverApi.GetSystem("AttackCDShow", "AttackCDShowServerSystem")

# 只在需要显示特殊 CD 的业务分支中调用。
system.AttackCooldownServerModule.StartCooldown(playerId, 0.8)

# 发送 0 清除当前进度条。
system.AttackCooldownServerModule.StartCooldown(playerId, 0)
```

`StartCooldown(playerId, cooldownSeconds)` 的时长参数必须显式提供。有限非负数字有效，非法时长抛出 `ValueError`；离线玩家返回 `False`，在线玩家发包后返回 `True`。此返回值不代表客户端确认收到。调用方应在客户端脚本加载完成后发送，不能依赖加入早期的通知。

也可从 `AttackCDShow` 服务端系统直接定向发送相同协议：

```python
system.NotifyToClient(playerId, "AttackCooldown", {"cooldown": 0.8})
```

## 唯一发包协议

命名空间为 `AttackCDShow`，发送系统为 `AttackCDShowServerSystem`，事件名为 `AttackCooldown`。定向目标由 `NotifyToClient` 指定，包内只有冷却时长：

```python
{"cooldown": 0.8}  # 秒
```

不发送 `playerId`、序号、剩余时间或进度；没有客户端 ready/空挥上报，也没有结束包或状态补发。客户端从收包时开始，按其 30 Hz 脚本 `Update` 本地推进；进度为 `1 - 剩余时间 / 总时间`。

## 覆盖与显示规则

**每个新时长包都视为一次新的冷却触发**，立即替换旧时长、进度归零，再按新时长填满。采用 Java 再次攻击的重置语义，不叠加、不取最长值，也不是“只修改攻击速度属性但保留已累计时间”的模式。

- 相同时长再次下发：重新开始，不忽略重复值。
- 2 秒 CD 进行中收到 0.5 秒：归零后开始新的 0.5 秒 CD。
- 短 CD 中收到长 CD：归零后开始新的长 CD。
- 收到 0：立即清除显示；之后正时长包可以重新启动。
- 以包到达顺序覆盖；协议没有序号，不能判断尚未到达的旧通知。

第一人称准心下只显示 16×4 充能条，冷却期间不要求瞄准目标。冷却完成或收到 0 后立即隐藏，不显示任何就绪标记，也不进行目标或生命值检测。未收到 CD 时不显示。

充能条填充部分使用 `ui/attack_cooldown.json` 中 `filled_progress_bar.color: [0.65, 0.65, 0.65]` 降低颜色强度，避免原始白色过亮；不降低透明度、不改变空槽。调整这三个相同的 RGB 系数可统一变亮或变暗。

UI 尚未创建、UI 重建或第三人称隐藏期间，冷却仍推进；创建/重建 UI 只绘制当前进度，不重启或额外推进计时。HUD 节点只渲染，计时的唯一所有者是客户端模块。客户端逻辑帧停滞会延长实际墙钟时长；该显示不能作为服务端战斗判定依据。

## 加载与验证

在网易开发工作台中加载正式行为包和资源包；项目命名空间为 `attackcdshow`。`update.bat` / `python packme.py` 用于打包正式两包，不包含嵌套原型包。

已用 Python 2.7.18 的临时模拟 SDK 场景运行正式两端系统及 HUD 节点，覆盖：仅时长定向包、无原生自动触发或逐帧包、无客户端上报、UI 创建前计时、相同时长重置、长短时长双向覆盖、隐藏视角计时、完成后持续隐藏、零清除、极短时长、延迟 UI 创建/重建、创建失败恢复及完整解绑。移除就绪标记后另已验证只剩冷却条控件、贴图删除、亮度设置保留，且不需要目标检测接口。临时脚本不随包发布。

模拟 SDK 不证明引擎实机绘制。进度条裁剪、原生输入穿透和 F1 / `HideHudGUI` 对自定义 HUD 的自动隐藏仍需实机验证；未添加未经证实的隐藏查询接口或绑定。

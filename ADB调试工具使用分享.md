# 《ADB 调试工具》使用分享

## 一、环境准备

### 1.1 下载与安装

ADB（Android Debug Bridge）随 **Android SDK Platform-Tools** 一起发布，不需要装完整 Android Studio。

- 官方下载地址：https://developer.android.com/tools/releases/platform-tools
- Windows 选 `platform-tools-latest-windows.zip`

下载后解压到一个固定目录，例如：
```
C:\platform-tools\
```

解压后目录里应包含：`adb.exe`、`fastboot.exe`、`AdbWinUsbApi.dll`、`AdbWinApi.dll`。

### 1.2 配置环境变量（Windows）

把 `adb.exe` 所在目录加进 PATH，这样在任意目录都能直接敲 `adb`。

1. 右键「此电脑」→ 属性 → 高级系统设置 → 环境变量
2. 在「系统变量」里找到 `Path`，双击编辑
3. 新建一条，填入 `C:\platform-tools\`

```
┌─ 环境变量 / Path 编辑界面（示意）──────────────────────┐
│  %SystemRoot%\system32                               │
│  %SystemRoot%                                        │
│  C:\platform-tools\   ← 新增这一行（红框标注）         │
│  [ 新建 ]  [ 编辑 ]  [ 删除 ]  [ 浏览 ]                │
└──────────────────────────────────────────────────────┘
```

### 1.3 验证安装

打开新的命令行窗口（旧窗口不会刷新 PATH），执行：

```bash
adb version
```

预期回显：

```text
Android Debug Bridge version 1.0.41
Version 35.0.1-11580240
Installed as C:\platform-tools\adb.exe
```

看到版本号即安装成功。若提示「不是内部或外部命令」，说明 PATH 没生效，检查 1.2 步骤。

### 1.4 手机端开启调试

手机要能被电脑识别，需打开「USB 调试」：

1. 设置 → 关于手机 → 连续点「版本号」7 次，开启开发者模式
2. 返回 → 系统/更多设置 → 开发者选项 → 打开「USB 调试」
3. USB 连接方式选「传输文件（MTP）」

```
┌─ 开发者选项（示意）────────────────────────────────────┐
│ ☑ USB 调试            ← 打开（红框标注）               │
│ ☑ USB 安装                                           │
│ ☑ 无线调试                                           │
└──────────────────────────────────────────────────────┘
```

插上数据线，手机弹出「是否允许 USB 调试」时，勾选「一律允许」并点确定。

---

## 二、核心功能演示

### 2.1 功能一：查看已连接设备 `adb devices`

这是所有操作的第一步——先确认电脑认到了设备。

```bash
adb devices
```

正常回显（设备已授权）：

```text
List of devices attached
emulator-5554	device
```

常见三种状态：

```text
List of devices attached
emulator-5554	device        ← 已连接且已授权，可用
8AHX1LPHC1745	unauthorized  ← 手机上没点"允许"，需去手机确认
8AHX1LPHC1745	offline       ← 连接异常，重插线或 adb kill-server
```

> 多台设备时，后续命令要加 `-s <序列号>`，例如 `adb -s emulator-5554 install app.apk`。

### 2.2 功能二：安装应用 `adb install`

把电脑上的 APK 装进设备。

```bash
adb install C:\Downloads\wechat.apk
```

成功回显：

```text
Performing Streamed Install
Success
```

常用参数：

| 命令 | 作用 |
|------|------|
| `adb install app.apk` | 普通安装，已存在则报错 |
| `adb install -r app.apk` | 覆盖安装（保留数据） |
| `adb install -t app.apk` | 允许安装 testOnly 包 |
| `adb install -d app.apk` | 允许降级安装 |

```
┌─ 安装过程（示意）─────────────────────────────────────┐
│ > adb install -r C:\Downloads\wechat.apk             │
│ Performing Streamed Install                          │
│ Success   ← 看到这行即安装成功（绿字/红框标注）         │
└──────────────────────────────────────────────────────┘
```

### 2.3 功能三：进入设备 Shell `adb shell`

`adb shell` 让你直接在设备里执行 Linux 命令，是排查问题的主战场。

```bash
adb shell
```

进入后提示符变成设备名：

```text
emulator-5554:/ $ 
```

常用 shell 命令：

```bash
# 查看已安装包名
pm list packages

# 查看某个包的路径
pm path com.tencent.mm

# 查看设备型号
getprop ro.product.model

# 查看屏幕分辨率
wm size

# 退出 shell
exit
```

一次性执行（不进入交互模式）：

```bash
adb shell pm list packages | findstr tencent
```

回显：

```text
package:com.tencent.mm
package:com.tencent.mobileqq
```

### 2.4 功能四：查看日志 `adb logcat`

实时抓取系统与应用日志，排查崩溃、ANR 必备。

简单使用——清屏后实时看日志：

```bash
adb logcat -c   # 清空旧日志
adb logcat      # 持续输出，Ctrl+C 退出
```

按关键字过滤（只看某个包的 Error 级日志）：

```bash
adb logcat -v time *:E | findstr com.tencent.mm
```

回显示例：

```text
07-16 14:22:03.441 E AndroidRuntime: FATAL EXCEPTION: main
07-16 14:22:03.441 E AndroidRuntime: Process: com.tencent.mm, PID: 12345
07-16 14:22:03.441 E AndroidRuntime: java.lang.NullPointerException
```

导出日志到文件（方便发给同事）：

```bash
adb logcat -d > C:\logs\device.log
```

常用 logcat 缓冲区分级：

| 级别 | 含义 |
|------|------|
| V | Verbose 最详细 |
| D | Debug 调试 |
| I | Info 信息 |
| W | Warn 警告 |
| E | Error 错误 |
| F | Fatal 致命 |

### 2.5 功能五：卸载应用 `adb uninstall`

```bash
adb uninstall com.tencent.mm
```

成功回显：

```text
Success
```

只卸载但保留数据目录（恢复出厂用）：

```bash
adb uninstall -k com.tencent.mm
```

> 卸载用的是**包名**（如 `com.tencent.mm`），不是 APK 文件名。包名用 `pm list packages` 查。

---

## 三、实战示例

### 3.1 项目背景

测试同事发来 `demo-app.apk`，需要在 3 台设备上验证能否正常启动。我们用 ADB 批量完成：装包 → 确认装好 → 抓启动日志 → 验证完后卸载。

### 3.2 完整操作流程

**第 1 步：确认设备在线**

```bash
adb devices
```

```text
List of devices attached
emulator-5554	device
8AHX1LPHC1745	device
```

**第 2 步：覆盖安装（保留旧数据，避免重复登录）**

```bash
adb install -r C:\Downloads\demo-app.apk
```

```text
Performing Streamed Install
Success
```

**第 3 步：确认包已安装**

```bash
adb shell pm list packages | findstr demo
```

```text
package:com.example.demoapp
```

**第 4 步：启动应用并抓取崩溃日志**

```bash
adb logcat -c
adb shell am start -n com.example.demoapp/.MainActivity
adb logcat -d *:E > C:\logs\demo-start.log
```

`am start` 回显：

```text
Starting: Intent { cmp=com.example.demoapp/.MainActivity }
```

**第 5 步：测试完卸载**

```bash
adb uninstall com.example.demoapp
```

```text
Success
```

### 3.3 最终结果

打开 `C:\logs\demo-start.log`，无 E 级日志，说明启动过程无崩溃，验收通过。三台设备重复 2~5 步即可。

```
┌─ 验收结论（示意）──────────────────────────────────────┐
│ C:\logs\demo-start.log                                  │
│ 总行数: 0 条 Error   ← 启动无异常（红框标注）           │
│ 结论: 应用正常启动，验收通过                            │
└──────────────────────────────────────────────────────┘
```

---

## 四、踩坑记录

### 坑 1：`adb devices` 显示 `unauthorized`

**现象**：设备连上但状态是 `unauthorized`，所有命令都报错。
**原因**：手机没弹「允许 USB 调试」或没勾「一律允许」。
**解决**：拔线重插，手机上点「允许」并勾选一律允许；仍不行执行：

```bash
adb kill-server
adb start-server
adb devices
```

### 坑 2：`adb install` 报 `INSTALL_FAILED_ALREADY_EXISTS`

**现象**：`Failure [INSTALL_FAILED_ALREADY_EXISTS: Attempt to re-install ... without first uninstalling]`
**原因**：设备上已装同名包。
**解决**：加 `-r` 覆盖安装，或先 `adb uninstall <包名>`。

### 坑 3：`adb install` 报 `INSTALL_FAILED_VERSION_DOWNGRADE`

**现象**：装低版本 APK 失败。
**解决**：加 `-d` 允许降级：`adb install -d app.apk`。

### 坑 4：提示 `adb server version (31) doesn't match this client (41)`

**现象**：客户端与后台 server 版本不一致。
**原因**：电脑上有多个 adb（如手机助手、模拟器自带）。
**解决**：杀掉所有 adb，统一用一个版本：

```bash
adb kill-server
taskkill /f /im adb.exe
# 重新用 C:\platform-tools\adb.exe 执行命令
```

### 坑 5：logcat 输出太多刷屏看不到关键

**解决**：加级别过滤 + 关键字，例如只看某包 Error：

```bash
adb logcat -v time *:E | findstr com.example.demoapp
```

### 坑 6：无线调试连不上

**现象**：`adb connect 192.168.1.100:5555` 失败。
**解决**：手机和电脑同一 WiFi；手机开发者选项开「无线调试」并点「使用配对码配对」；先用配对码配对，再 connect。

---

## 五、总结

### 优点

- 谷歌官方工具，免费、跨平台（Win/Mac/Linux）
- 无需 root 即可完成安装、调试、日志抓取
- 命令化，可写脚本批量操作多设备
- 与 Android Studio、模拟器无缝配合

### 缺点

- 纯命令行，新手需要记忆命令
- 部分功能（如修改系统设置）需 root
- 多设备/版本冲突时排查较烦

### 适用场景

- 真机/模拟器上快速安装、卸载、调试应用
- 抓取崩溃日志排查 bug
- 自动化测试脚本（配合 `am`、`pm`、`input` 等 shell 命令）
- 设备批量部署与验收

---

### 命令速查表

| 功能 | 命令 |
|------|------|
| 查看设备 | `adb devices` |
| 安装（覆盖） | `adb install -r app.apk` |
| 卸载 | `adb uninstall 包名` |
| 进 shell | `adb shell` |
| 查包名 | `adb shell pm list packages` |
| 实时日志 | `adb logcat` |
| 导出日志 | `adb logcat -d > log.txt` |
| 启动应用 | `adb shell am start -n 包名/Activity` |
| 重启服务 | `adb kill-server && adb start-server` |

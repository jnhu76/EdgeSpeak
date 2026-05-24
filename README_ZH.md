# EdgeSpeak

[English](README.md)

跨平台桌面文字转语音工具，基于 Microsoft Edge TTS。

使用 Python + pywebview (原生 WebView2) 构建，工具箱风格界面。

## 功能

### 语音与语言

- **7 种语言**：英语、中文、日语、韩语、法语、俄语、西班牙语
- **口音筛选**：按地区口音过滤语音（如 en-US、en-GB、zh-CN、zh-TW）
- **语音列表**：可滚动的语音列表，显示性别和类别标签，点击选择
- **语言切换**：运行时切换界面语言（中文 / English）

### 音频生成

- **可调参数**：语速（-50% ~ +100%）、音调（-50Hz ~ +50Hz）、音量（-50% ~ +50%）
- **速度预设**：一键切换 0.5x / 1x / 1.5x / 2x
- **重置按钮**：快速将音调、音量滑块恢复默认值
- **自动停顿**：在句间和段间自动插入静音（时长可配置）
- **手动停顿**：在光标位置插入 `[pause:1.5s]` 标记
- **文本导入**：从 .txt 文件加载文本
- **选文试听**：选中文本后点击"试听"仅生成选中部分

### 生成历史

- 每次生成自动记录：时间戳、语音、语速、音调、音量、时长
- **逐条操作**：播放、保存 MP3、保存 SRT、删除
- 当前播放项高亮显示
- "清空历史"按钮一键清除（同时清空文本和停止播放）
- 历史在会话期间保存在内存中

### 播放控制

- **播放 / 暂停 / 停止**
- **进度条**：可拖拽到任意位置
- **时间显示**：当前播放位置 / 总时长
- 通过 HTML5 Audio + Blob URL 播放（无需外部播放器）

### 字幕导出

- SRT 字幕文件，词级时间戳
- 时间边界与生成的音频同步

### 对话模式（多角色）

- **模式切换**：顶部标签栏切换"单人模式"和"对话模式"
- **角色管理**：添加/编辑/删除角色，每个角色可设置语音、语速、音调、音量
- **颜色标签**：每个角色自动分配独特颜色
- **模板预设**：内置模板（男女对话、采访、故事、课堂）
- **轮间停顿**：可配置角色对话之间的静音时长（默认 0.8 秒）
- **段落停顿**：空行处插入更长的停顿（默认 2.0 秒）
- **带角色名 SRT**：字幕自动添加 `[角色名]` 前缀

#### 对话文本格式

在行首使用 `[角色名]` 标记说话人：

```
[男] 你好，请问你是哪里人？
[女] 我是北京人，你呢？
[男] 我是上海人。

[女] 欢迎来北京玩！
[旁白] 两人相视而笑。
```

**规则：**
- `[角色名]` 必须在行首，后面跟台词
- 空行 = 段落停顿（时长可配置）
- 没有标签的行继承上一个说话人
- 可选在开头定义角色：

```
---characters---
男: zh-CN-YunxiNeural, rate=+0%, pitch=+0Hz
女: zh-CN-XiaoxiaoNeural, rate=+0%, pitch=+5Hz
旁白: zh-CN-YunyangNeural, rate=-10%, pitch=-5Hz
---end---
[男] 你好
[女] 你好呀
```

**更多示例：**

采访：
```
[主持人] 欢迎来到我们的节目！
[嘉宾] 谢谢邀请。
[主持人] 能分享一下你的经历吗？
[嘉宾] 当然可以。
```

故事：
```
[旁白] 从前有一座山。
[小明] 小红，我们去探险吧！
[小红] 好啊，但我们要早点回来。
[旁白] 于是他们出发了。
```

### 打包发布

- Windows exe + Linux AppImage，通过 PyInstaller + GitHub Actions CI 自动构建
- 无控制台窗口，自定义应用图标
- UI 无网络依赖（CSS/JS 全部内联，无 CDN）
- 产物命名：`EdgeSpeak_win_amd64.exe`、`EdgeSpeak_linux_amd64.AppImage`

## 版本历史

| 版本 | 说明 |
|------|------|
| **v0.1.x** | 单人模式：基础 TTS，语音选择，生成历史，SRT 导出 |
| **v0.2.x** | 对话模式：多角色对话，角色管理，模板预设 |
| **v0.3.x** | Speech Director：自然语音引擎，Speech Plan 中间表示（规划中） |

## 快速开始

### 运行

```bash
uv sync
uv run python -m tts_tool
```

### 测试

```bash
uv run pytest tests/ -v
```

### 代码检查

```bash
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
```

## 构建

### Windows

```powershell
uv run pyinstaller tts-tool.spec --clean --noconfirm
```

输出：`dist/tts-tool.exe` (~19 MB，单文件，无控制台窗口)

### Linux

```bash
sudo apt install libgtk-3-0 libglib2.0-0 libwebkit2gtk-4.1-dev
uv sync
uv run pyinstaller tts-tool.spec --clean --noconfirm
```

### macOS

```bash
uv sync
uv run pyinstaller tts-tool.spec --clean --noconfirm
```

## 项目结构

```
src/tts_tool/
  __main__.py          入口
  tts_provider.py      TTSProvider 抽象基类（策略模式）
  providers/
    edge_provider.py   Edge TTS 实现
  tts_engine.py        TTSEngine 门面
  text_parser.py       句/段分割
  config.py            速度预设、应用配置
  subtitle.py          SRT 生成
  voice_list.py        语音获取与过滤
  audio_player.py      pygame 播放
  i18n.py              国际化
  job.py               Job + JobStore（生成历史模型）
  dialog/
    models.py          DialogCharacter, DialogTurn, DialogScript
    parser.py          对话文本解析（[角色名] 标签）
    merger.py          音频拼接 + SRT 时间偏移合并
    presets.py         默认角色语音映射
    templates.py       预置对话模板
  gui/
    app.py             pywebview 入口
    api.py             Python-JS 桥接
    index.html         前端界面（工具箱风格）
    icon.ico           应用图标
```

## 路线图

完整路线图见 [TODO.md](TODO.md)，核心规划：

- **Speech Director（语音导演）** — 文本到音频之间的"导演分镜脚本"：
  ```
  input.txt → speech_plan.json → 逐段 TTS → 合成 MP3
  ```
  - Speech Plan：描述谁说、说什么、怎么说、哪里停、哪里慢、哪里强调
  - 韵律规则：基于意图和标点自动规划停顿、语速、重音
  - 多 Provider 支持：Edge / Qwen / Piper / Kokoro
  - CLI：`build`（文本→计划）+ `render`（计划→MP3）
  - UI：预览和编辑 Speech Plan JSON，再渲染输出

## 依赖

- [pywebview](https://pypi.org/project/pywebview/) - 原生 WebView GUI
- [edge-tts](https://pypi.org/project/edge-tts/) - Microsoft Edge TTS API
- [pygame](https://pypi.org/project/pygame/) - 音频时长计算

## 许可证

MIT

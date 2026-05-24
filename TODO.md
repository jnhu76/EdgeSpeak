# EdgeSpeak - Roadmap

## Completed

### v0.1.x — Single Mode (基础版)
- [x] Edge TTS single voice generation
- [x] Voice selector: language → accent → voice
- [x] Rate / pitch / volume controls
- [x] Speed presets (slow / normal / fast)
- [x] MP3 / SRT save (fixed: file dialog tuple handling)
- [x] Generation history with playback
- [x] Text file import
- [x] i18n: zh / en / ja / ko / fr / ru / es
- [x] Cross-platform build: Windows exe + Linux AppImage
- [x] CI: GitHub Actions release pipeline

### v0.2.x — Dialog Mode (对话版)
- [x] Dialog models: DialogCharacter, DialogTurn, DialogScript
- [x] Dialog parser: `[角色名]` tag parsing, empty line = paragraph pause
- [x] Character presets per language (zh / en)
- [x] Dialog templates: 男女对话, 采访, 故事, 课堂
- [x] Audio merger: MP3 byte concatenation + silence frames + SRT merge
- [x] UI: tab switch (单人 / 对话), character panel, dialog editor, toolbar
- [x] API: parse_dialog_text, get_dialog_templates, generate_dialog
- [x] History: dialog items show character count + turn count

---

## Next: Speech Director (自然语音引擎)

> **核心理念：** Speech Plan 是文本到音频之间的"导演分镜脚本"。
> 它不直接发声，只描述：谁说、说什么、怎么说、哪里停、哪里慢、哪里强调。

```
源文本 input.txt
   ↓ 编译
speech_plan.json   ← 中间表示 IR
   ↓ 渲染
chunks/*.wav
   ↓ 合成
final.mp3
```

### Phase 1: Speech Plan 最小闭环

**目标：** 输入一段文本 → 生成 speech_plan.json → 渲染成带停顿、语速变化的 MP3

- [ ] `speech_director/models.py` — SpeechPlan / SpeechSegment 数据结构
  - id, role, text, intent, provider, voice, rate, pitch, volume
  - pause_before_ms, pause_after_ms, emphasis, instruction
- [ ] `speech_director/segmenter.py` — 句子切分 + 意群切分
  - split_sentences(): 按 .!? 切
  - split_thought_groups(): 按逗号、连接词 (but/because/although...) 粗切
- [ ] `speech_director/prosody_rules.py` — 停顿 / 语速 / 重音规则
  - pause_after_for_text(): 按标点和 intent 定停顿
  - rate_for_intent(): instruction=-5%, natural=+0%, slow=-15%, chunk=-12%
  - detect_emphasis(): 关键词 + 固定短语规则
- [ ] `speech_director/plan_builder.py` — 文本 → SpeechPlan
  - build_listening_plan(): teacher 提示 → 原速完整句 → 意群慢读 → 再听完整句
- [ ] `speech_director/audio_merger.py` — 按 pause_after_ms 插静音合成 MP3

### Phase 2: Renderer + Edge Provider

**目标：** 遍历 SpeechPlan segments，调用 TTS provider 逐段生成，合并输出

- [ ] `speech_director/renderer.py` — 按 plan 渲染音频
  - render_plan(): 遍历 segments → synthesize_segment() → merge_with_pauses()
  - synthesize_segment(): 按 provider 分发到对应引擎
- [ ] Edge provider 适配：复用现有 TTSEngine，支持 per-segment rate/pitch/volume
- [ ] 静音帧生成：按 pause_before_ms / pause_after_ms 插入

### Phase 3: CLI 入口

```bash
python -m speech_director build --input input.txt --plan speech_plan.json --mode listening
python -m speech_director render --plan speech_plan.json --output final.mp3
```

- [ ] CLI: build 子命令 — 文本 → speech_plan.json
- [ ] CLI: render 子命令 — speech_plan.json → final.mp3
- [ ] 支持 --mode: listening / reading / shadowing

### Phase 4: UI 集成

- [ ] 新增 tab: "听力训练"模式
- [ ] 两个按钮：生成 Speech Plan (预览 JSON) → 渲染 MP3
- [ ] Speech Plan JSON 编辑器（用户可手动微调停顿、语速、重音）
- [ ] 训练模式模板：听力练习 / 跟读练习 / 影子跟读

### Phase 5: 更多 Provider

- [ ] Qwen TTS provider — 支持 instruction 字段 (自然语言指令)
- [ ] Piper TTS provider — 本地离线语音
- [ ] Kokoro TTS provider
- [ ] Provider 接口统一：所有 provider 实现相同的 synthesize(seg) 方法

### Phase 6: LLM 优化 Speech Plan

- [ ] 用 LLM 自动优化停顿位置、语速曲线、重音标记
- [ ] 根据文本语义动态调整 intent 和 prosody
- [ ] A/B 测试：规则版 vs LLM 版的听感差异

---

## Future Ideas
- [ ] Post Processor: 音频后处理（均衡、压缩、混响）提升质感
- [ ] 背景音 / 环境音叠加
- [ ] 实时预览：调整单个 segment 后即时试听
- [ ] 批量生成：多个 speech plan 队列渲染

## Design Docs
- [Dialog Mode Design](docs/dialog-design.md)
- Speech Plan Design (本文件 Phase 1-6 即设计文档)

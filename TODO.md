# TODO - Dialog Mix Feature

## Goal
Support generating conversational/dialog audio where multiple voices take turns speaking, producing a single mixed audio file.

## Tasks

### Core Model
- [ ] Design dialog data model: list of turns, each turn has {text, voice, character_name}
- [ ] Support character definition: name + voice mapping
- [ ] Support inline dialog format in text editor (e.g. `[A]Hello[B]Hi, how are you?`)

### UI - Dialog Editor
- [ ] Add tab/mode switch: "Single" vs "Dialog" in the right panel
- [ ] Dialog mode: split text editor into per-turn segments with voice selector per turn
- [ ] Character panel: define characters with name + voice + rate/pitch/volume
- [ ] Visual distinction between characters (color coding or labels)

### Audio Generation
- [ ] Generate each turn as a separate audio segment with its own voice/params
- [ ] Concatenate all segments into a single audio file with configurable inter-turn pause
- [ ] Store each dialog generation as a single history item with metadata (character list, turn count)

### History & Export
- [ ] History item shows "Dialog: N turns, M characters" instead of single voice
- [ ] Save combined MP3 and combined SRT with all turns
- [ ] Option to export individual turns as separate files

### Tests
- [ ] Dialog model unit tests
- [ ] Multi-voice audio concatenation tests (with mocked TTS)
- [ ] Dialog text parsing tests (inline format)

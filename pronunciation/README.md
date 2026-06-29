# German Translation & Audio Generator

A lightweight Python utility that converts simple English sentence lists into structured German learning material.

The script automatically:

* Translates English to German
* Generates an English-friendly pronunciation guide
* Creates high-quality German speech (MP3)
* Formats everything into a clean Markdown lesson
* Supports incremental generation (only processes new sentences)
* Can reset the project with a single command

---

## Features

* English → German translation using **deep-translator**
* High-quality German neural voices using **Edge TTS**
* Automatic pronunciation generation
* Automatic MP3 generation
* Safe Markdown rewriting
* Idempotent (safe to run multiple times)
* Automatic numbering
* Rich console output
* Project reset command

---

## Project Structure

```
pronunciation/
│
├── script.py
├── dialogues.md
└── audios/
```

The `audios` folder is created automatically.

---

## Installation

Install the required packages:

```bash
pip install deep-translator edge-tts rich
```

Python 3.11 or newer is recommended.

---

## Getting Started

Run the script once:

```bash
python script.py
```

If `dialogues.md` doesn't exist, it will be created automatically.

Default contents:

```markdown
# Dialogues

Add English sentences below.

- Hello world
```

---

## Adding Sentences

Simply add English sentences as Markdown list items.

Example:

```markdown
# Dialogues

Add English sentences below.

- Hello world
- My name is John.
- I would like a coffee.
- Where is the train station?
```

Only lines beginning with `- ` are treated as new input.

---

## Running the Generator

Execute:

```bash
python script.py
```

The script will:

1. Read every new English sentence.
2. Translate it into German.
3. Generate a pronunciation guide.
4. Create an MP3 using Edge TTS.
5. Replace the original list item with a structured lesson.

Example output:

```markdown
## 001

### English

Hello world

### German

Hallo Welt

### Pronunciation

HAH-loh VELT

### Audio

[audios/001.mp3](audios/001.mp3)

---
```

The generated MP3 will be saved as:

```
audios/001.mp3
```

---

## Incremental Generation

The generator is designed to be run repeatedly.

After processing your first lesson, simply append more English sentences to the end of `dialogues.md`.

Example:

```markdown
...

---

- I live in Germany.
- How much does this cost?
```

Running the script again will only process these new list items.

Previously generated lessons and audio files are left unchanged.

---

## Resetting the Project

To restore the project to its initial state:

```bash
python script.py reset
```

This will:

* Delete every generated MP3
* Recreate the `audios` directory
* Reset `dialogues.md` to its default contents

Result:

```markdown
# Dialogues

Add English sentences below.

- Hello world
```

---

## Console Output

Example:

```
German Translation & Audio Generator

✓ dialogues.md loaded
✓ Found 4 new sentences

Done.

Generated:

001.mp3
002.mp3
003.mp3
004.mp3
```

Errors are reported without deleting existing content.

---

## Translation

Powered by:

* **deep-translator**
* Google Translate backend

Language flow:

```
English
      │
      ▼
German Translation
```

---

## Text-to-Speech

Powered by Microsoft's Edge Neural voices.

Current default voice:

```
de-DE-KatjaNeural
```

Audio is exported as standard MP3 files.

---

## Pronunciation Guide

The pronunciation guide is intended for English speakers.

Example:

| German             | Pronunciation       |
| ------------------ | ------------------- |
| Guten Tag          | GOO-ten TAHK        |
| Ich heiße Anna     | Ikh HY-suh AH-na    |
| Wie geht es Ihnen? | VEE GAYT ess EE-nen |

This is **not IPA**. It is a simplified phonetic approximation to help beginners read German aloud.

---

## File Safety

The script never writes directly to `dialogues.md`.

Instead it:

1. Creates a temporary file.
2. Writes all generated content.
3. Replaces the original file only after a successful write.

This minimizes the risk of data loss.

---

## Current Limitations

* Internet connection required for translation and TTS.
* Pronunciation is an approximation and not a linguistic transcription.
* Only English → German translation is currently supported.
* Existing generated lesson blocks are treated as read-only.

---

## Future Improvements

Potential enhancements include:

* Multiple TTS voices
* Slow-speed audio
* Dialogue mode with different speakers
* Automatic Anki deck generation
* PDF lesson generation
* Vocabulary extraction
* Quiz generation
* Multiple language support
* Configuration file (`config.toml`)
* Custom pronunciation dictionary
* Batch processing

---

## License

This utility is intended as part of the German Master Guide project and may be freely modified or extended to suit your own learning workflow.
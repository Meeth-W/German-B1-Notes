import asyncio
import sys
import re
import shutil
from pathlib import Path
from typing import List, Tuple

try:
    from deep_translator import GoogleTranslator
    import edge_tts
    from rich.console import Console
except ImportError as e:
    print(f"Error: Missing required library. Please install it. Details: {e}")
    print("Run: pip install deep-translator edge-tts rich")
    sys.exit(1)

console = Console()

BASE_DIR = Path(__file__).parent.resolve()
DIALOGUES_PATH = BASE_DIR / "dialogues.md"
AUDIOS_DIR = BASE_DIR / "audios"

# German function/grammatical words to keep capitalized on the first letter only
FUNCTION_WORDS = {
    'ich', 'du', 'er', 'sie', 'es', 'wir', 'ihr', 'ein', 'eine', 'einen', 'einem', 
    'einer', 'eines', 'der', 'die', 'das', 'dem', 'den', 'des', 'mit', 'zu', 'von', 
    'bei', 'in', 'an', 'auf', 'aus', 'nach', 'seit', 'vor', 'über', 'unter', 'neben', 
    'zwischen', 'und', 'oder', 'aber', 'weil', 'dass', 'wenn', 'nicht', 'sich', 
    'mich', 'dich', 'mir', 'dir', 'uns', 'euch'
}

def translate_text(text: str) -> str:
    return GoogleTranslator(source='en', target='de').translate(text)

def transcribe_german_word(word: str) -> str:
    orig_word = word
    w = word.lower()
    
    w = re.sub(r'sch', 'sh', w)
    
    w = re.sub(r'^sp', 'shp', w)
    w = re.sub(r'^st', 'sht', w)
    
    w = re.sub(r'(?<=[aou])ch', 'kh', w)
    w = re.sub(r'(?<=au)ch', 'kh', w)
    w = re.sub(r'ch', 'kh', w)  
    
    w = re.sub(r'ie', 'ee', w)
    w = re.sub(r'ei|ey|ai|ay', 'y', w)
    w = re.sub(r'eu|äu', 'oy', w)
    w = re.sub(r'au', 'ow', w)
    
    w = re.sub(r'ä', 'eh', w)
    w = re.sub(r'ö', 'er', w)
    w = re.sub(r'ü', 'ew', w)
    w = re.sub(r'ß', 's', w)
    
    if w.startswith('s') and len(w) > 1 and w[1] in 'aeiouyäöü': w = 'z' + w[1:]
    
    w = re.sub(r'v', 'f', w)
    w = re.sub(r'w', 'v', w)
    w = re.sub(r'z', 'ts', w)
    w = re.sub(r'j', 'y', w)
    
    w = re.sub(r'ee', 'ay', w)
    w = re.sub(r'oo', 'oh', w)
    w = re.sub(r'aa', 'ah', w)
    
    if w.endswith('er'): w = w[:-2] + 'uh'
    elif w.endswith('e') and len(w) > 2: w = w[:-1] + 'uh'
        
    if w.endswith('b'): w = w[:-1] + 'p'
    elif w.endswith('d'): w = w[:-1] + 't'
    elif w.endswith('g'): w = w[:-1] + 'k'
        
    w = re.sub(r'(?<![aeiouy])a(?![aeiouy])', 'ah', w)
    w = re.sub(r'(?<![aeiouy])o(?![aeiouy])', 'oh', w)
    w = re.sub(r'(?<![aeiouy])u(?![aeiouy])', 'oo', w)
    w = re.sub(r'(?<![aeiouy])i(?![aeiouy])', 'ih', w)
    
    for char in ['b', 'c', 'd', 'f', 'g', 'l', 'm', 'n', 'p', 'r', 's', 't']:
        w = re.sub(char + '{2,}', char, w)
        
    if not w: return orig_word
        
    return w

def split_syllables(w: str) -> List[str]:
    vowel_rx = re.compile(r'(ay|ee|oy|ow|ah|oh|oo|ih|eh|ew|er|uh|y|a|e|i|o|u)', re.IGNORECASE)
    matches = list(vowel_rx.finditer(w))
    if not matches: return [w]
    
    syllables = []
    start = 0
    for i in range(len(matches) - 1):
        curr_vowel = matches[i]
        next_vowel = matches[i+1]
        cons_start = curr_vowel.end()
        cons_end = next_vowel.start()
        cons_len = cons_end - cons_start
        
        if cons_len <= 1:
            split_pt = cons_start
        else:
            split_pt = cons_start + 1
            
        syllables.append(w[start:split_pt])
        start = split_pt
        
    syllables.append(w[start:])
    return syllables

def capitalize_word_phonetics(w: str, orig_word: str) -> str:
    if orig_word.lower() in FUNCTION_WORDS:
        return w.capitalize()
        
    syllables = split_syllables(w)
    if len(syllables) == 1:
        return syllables[0].upper()
        
    syllables[0] = syllables[0].upper()
    for i in range(1, len(syllables)):
        syllables[i] = syllables[i].lower()
        
    return "-".join(syllables)

def german_to_phonetic(text: str) -> str:
    tokens = re.split(r"([a-zA-ZäöüÄÖÜß]+)", text)
    result = []
    for token in tokens:
        if token.isalpha() or (token and token[0] in 'äöüÄÖÜß'):
            ph = transcribe_german_word(token)
            cap_ph = capitalize_word_phonetics(ph, token)
            result.append(cap_ph)
        else:
            result.append(token)
    return "".join(result)

async def generate_audio(text: str, output_path: str, voice: str = "de-DE-KatjaNeural") -> None:
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def initialize_project() -> None:
    AUDIOS_DIR.mkdir(parents=True, exist_ok=True)
    if not DIALOGUES_PATH.exists():
        with open(DIALOGUES_PATH, "w", encoding="utf-8") as f:
            f.write("# Dialogues\n\nAdd English sentences below.\n\n- Hello world\n")

def reset_project() -> None:
    console.print("[yellow]Resetting project...[/yellow]")
    
    if AUDIOS_DIR.exists(): shutil.rmtree(AUDIOS_DIR)
    AUDIOS_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(DIALOGUES_PATH, "w", encoding="utf-8") as f:
        f.write("# Dialogues\n\nAdd English sentences below.\n\n- Hello world\n")
        
    console.print("[green]OK: Project reset successfully.[/green]")

async def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1].lower() == "reset":
        reset_project()
        return

    console.print("[bold blue]German Translation & Audio Generator[/bold blue]\n")
    
    initialize_project()
    console.print("[green]OK: dialogues.md loaded[/green]")

    with open(DIALOGUES_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    lesson_numbers = [int(num) for num in re.findall(r'^## (\d+)', content, re.MULTILINE)]
    next_num = max(lesson_numbers) + 1 if lesson_numbers else 1

    lines = content.splitlines()
    new_lines = []
    generated_audios = []
    new_sentences_count = sum(1 for line in lines if line.strip().startswith("- "))

    if new_sentences_count == 0:
        console.print("[yellow]No new English sentences found to process.[/yellow]")
        return

    console.print(f"[green]OK: Found {new_sentences_count} new sentences[/green]\n")

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- "):
            english_text = stripped[2:].strip()
            if not english_text:
                new_lines.append(line)
                continue
            
            try:
                # 1. Translate
                german_text = translate_text(english_text)
                
                # 2. Pronunciation
                pronunciation = german_to_phonetic(german_text)
                
                # 3. Audio Generation
                num_str = f"{next_num:03d}"
                audio_filename = f"{num_str}.mp3"
                audio_path = AUDIOS_DIR / audio_filename
                
                await generate_audio(german_text, str(audio_path))
                
                # 4. Format Lesson Block
                lesson_block = (
                    f"## {num_str}\n\n"
                    f"### English\n\n"
                    f"{english_text}\n\n"
                    f"### German\n\n"
                    f"{german_text}\n\n"
                    f"### Pronunciation\n\n"
                    f"{pronunciation}\n\n"
                    f"### Audio\n\n"
                    f"[audios/{audio_filename}](audios/{audio_filename})\n\n"
                    f"---"
                )
                new_lines.append(lesson_block)
                generated_audios.append(audio_filename)
                next_num += 1
            except Exception as e:
                console.print(f"[red]Error processing '{english_text}': {e}[/red]")
                new_lines.append(line)
        else:
            new_lines.append(line)

    temp_path = DIALOGUES_PATH.with_suffix(".tmp")
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines) + "\n")
        
        temp_path.replace(DIALOGUES_PATH)
    except Exception as e:
        console.print(f"[red]File safety error: could not write markdown file. {e}[/red]")
        if temp_path.exists(): temp_path.unlink()
        return

    console.print("\n[bold green]Done.[/bold green]")
    if generated_audios:
        console.print("\n[bold]Generated:[/bold]")
        for audio in generated_audios:
            console.print(f"[green]OK: {audio}[/green]")

if __name__ == "__main__":
    asyncio.run(main())

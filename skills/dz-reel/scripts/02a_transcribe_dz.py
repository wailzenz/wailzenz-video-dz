# -*- coding: utf-8 -*-
"""wailzenz-video-dz: word-timed transcription for Algerian Darija (and any Arabic / English / French),
replacing step 4's `python3 -m whisper --model medium` (CPU, weak on Maghrebi dialect).

  python3 02a_transcribe_dz.py <work> [--engine auto|cpp|hadra|whisper|compare] [--lang ar|en|fr]
                                      [--no-prompt] [--prompt "..."] [--save-default ENGINE]

Reads <work>/a.wav (16 kHz mono, made by step 4's ffmpeg line). Writes <work>/a.json in openai-whisper's format
({"text","language","segments":[{"id","start","end","text","words":[{"word","start","end","probability"}]}]}),
so 02_captions.py, 10_script_edit.py, 22_hook.py etc. read it unchanged.

Engines:
  cpp      whisper.cpp large-v3 (Metal GPU on a Mac). Needs `whisper-cli` + ~/.wailzenz-video-dz/models/ggml-large-v3-q5_0.bin
  hadra    algerian-nlp/Hadra-ASR-whisper-medium (MIT), a LoRA on openai/whisper-medium trained on Algerian Darja,
           via transformers + peft. First run downloads ~1.8 GB; peaks at ~6 GB RAM.
  whisper  openai-whisper large-v3 (any OS; uses an NVIDIA GPU if there is one, else the CPU — slow but works).
  compare  runs two engines (cpp or whisper, plus hadra), writes a_<engine>.json for each, prints them, keeps the first.
  auto     (default) the engine saved with --save-default, else cpp if available, else whisper.
"""
import argparse, json, os, re, shutil, subprocess, sys

WVD_HOME = os.environ.get("WVD_HOME", os.path.join(os.path.expanduser("~"), ".wailzenz-video-dz"))
MODELS = os.environ.get("WHISPER_CPP_MODELS", os.path.join(WVD_HOME, "models"))
CONFIG = os.path.join(WVD_HOME, "config.json")
# Biases Whisper towards Darija spelling instead of "correcting" it into Modern Standard Arabic.
DZ_PROMPT = "سلام عليكم، واش راكم؟ اليوم نحكيلكم كيفاش درت، بصح هادي حاجة مليحة بزاف."
HALLUCINATIONS = ["اشتركوا في القناة", "ترجمة نانسي قنقر", "شكرا للمشاهدة", "شكرا لكم على المشاهدة"]
END_PUNCT = tuple(".?!؟…")


def group_words(words, gap=0.6, max_words=12, max_dur=6.0):
    """[(text, start, end, p)] -> sentence segments, split on pauses, end punctuation or length."""
    segs, cur = [], []
    for w in words:
        if cur and (w[1] - cur[-1][2] >= gap or len(cur) >= max_words or w[2] - cur[0][1] > max_dur):
            segs.append(cur); cur = []
        cur.append(w)
        if w[0].endswith(END_PUNCT):
            segs.append(cur); cur = []
    if cur: segs.append(cur)
    out = []
    for s in segs:
        text = " ".join(w[0] for w in s)
        if any(h in text for h in HALLUCINATIONS):
            continue
        out.append({"id": len(out), "start": round(s[0][1], 3), "end": round(s[-1][2], 3), "text": " " + text,
                    "words": [{"word": " " + t, "start": round(a, 3), "end": round(b, 3), "probability": round(p, 3)}
                              for t, a, b, p in s]})
    return out


def tidy(words):
    """Monotonic, non-zero word times (whisper.cpp sometimes gives the first word of a segment 0 ms)."""
    out, last = [], 0.0
    for t, a, b, p in words:
        t = t.strip()
        if not t or re.fullmatch(r"\[.*\]|\(.*\)", t):
            continue
        a = max(a, last)
        b = max(b, a + 0.08)
        out.append((t, a, b, p)); last = b
    return out


def cpp_model(lang):
    names = ["ggml-large-v3-q5_0.bin"] if lang == "ar" else ["ggml-large-v3-turbo-q5_0.bin", "ggml-large-v3-q5_0.bin"]
    for n in names:
        p = os.path.join(MODELS, n)
        if os.path.exists(p): return p
    return None


def cpp_available(lang):
    return bool(shutil.which("whisper-cli")) and cpp_model(lang) is not None


def run_cpp(wav, work, lang, prompt):
    model = cpp_model(lang)
    if not shutil.which("whisper-cli") or not model:
        sys.exit(f"❌ whisper.cpp not ready (whisper-cli on PATH + a model in {MODELS}) — run setup/setup-mac.sh, or use --engine whisper")
    base = os.path.join(work, "a_cpp_raw")
    cmd = ["whisper-cli", "-m", model, "-l", lang, "-f", wav, "-ml", "1", "-sow", "-ojf", "-of", base, "-np"]
    if prompt:
        cmd += ["--prompt", prompt]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("❌ whisper-cli failed:\n" + r.stderr[-800:])
    d = json.load(open(base + ".json", encoding="utf-8"))
    words = []
    for s in d.get("transcription", []):
        ps = [t.get("p", 1.0) for t in s.get("tokens", []) if not t.get("text", "").startswith("[_")]
        words.append((s["text"], s["offsets"]["from"] / 1000, s["offsets"]["to"] / 1000, sum(ps) / len(ps) if ps else 1.0))
    return tidy(words)


def run_whisper(wav, lang, prompt):
    import torch, whisper
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    m = whisper.load_model(os.environ.get("WHISPER_MODEL", "large-v3"), device=dev)
    r = m.transcribe(wav, language=lang, word_timestamps=True, initial_prompt=prompt,
                     condition_on_previous_text=False, fp16=(dev == "cuda"))
    return tidy([(w["word"], w["start"], w["end"], w.get("probability", 1.0)) for s in r["segments"] for w in s.get("words", [])])


def run_hadra(wav, lang, prompt):
    import soundfile as sf, torch
    from peft import PeftModel
    from transformers import WhisperForConditionalGeneration, WhisperProcessor, pipeline
    base_id, adapter_id = "openai/whisper-medium", "algerian-nlp/Hadra-ASR-whisper-medium"
    # The adapter repo's tokenizer config breaks WhisperProcessor on recent transformers (see its model card),
    # and the adapter doesn't change the tokenizer — so load the processor from the base model.
    proc = WhisperProcessor.from_pretrained(base_id)
    model = WhisperForConditionalGeneration.from_pretrained(base_id, dtype=torch.float32)
    model = PeftModel.from_pretrained(model, adapter_id).merge_and_unload()
    model.generation_config.forced_decoder_ids = None
    dev = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
    if dev != "cpu":
        model = model.half()   # fp32 peaked at ~9.8 GB on an 8 GB Mac; fp16 roughly halves it
    asr = pipeline("automatic-speech-recognition", model=model, tokenizer=proc.tokenizer,
                   feature_extractor=proc.feature_extractor, device=dev, chunk_length_s=30, dtype=model.dtype)
    audio, sr = sf.read(wav, dtype="float32")
    if audio.ndim > 1: audio = audio.mean(1)
    gk = {"language": {"ar": "arabic", "en": "english", "fr": "french"}.get(lang, lang), "task": "transcribe"}
    # No prompt: it's already trained on Darija, and transformers' word timestamps crash with prompt_ids
    # ("size of tensor a must match ... at non-singleton dimension 1" in _extract_token_timestamps).
    res = asr({"raw": audio, "sampling_rate": sr}, return_timestamps="word", generate_kwargs=gk)
    words = []
    for c in res.get("chunks", []):
        a, b = c["timestamp"]
        if a is None: continue
        words.append((c["text"], float(a), float(b if b is not None else a + 0.3), 1.0))
    return tidy(words)


def write(segs, path, lang):
    json.dump({"text": "".join(s["text"] for s in segs), "language": lang, "segments": segs},
              open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def saved_engine():
    try:
        return json.load(open(CONFIG, encoding="utf-8")).get("engine")
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("work", nargs="?")
    ap.add_argument("--engine", choices=["auto", "cpp", "hadra", "whisper", "compare"], default="auto")
    ap.add_argument("--lang", default="ar")
    ap.add_argument("--prompt", default=None, help="initial prompt (default: a short Darija sentence when --lang ar)")
    ap.add_argument("--no-prompt", action="store_true")
    ap.add_argument("--save-default", choices=["cpp", "hadra", "whisper"], help="remember this engine for --engine auto")
    a = ap.parse_args()
    if a.save_default:
        os.makedirs(WVD_HOME, exist_ok=True)
        cfg = {}
        if os.path.exists(CONFIG):
            cfg = json.load(open(CONFIG, encoding="utf-8"))
        cfg["engine"] = a.save_default
        json.dump(cfg, open(CONFIG, "w", encoding="utf-8"), indent=1)
        print(f"✅ default engine = {a.save_default} ({CONFIG})")
        if not a.work: return
    if not a.work:
        ap.error("work folder required")
    work = os.path.abspath(a.work)
    wav = os.path.join(work, "a.wav")
    if not os.path.exists(wav):
        sys.exit(f"❌ {wav} not found — run step 4's ffmpeg line first")
    prompt = None if a.no_prompt else (a.prompt if a.prompt is not None else (DZ_PROMPT if a.lang == "ar" else None))
    base = "cpp" if cpp_available(a.lang) else "whisper"
    if a.engine == "compare":
        engines = [base, "hadra"]
    elif a.engine == "auto":
        engines = [saved_engine() or base]
    else:
        engines = [a.engine]
    run = {"cpp": lambda: run_cpp(wav, work, a.lang, prompt), "whisper": lambda: run_whisper(wav, a.lang, prompt),
           "hadra": lambda: run_hadra(wav, a.lang, prompt)}
    results = {}
    for e in engines:
        segs = group_words(run[e]())
        results[e] = segs
        write(segs, os.path.join(work, f"a_{e}.json"), a.lang)
    shutil.copy(os.path.join(work, f"a_{engines[0]}.json"), os.path.join(work, "a.json"))
    for e, segs in results.items():
        print(f"== {e}: {len(segs)} segments, {sum(len(s['words']) for s in segs)} words")
        for s in segs:
            print(f"{s['start']:7.2f}-{s['end']:7.2f} {s['text'].strip()}")
    print(f"✅ a.json ← {engines[0]}")


if __name__ == "__main__":
    main()

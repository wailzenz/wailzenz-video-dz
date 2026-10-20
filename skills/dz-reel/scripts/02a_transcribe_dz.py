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
        # the length limits never orphan a sentence's last word («…doesn't» | «have.» showed «have.» alone) — only a pause splits it off
        too_long = (len(cur) >= max_words or w[2] - cur[0][1] > max_dur) and not w[0].endswith(END_PUNCT) if cur else False
        if cur and (w[1] - cur[-1][2] >= gap or too_long):
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


def speech_onsets(wav, hop=0.01):
    """Per-10 ms 'is someone speaking' flags (RMS above the clip's noise floor + 15 dB)."""
    import numpy as np, soundfile as sf
    x, sr = sf.read(wav, dtype="float32")
    if x.ndim > 1: x = x.mean(1)
    n = int(sr * hop); frames = len(x) // n
    rms = 20 * np.log10(np.sqrt((x[:frames * n].reshape(frames, n) ** 2).mean(1)) + 1e-9)
    floor = np.percentile(rms, 10)
    return rms > max(floor + 15, -50), hop


def snap_starts(words, wav):
    """whisper's time for the first word of a sentence is often early (it can sit in the silence before you
    speak) — or late when the voice is already going. Move such starts to where the voice actually begins,
    never past the next word and never back into the previous one."""
    try:
        act, hop = speech_onsets(wav)
    except Exception:
        return words
    out = []
    for i, (t, a, b, p) in enumerate(words):
        prev_end = out[-1][2] if out else 0.0
        nxt = words[i + 1][1] if i + 1 < len(words) else b
        if a - prev_end > 0.25 or i == 0:                     # a sentence start: after a pause, or the very first word
            lo, hi = int(max(a, prev_end) / hop), int(max(min(nxt, b) - 0.05, a) / hop)
            hit = next((k for k in range(lo, min(hi, len(act))) if act[k]), None)
            if hit is not None and hit * hop > a:
                a = hit * hop
            else:   # …or late: the voice is already going before whisper's start (a clip that opens mid-word) → walk back to its onset
                k, stop = int(a / hop) - 1, int(max(prev_end, a - 0.35) / hop)
                while stop <= k < len(act) and act[k]: k -= 1
                if (k + 1) * hop < a - 0.03: a = round((k + 1) * hop, 3)
        out.append((t, a, max(b, a + 0.08), p))
    return out


def run_cpp(wav, work, lang, prompt):
    """whisper.cpp with DTW token timestamps (flash attention must be off for DTW) — the plain segment offsets
    run ~0.5 s early on Darija, so captions would show words before they are said."""
    model = cpp_model(lang)
    if not shutil.which("whisper-cli") or not model:
        sys.exit(f"❌ whisper.cpp not ready (whisper-cli on PATH + a model in {MODELS}) — run setup/setup-mac.sh, or use --engine whisper")
    preset = "large.v3.turbo" if "turbo" in os.path.basename(model) else "large.v3"
    base = os.path.join(work, "a_cpp_raw")
    cmd = ["whisper-cli", "-m", model, "-l", lang, "-f", wav, "-ojf", "--dtw", preset, "-nfa", "-of", base, "-np"]
    if prompt:
        cmd += ["--prompt", prompt]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("❌ whisper-cli failed:\n" + r.stderr[-800:])
    d = json.load(open(base + ".json", encoding="utf-8"))
    words = []
    for s in d.get("transcription", []):
        seg_end = s["offsets"]["to"] / 1000
        cur = []
        toks = [t for t in s.get("tokens", []) if not t.get("text", "").startswith("[_")]
        for t in toks:                                      # tokens → words: a leading space starts a new word
            ts = t["t_dtw"] / 100 if t.get("t_dtw", -1) >= 0 else t["offsets"]["from"] / 1000
            if not cur or t["text"].startswith(" "):
                cur.append([t["text"].strip(), ts, [t.get("p", 1.0)]])
            else:
                cur[-1][0] += t["text"]; cur[-1][2].append(t.get("p", 1.0))
        for i, (txt, ts, ps) in enumerate(cur):
            end = cur[i + 1][1] if i + 1 < len(cur) else seg_end
            words.append((txt, ts, end, sum(ps) / len(ps)))
    return tidy(snap_starts(tidy(words), wav))


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
    dev = os.environ.get("WVD_TORCH_DEVICE") or ("cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu"))
    # WVD_TORCH_DEVICE=cpu: on 8 GB Macs the MPS path keeps a CPU and a GPU copy of the model and can swap itself to a halt
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

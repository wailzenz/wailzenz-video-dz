# -*- coding: utf-8 -*-
"""reel.py — the dz-reel pipeline in five commands, with short output (wailzenz-video-dz, 2026-10-20).

Every step's full log goes to <work>/logs/<step>.log; the screen gets only what you need to decide the next step.
Run after:  source "<plugin>/setup/env.sh"

  python3 reel.py prep    <video> <work> [--lang ar|en|fr]   copy · dropped frames · light · cut plan · transcription · draft fixes.json
  python3 reel.py script  <work>                             captions + the numbered script (show it to the user; drop lines here)
  python3 reel.py cut     <work> [--grade] [--endcard ar|none]  theme · cut + zoom · frames · face track (chin rule)
  python3 reel.py preview <work> [t …]                       compose.html (+ scene kit) · 6-frame sheet (default: the kit's moments)
  python3 reel.py final   <work> --name <name> [--cover "Line|*line*"] [--cover-t 3.8] [--export <dir>]
                                                             sound cues · render · encode · −14 LUFS · subtitles · all checks · cover · export
House theme: $WVD_HOME/house-theme.json (copied into each new work folder).
"""
import json, os, re, shutil, subprocess, sys, time
from pathlib import Path

SC = Path(__file__).resolve().parent
HOME = Path(os.environ.get("WVD_HOME", Path.home() / ".wailzenz-video-dz"))


def die(msg): print("❌ " + msg); sys.exit(1)


def opt(args, name, default=None):
    return args[args.index(name) + 1] if name in args and args.index(name) + 1 < len(args) else default


def run(W, step, cmd, ok=(0,)):
    """Run a step, log everything, return (returncode, output)."""
    (W / "logs").mkdir(exist_ok=True)
    t0 = time.time()
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, cwd=SC.parent)   # the skill folder, like the manual steps
    out = (r.stdout or "") + (r.stderr or "")
    (W / "logs" / f"{step}.log").write_text(out, encoding="utf-8")
    if r.returncode not in ok:
        tail = "\n".join(out.strip().splitlines()[-6:])
        die(f"{step} failed ({time.time() - t0:.0f}s) — {W / 'logs' / (step + '.log')}\n{tail}")
    return r.returncode, out


def lines(out, *marks):
    return [l.strip() for l in out.splitlines() if l.strip().startswith(marks)]


def state(W, **kw):
    p = W / "reel.json"; s = json.loads(p.read_text()) if p.exists() else {}
    if kw: s.update(kw); p.write_text(json.dumps(s, ensure_ascii=False, indent=1))
    return s


def dur(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)], capture_output=True, text=True)
    try: return float(r.stdout.strip())
    except ValueError: return 0.0


# ── prep ────────────────────────────────────────────────────────────────────────────────────────────
def prep(args):
    if len(args) < 2: die("prep <video> <work> [--lang ar|en|fr]")
    V, W = Path(args[0]).expanduser(), Path(args[1]).expanduser().resolve()
    lang = opt(args, "--lang", "ar")
    if not V.exists(): die(f"no video: {V}")
    W.mkdir(parents=True, exist_ok=True); src = W / "src.mov"
    if not src.exists(): shutil.copy2(V, src)
    state(W, lang=lang)
    d = dur(src); print(f"🎬 {V.name} → {W}  ·  {d:.1f}s  ·  lang {lang}")
    # dropped frames
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "frame=pts_time", "-of", "csv=p=0", str(src)], capture_output=True, text=True)
    ts = [float(x) for x in r.stdout.split() if x.strip()]
    gaps = [b - a for a, b in zip(ts, ts[1:]) if b - a > 0.07]
    if gaps:
        run(W, "frames_fix", ["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", "minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1", "-c:a", "copy", W / "src_fixed.mov"])
        print(f"🩹 {len(gaps)} dropped-frame gaps → repaired (src_fixed.mov) — tell the user to film with the camera app next time")
    # light / colour
    _, out = run(W, "scopes", ["python3", SC / "25_scopes.py", W])
    warn = lines(out, "⚠️")
    if warn:
        curve = re.search(r"curves=master='[^']+'", out)
        if curve:
            run(W, "before_after", ["ffmpeg", "-v", "error", "-y", "-ss", f"{d / 3:.2f}", "-i", src, "-frames:v", "1", "-filter_complex",
                                    f"[0]split[a][b];[b]{curve.group(0)}[c];[a]scale=432:-1[a2];[c]scale=432:-1[c2];[a2][c2]hstack", W / "before_after.jpg"])
        print(f"🔬 {warn[0].lstrip('⚠️ ').strip()} — ask the user (before/after: before_after.jpg); yes → `cut --grade`")
    else:
        print("🔬 light and colour OK")
    # cut plan
    _, out = run(W, "cut_plan", ["python3", SC / "01_cut_plan.py", W])
    summ = next((l for l in out.splitlines() if "انشال=" in l), "").strip()
    m = re.search(r"الباقي=([\d.]+)s\s+انشال=([\d.]+)s", summ)
    print(f"✂️  kept {m.group(1)}s · removed {m.group(2)}s of pauses" if m else "✂️  " + summ)
    for l in lines(out, "✅", "⚠️"): print("   " + l)
    # transcription
    run(W, "audio", ["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-ac", "1", "-ar", "16000", W / "a.wav"])
    run(W, "transcribe", ["python3", SC / "02a_transcribe_dz.py", W, "--lang", lang])
    a = json.loads((W / "a.json").read_text(encoding="utf-8"))
    fx = W / "fixes.json"
    if not fx.exists():
        draft = {"fix": [[w["word"].strip() for w in s.get("words", [])] for s in a["segments"]], "hot": []}
        if lang == "ar": draft["gloss"] = {}
        fx.write_text(json.dumps(draft, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"🗣️  {len(a['segments'])} sentences (fixes.json drafted — same word count per sentence):")
    for i, s in enumerate(a["segments"]):
        print(f"  {i} [{s['start']:5.2f}] ({len(s.get('words', []))}) {s['text'].strip()}")
    print("→ correct fixes.json" + (" (Darija spelling · gloss for every French/English term · hot words)" if lang == "ar" else " (wrong words only · 2–4 hot words)") + ", then: reel.py script")


# ── script ─────────────────────────────────────────────────────────────────────────────────────────
def script(args):
    W = Path(args[0]).resolve()
    _, out = run(W, "captions", ["python3", SC / "02_captions.py", W])
    for l in lines(out, "⚠️", "❌"): print(l)
    _, out = run(W, "script", ["python3", SC / "10_script_edit.py", W, "show"])
    for l in out.splitlines():
        if re.match(r"^\s*\d+\s+\[", l) or "المدة الحالية" in l: print(l.rstrip())
    print("→ ask the user ONCE (one AskUserQuestion): lines to drop · brightness if flagged · end card. Drop: 10_script_edit.py <work> drop N, then reel.py cut")


# ── cut ────────────────────────────────────────────────────────────────────────────────────────────
def cut(args):
    W = Path(args[0]).resolve(); st = state(W); lang = st.get("lang", "ar")
    th = W / "theme.json"
    if not th.exists():
        house = HOME / "house-theme.json"
        t = json.loads(house.read_text(encoding="utf-8")) if house.exists() else {}
        if not t: print("⚠️ no $WVD_HOME/house-theme.json — run the onboarding (references/start.md) for this user's colours")
        t["grade"] = "auto" if "--grade" in args else False
        end = opt(args, "--endcard", "ar" if lang == "ar" else "none")
        if end == "none": t["outro"] = {"l1": "", "l2": "", "cta": "", "word": "", "sub": "", "chips": []}
        th.write_text(json.dumps(t, ensure_ascii=False, indent=1), encoding="utf-8")
        sfx = W / "sfx.json"
        if not sfx.exists(): sfx.write_text(json.dumps({"outro": 0 if end == "none" else 4.5}))
        print(f"🎨 theme: house look · grade {'auto' if '--grade' in args else 'off'} · end card {end}")
    elif "--grade" in args:
        t = json.loads(th.read_text(encoding="utf-8")); t["grade"] = "auto"; th.write_text(json.dumps(t, ensure_ascii=False, indent=1), encoding="utf-8")
    _, out = run(W, "cut_zoom", ["python3", SC / "03_cut_zoom.py", W])
    print("✂️  " + next((l.strip() for l in out.splitlines() if "cutz.mp4" in l), "cutz.mp4 ready"))
    vfr = W / "vfr"
    if vfr.exists(): shutil.rmtree(vfr)
    vfr.mkdir()
    run(W, "frames", ["ffmpeg", "-v", "error", "-i", W / "cutz.mp4", "-vf", "fps=30", "-q:v", "3", "-y", vfr / "%05d.jpg"])
    _, out = run(W, "headcrop", ["python3", SC / "23_headcrop.py", W, "--from", "0"])
    for l in lines(out, "✅", "⚠️"): print("🙂 " + l.lstrip("✅ ").strip())
    ex = SC.parent.parent.parent / "examples" / "scenes.kit.example.js"
    print(f"→ write <work>/scenes.js with KIT.reel([...]) (pattern: {ex}), then: reel.py preview")


# ── compose ────────────────────────────────────────────────────────────────────────────────────────
def compose(W):
    if not (W / "scenes.js").exists(): die("no scenes.js — write KIT.reel([...]) first")
    ref = (SC / "compose.REFERENCE.html").read_text(encoding="utf-8")
    tag = '<script src="moves.js"></script><script src="moves-compose.js"></script>'
    if tag not in ref: die("compose.REFERENCE.html changed — can't place the scene scripts")
    mk = '\n<script src="motion-kit.js"></script>' if (W / "motion-kit.js").exists() else ""
    (W / "compose.html").write_text(ref.replace(tag, tag + mk + '\n<script src="scene-kit.js"></script>\n<script src="scenes.js"></script>', 1), encoding="utf-8")
    shutil.copy2(SC / "scene-kit.js", W / "scene-kit.js")
    for f in ("moves.js",):   # always the plugin's current moves (fixes reach old work folders)
        if (W / f).exists(): (W / f).unlink()


def preview(args):
    W = Path(args[0]).resolve(); compose(W)
    times = [a for a in args[1:] if re.match(r"^\d+(\.\d+)?$", a)]
    p = W / "prev"
    if p.exists(): shutil.rmtree(p)
    _, out = run(W, "preview", ["node", SC / "04_render_frames.js", W, "preview", *(times or ["auto"])])
    errs = [l for l in out.splitlines() if "مشهد متخطّى" in l or "KIT:" in l or "Error" in l]
    for l in errs[:5]: print("⚠️ " + l.strip())
    if not times:
        k = W / "kit_cues.json"
        times = [f"{t:.2f}" for t in json.loads(k.read_text())["preview"]] if k.exists() else []
    if not times: times = [f"{float(f.stem[1:]):.2f}" for f in sorted(p.glob("t*.jpg"))]
    run(W, "sheet", ["bash", SC / "07_contact_sheet.sh", W, W / "sheet.jpg", *times])
    print(f"🖼️  {W / 'sheet.jpg'}  ({len(times)} frames: {' '.join(times)}) — read this one image, fix, repeat; then: reel.py final")


# ── final ──────────────────────────────────────────────────────────────────────────────────────────
def onset_starts(wav):
    import numpy as np, wave
    w = wave.open(str(wav)); sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768
    hop = int(sr * 0.01); n = len(x) // hop; db = 20 * np.log10(np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
    act = db > max(np.percentile(db, 10) + 15, -50); on, quiet = [], 99
    for i, a in enumerate(act):
        if a and quiet >= 20: on.append(i * 0.01)
        quiet = 0 if a else quiet + 1
    return on


def final(args):
    W = Path(args[0]).resolve(); st = state(W); lang = st.get("lang", "ar")
    name = opt(args, "--name", st.get("name") or W.name); state(W, name=name)
    compose(W); t0 = time.time()
    _, out = run(W, "render", ["node", SC / "04_render_frames.js", W, "all"])
    done = next((l.strip() for l in out.splitlines() if l.startswith("تم ")), "")
    # sound: the kit's cues (sfx.json keeps its outro and any hand-made keys you add)
    sp = W / "sfx.json"; sfx = json.loads(sp.read_text()) if sp.exists() else {"outro": 0}
    kc = W / "kit_cues.json"
    if kc.exists() and (len(sfx) <= 1 or sfx.get("_kit")):
        sfx = {"outro": sfx.get("outro", 0), "_kit": True, **json.loads(kc.read_text())["sfx"]}; sp.write_text(json.dumps(sfx, indent=1))
    run(W, "sfx", ["python3", SC / "05_sfx.py", W])
    run(W, "encode", ["bash", SC / "06_encode.sh", W, W / "ad-final.mp4"])
    _, out = run(W, "master", ["bash", SC / "06b_master.sh", W, W / "ad-final.mp4", W / "ad-master.mp4"])
    loud = re.search(r"(-?[\d.]+) LUFS · ذروة (-?[\d.]+)", out)
    run(W, "srt", ["python3", SC / "09_srt.py", W, "ad-master"])
    rc, out = run(W, "safe_check", ["node", SC / "08_safe_check.js", W, "--shot"], ok=(0, 3))
    safe = [l.strip() for l in out.splitlines() if l.strip().startswith(("❌", "ℹ️", "⚠️"))]
    # sync: sentence starts heard in the final vs caps.json
    run(W, "sync_audio", ["ffmpeg", "-v", "error", "-y", "-i", W / "ad-final.mp4", "-vn", "-ac", "1", "-ar", "16000", W / "fa.wav"])
    model = Path(os.environ.get("WHISPER_CPP_MODELS", HOME / "models")) / "ggml-large-v3-turbo-q5_0.bin"
    sync = []
    if model.exists() and shutil.which("whisper-cli"):
        run(W, "sync", ["whisper-cli", "-m", model, "-l", lang, "-f", W / "fa.wav", "-oj", "-of", W / "fa", "-np"])
        heard = [s["offsets"]["from"] / 1000 for s in json.loads((W / "fa.json").read_text())["transcription"] if s["text"].strip()]
        run(W, "cut_audio", ["ffmpeg", "-v", "error", "-y", "-i", W / "cutz.mp4", "-vn", "-ac", "1", "-ar", "16000", W / "ca.wav"])
        on = onset_starts(W / "ca.wav")                                     # voice only, on the cut timeline
        caps = json.loads((W / "caps.json").read_text(encoding="utf-8"))["cards"]
        for i, c in enumerate(caps):
            w0 = c["w"][0]["s"]; h = min(heard, key=lambda x: abs(x - w0)) if heard else w0
            if h == 0.0 and on: h = min(on, key=lambda x: abs(x - w0))          # whisper's first segment always says 0.00
            if abs(h - w0) >= 0.1: sync.append(f"sentence {i} «{c['w'][0]['t']}» at {w0:.2f}s, heard {h:.2f}s")
    keep = json.loads((W / "cut.json").read_text())["keep"]
    seam = ""
    if len(keep) > 1:
        _, out = run(W, "seams", ["python3", SC / "19_seam_check.py", W, W / "ad-final.mp4"], ok=(0, 1, 2, 3))
        seam = (lines(out, "✅", "⚠️", "❌") or [""])[-1]
    deliver = W / "ad-master.mp4"; cover = opt(args, "--cover")
    if cover:
        cmd = ["python3", SC / "28_cover.py", W, cover, "--first", W / "ad-master.mp4"]
        if opt(args, "--cover-t"): cmd += ["--t", opt(args, "--cover-t")]
        run(W, "cover", cmd); deliver = W / "ad-master-cover.mp4"
    D = dur(deliver)
    run(W, "final_sheet", ["ffmpeg", "-v", "error", "-y", "-i", deliver, "-vf", f"fps=6/{max(D, 1):.2f},scale=360:-1,tile=6x1", "-frames:v", "1", W / "final_sheet.jpg"])
    exp = Path(opt(args, "--export", W.parent.parent / "exports" if (W.parent.parent / "exports").exists() else W)).resolve()
    exp.mkdir(parents=True, exist_ok=True)
    files = [(deliver, f"{name}_final.mp4"), (W / "ad-master.srt", f"{name}.srt"), (W / "ad-master.txt", f"{name}_post-caption.txt")]
    if cover: files.append((W / "cover.jpg", f"{name}_cover.jpg"))
    for a, b in files:
        if a.exists(): shutil.copy2(a, exp / b)
    mb = deliver.stat().st_size / 1e6
    print(f"🎬 {name}: {D:.2f}s · {mb:.1f} MB · {('%s LUFS, peak %s' % loud.groups()) if loud else 'loudness ?'} · {done} · {time.time() - t0:.0f}s")
    print(("✅ safe zones · hook · captions under the chin" if rc == 0 else "❌ safe check failed — fix before delivering") + "".join("\n   " + l for l in safe if not l.startswith("ℹ️  ما فيه فشل")))
    print("✅ sync (sentence starts < 0.1 s)" if not sync else "⚠️ sync: " + " · ".join(sync))
    if seam: print(seam)
    print(f"📦 {exp}: " + " · ".join(b for a, b in files if a.exists()) + f"\n🖼️  {W / 'final_sheet.jpg'} — look once, then deliver (nothing is posted anywhere)")
    if rc != 0: sys.exit(3)


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("prep", "script", "cut", "preview", "final"):
        print(__doc__); sys.exit(1)
    {"prep": prep, "script": script, "cut": cut, "preview": preview, "final": final}[sys.argv[1]](sys.argv[2:])

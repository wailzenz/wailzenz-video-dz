# -*- coding: utf-8 -*-
"""خطة القص: يقيس السكتات بالصوت ويطلع مقاطع الكلام.  الاستخدام: python3 01_cut_plan.py <workdir>"""
# ── توافق ويندوز/UTF-8 (مضاف) ─────────────────────────────────────
import sys as _sys, builtins as _bi
try:
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    _sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
_real_open = _bi.open
def _utf8_open(f, mode="r", *a, **k):
    if "b" not in mode:
        k.setdefault("encoding", "utf-8")
    return _real_open(f, mode, *a, **k)
_bi.open = _utf8_open
# ──────────────────────────────────────────────────────────────────
import subprocess, re, json, sys, os
import numpy as np
W = os.path.abspath(sys.argv[1]); SRC = os.path.join(W, "src.mov")
# wailzenz-video-dz (2026-10-20, «be careful when cutting»): the old fixed -32 dB / 0.35 s / 0.13 s pad treated soft Darija word
# endings (-36…-44 dB on a phone recording) as silence and clipped them, and removed every breathing pause → choppy speech.
#   • silence = the clip's own noise floor + 14 dB (clamped to -52…-32 dB), not a fixed level
#   • only pauses ≥ MIND are cut (natural breaths stay) · more room kept AFTER a word (tails) than before it
#   • every cut is then checked against the voice energy and widened until it no longer touches speech
MIND = float(os.environ.get("CUT_MIN_SILENCE", "0.55"))
PAD_HEAD, PAD_TAIL, MERGE, BLIP = 0.14, 0.22, 0.30, 0.45   # BLIP: a breath/click up to this long doesn't split a pause
TAIL = 0.7   # سكتة بآخر الفيديو بعد آخر كلمة (الصوت ما ينقص فجأة) — يمسك آخر فريم ويسكت

dur = float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
    "-of","csv=p=0", SRC], capture_output=True, text=True).stdout.strip())
raw = subprocess.run(["ffmpeg","-v","error","-i",SRC,"-vn","-ac","1","-ar","16000","-f","f32le","-"], capture_output=True).stdout
x = np.frombuffer(raw, np.float32); HOP = 160                                   # 10 ms
nfr = len(x) // HOP
rms = 20 * np.log10(np.sqrt((x[:nfr * HOP].reshape(nfr, HOP) ** 2).mean(1)) + 1e-9)
floor = float(np.percentile(rms, 10))
thr = min(-32.0, max(-52.0, floor + 14))
peak = float(np.percentile(rms, 90))           # typical loud speech
breath_max = peak - 7                          # a sound that never gets louder than this between two silences = breath/click
NOISE = f"{thr:.1f}dB"
out = subprocess.run(["ffmpeg","-hide_banner","-nostats","-i",SRC,"-af",
    f"silencedetect=noise={NOISE}:d=0.20","-f","null","-"], capture_output=True, text=True).stderr

sil=[]; s=None
for m in re.finditer(r"silence_(start|end): ([0-9.]+)", out):
    k,v = m.group(1), float(m.group(2))
    if k=="start": s=v
    else:
        sil.append(((0.0 if s is None else s), v)); s=None
if s is not None: sil.append((s,dur))
# join silences split by a short breath/click, then keep only real pauses (≥ MIND)
_j=[]
for a,b in sil:
    gap = rms[int(_j[-1][1]*100):int(a*100)] if _j else None
    if _j and a-_j[-1][1]<BLIP and (gap.size == 0 or gap.max() < breath_max): _j[-1]=(_j[-1][0],b)
    else: _j.append((a,b))
sil=[(a,b) for a,b in _j if b-a>=MIND]

keep=[]; cur=0.0
for a,b in sil:
    if a-cur>0.01: keep.append([cur,a])
    cur=b
if dur-cur>0.01: keep.append([cur,dur])
keep=[[max(0,a-PAD_HEAD),min(dur,b+PAD_TAIL)] for a,b in keep]

# guard: push every edge out of the voice (soft endings / breathy starts sit just under the threshold)
speech = max(thr, peak - 11)   # edges move out while the level is word-like (soft endings included, breaths not)
def voiced(t): i = int(t * 100); return 0 <= i < nfr and rms[i] > speech
for seg in keep:
    k = 0
    while k < 30 and seg[1] < dur and voiced(seg[1]): seg[1] = min(dur, seg[1] + 0.01); k += 1
    k = 0
    while k < 20 and seg[0] > 0 and voiced(seg[0] - 0.01): seg[0] = max(0, seg[0] - 0.01); k += 1

m=[]
for seg in keep:
    if m and seg[0]-m[-1][1]<MERGE: m[-1][1]=max(m[-1][1],seg[1])
    else: m.append(seg)
m=[x for x in m if x[1]-x[0]>=0.30]
tot=sum(b-a for a,b in m)
json.dump({"keep":m,"total":tot,"src_dur":dur,"tail":TAIL,"cut_noise_db":round(thr,1),"cut_min_silence":MIND},
          open(os.path.join(W,"cut.json"),"w"), indent=1)
print(f"مقاطع={len(m)}  الباقي={tot:.2f}s  انشال={dur-tot:.2f}s ({(dur-tot)/dur*100:.0f}%)  · السكوت تحت {NOISE} (أرضية الضجيج {floor:.0f}dB) · أقل سكتة تنقص {MIND}s")
for a,b in m: print(f"  {a:7.2f} -> {b:7.2f}  ({b-a:5.2f}s)")
bad = []
for (a0, a1), (b0, b1) in zip(m, m[1:]):
    g = rms[int(a1 * 100):int(b0 * 100)]
    if (g > speech + 4).sum() >= 4: bad.append(f"{a1:.2f}→{b0:.2f}")
print("✅ ولا قصة تمسّ الكلام" if not bad else "⚠️ قصات فيها صوت (اسمعها): " + " · ".join(bad))

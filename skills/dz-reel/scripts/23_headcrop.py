# -*- coding: utf-8 -*-
"""🆕 v3.8 القصّ من فوق الراس — ثابت طول الفيديو بكل كرت (نص الشاشة · R_DOWN · R_LOWER)
⛔ قاعدة المستخدم (نبّه أكثر من مرة وزعل — 27 و28 سبتمبر): القصّ يبدأ من فوق راسه بمساحة آمنة،
**ثابت طول الفترة — بلا تتبع ولا كاميرا تلحقه** («الماسك فوق») فلا ينقص وجهه ولا يطلع فراغ سقف كبير.

الشغل: راصد الوجه (Vision بالماك) على فريمات vfr/ ← أعلى الراس بكل فريم = أعلى صندوق الوجه − 0.35 من طوله (الشعر)
← نأخذ **أعلى نقطة وصلها راسه بالفيديو كله** (الشريحة 3٪ — تتجاهل رصداً شاذاً) ناقص هامش PAD
← رقم واحد يكتب <work>/studio.json ← "cardTop" (نسبة من ارتفاع الفريم). المحرّك يبدأ قصّ الكرت منه.

python3 23_headcrop.py <work> [--from 2.0]   # بعد الخطوة 6 · --from = بداية أول كرت (ملء الشاشة قبله ما يحتاج)
theme.json ← "cardZoom" (افتراضي 1): تقريب داخل الكرت — يفيد لو تحت جسمه نص محروق أو فراغ كبير

wailzenz-video-dz (2026-10-20): also writes studio.json → "face" = the face track of the whole video
({step, top, chin} — fractions of the frame height every 0.1 s) for the rule «captions never cover the face — always
under the chin»: the engine puts every caption that sits over the full-screen picture below the chin. Run it on every video.
"""
import json, os, statistics, subprocess, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _landscape import _facetrack

HAIR = 0.35      # الشعر فوق صندوق Vision = 20-35٪ من طول الوجه (مقاس بالعين 28 سبتمبر · 0.50 خلّى فراغ كبير فوقه)
STEP = 3         # كل ثالث فريم (10 بالثانية) يكفي
PAD = 0.015      # هامش صغير فوق أعلى نقطة للراس — «مساحة آمنة» مو سقف فاضي
BEARD = 0.10     # wailzenz-video-dz: Vision's box ends at the jaw line — a beard reaches ~10% of the face height below it
FPS = 30

def main(W, t0=0.0):
    vfr = os.path.join(W, "vfr")
    files = sorted(f for f in os.listdir(vfr) if f.endswith(".jpg"))
    if not files: sys.exit("❌ ما فيه فريمات بـvfr/ — شغّل الخطوة 6 أول")
    ft = _facetrack()
    if not ft: print("⚠️ راصد الوجه مو متوفر (ويندوز / بلا Xcode) — القصّ يبقى على faceAnchor"); return
    with tempfile.TemporaryDirectory() as tmp:
        for f in files[::STEP]: os.symlink(os.path.join(os.path.abspath(vfr), f), os.path.join(tmp, f))
        out = os.path.join(tmp, "ft.json")
        subprocess.run([ft, tmp, out], check=True, capture_output=True)
        rows = json.load(open(out))
    track(W, rows, len(files[::STEP]))
    pts = []
    for r in rows:
        fc = r.get("face")
        if not fc: continue
        t = (int(r["f"].split(".")[0]) - 1) / FPS
        if t < t0: continue
        pts.append((t, max(0.0, fc["y"] - HAIR * fc["h"]), fc["x"] + fc["w"] / 2))
    if len(pts) < 3: print("⚠️ الوجه ما انرصد كفاية — القصّ يبقى على faceAnchor"); return
    tops = sorted(p[1] for p in pts)
    hi = tops[int(len(tops) * 0.03)]                      # أعلى نقطة وصلها الراس (بلا الشواذ)
    top = round(max(0.0, hi - PAD), 4)
    sp = os.path.join(W, "studio.json")
    st = json.load(open(sp)) if os.path.exists(sp) else {}
    st.pop("head", None); st["cardTop"] = top
    json.dump(st, open(sp, "w"), ensure_ascii=False)
    print(f"✅ قصّ الكرت ثابت من {top:.0%} من أعلى الفريم (أعلى نقطة للراس {hi:.0%} ناقص هامش) · انكتب studio.json ← cardTop")

def track(W, rows, n):
    """wailzenz-video-dz: the face track for the chin rule → studio.json "face" (None where no face was found)."""
    top, chin = [None] * n, [None] * n
    for r in rows:
        fc = r.get("face")
        if not fc: continue
        i = (int(r["f"].split(".")[0]) - 1) // STEP
        if 0 <= i < n:
            top[i] = round(max(0.0, fc["y"] - HAIR * fc["h"]), 4)
            chin[i] = round(min(1.0, fc["y"] + fc["h"] * (1 + BEARD)), 4)
    sp = os.path.join(W, "studio.json")
    st = json.load(open(sp)) if os.path.exists(sp) else {}
    got = [c for c in chin if c is not None]
    if len(got) < 3:
        st.pop("face", None); json.dump(st, open(sp, "w"), ensure_ascii=False)
        print("⚠️ الوجه ما انرصد كفاية — قاعدة «الكابشن تحت الذقن» تتحقق بالعين من اللقطات"); return
    st["face"] = {"step": round(STEP / FPS, 4), "top": top, "chin": chin}
    json.dump(st, open(sp, "w"), ensure_ascii=False)
    low = sorted(got)[int(0.9 * (len(got) - 1))]
    print(f"✅ تتبع الوجه ({len(got)}/{n} لقطة) · الذقن يوصل لـ{low:.0%} من الطول ← انكتب studio.json ← face"
          + (" · لقطة قريبة: الكابشن تحت الذقن يحتاج رفع الفيديو بالمشاهد ملء الشاشة (المحرّك يديرها)" if low > 0.64 else ""))

if __name__ == "__main__":
    a = sys.argv[1:]
    t0 = float(a[a.index("--from") + 1]) if "--from" in a else 0.0
    main(a[0] if a and a[0] != "--from" else ".", t0)

# -*- coding: utf-8 -*-
"""يبني توقيتات الكابشن على التايم-لاين الجديد.  python3 02_captions.py <workdir>
يقرأ: cut.json · a.json (وِسبر) · fixes.json  ← {"fix":[[كلمات الجملة 0],...], "hot":[كلمات تُظلَّل]}
عدد كلمات كل جملة في fix لازم يساوي عدد كلمات وِسبر لنفس الجملة (عشان التوقيتات تبقى مضبوطة)."""
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
import json, sys, os, re
W=os.path.abspath(sys.argv[1])
keep=json.load(open(os.path.join(W,"cut.json")))["keep"]
tr=json.load(open(os.path.join(W,"a.json")))
fx=json.load(open(os.path.join(W,"fixes.json")))
FIX, HOT = fx["fix"], set(fx.get("hot",[]))
FXMAP = fx.get("fx", {})   # 🎬 حركات الكلمة العربية (v3.1): {"خلاص":"drop","متصلة":"type",…} — drop · shake · crack · type · pulse · stretch · slam
# 🇩🇿 Arabic gloss after French/English terms: "gloss": {"normal": "عادية", "Claude Code": "كلود كود"} → normal "عادية".
#    The gloss is an extra caption item (not spoken) that appears with the term's last word. Latin terms are
#    highlighted by default ("hot_latin": false turns that off); "gloss_quotes" sets the marks (default "").
GLOSS = {k.strip(): v for k, v in fx.get("gloss", {}).items()}
GQ = fx.get("gloss_quotes", '""')
# An English or French video (no Arabic letters in fixes.json) has no glosses and no automatic Latin highlight —
# the gloss rule is for French/English terms inside Darija.
ARABIC = any(re.search(r"[\u0600-\u06FF]", t) for f in FIX for t in ([f] if isinstance(f, str) else f) if t)
HOT_LATIN = fx.get("hot_latin", ARABIC)
GLOSS_REPEAT = fx.get("gloss_repeat", False)   # False = gloss a term the first time it appears in the video only
GLOSSED = set()
LAT = re.compile(r"[A-Za-zÀ-ɏ]")
GPUNCT = ".,!?؟،:;…«»\"'"
UNGLOSSED = []
def add_gloss(o):
    out, i = [], 0
    while i < len(o):
        for n in range(min(6, len(o) - i), 0, -1):          # longest Latin phrase with a gloss wins
            words = o[i:i + n]
            if not all(LAT.search(w["t"]) for w in words): continue
            key = " ".join(w["t"] for w in words).strip(GPUNCT)
            if key in GLOSS:
                last = words[-1]
                out.extend(words)
                if GLOSS_REPEAT or key not in GLOSSED:
                    tail = ""                     # «software،» → «software "برمجيات"،» — punctuation moves after the gloss
                    while last["t"] and last["t"][-1] in "،,.?!؟:;…": tail = last["t"][-1] + tail; last["t"] = last["t"][:-1]
                    out.append({"t": GQ[0] + GLOSS[key] + GQ[-1] + tail, "s": last["s"], "e": last["e"], "hot": False, "gloss": True})
                else:
                    last["_glossed"] = True   # already explained earlier in the video
                GLOSSED.add(key)
                i += n; break
        else:
            out.append(o[i]); i += 1
    run = []                                                 # Latin runs not followed by a gloss → reminder
    for w in out + [{"t": "", "gloss": False}]:
        if w.pop("_glossed", False): run = []; continue
        if LAT.search(w["t"]) and not w.get("gloss"): run.append(w["t"]); continue
        if run and not w.get("gloss"): UNGLOSSED.append(" ".join(run))
        run = []
    return out

def seg_of(t):
    best,bd=0,1e9
    for i,(a,b) in enumerate(keep):
        if a<=t<=b: return i
        d=min(abs(t-a),abs(t-b))
        if d<bd: bd,best=d,i
    return best
off=[];acc=0.0
for a,b in keep: off.append(acc); acc+=b-a
def newt(t,si):
    a,b=keep[si]; return off[si]+(max(a,min(b,t))-a)

cards=[]
for i,seg in enumerate(tr["segments"]):
    ws=seg.get("words",[]); f=FIX[i]
    if not ws: continue
    # 🆕 v3.5 (حلقة ← ريلات): "seg" = رقم القطعة بـcut.json — لازم لما الهوك مأخوذ من وسط الجواب (القطع متداخلة بالوقت
    #    وأقرب قطعة تطلع غلط، فكابشن الجواب ينحط فوق الهوك). 20_episode_cuts.py يكتبه لحاله.
    pin=isinstance(seg.get("seg"),int)
    si=seg["seg"] if pin else seg_of((ws[0]["start"]+ws[-1]["end"])/2)
    if isinstance(f,str):
        # نص بدل قائمة = وِسبر هلوس بهالجملة (كلماته غلط وعددها ما يفيد) → الكلمات الصحيحة تتوزّع على مدة الجملة بنسبة طولها
        toks=f.split(); s0,e0=ws[0]["start"],ws[-1]["end"]; tot=sum(len(t) for t in toks) or 1; c=0; pairs=[]
        for t in toks: a0=s0+(e0-s0)*c/tot; c+=len(t); pairs.append((t,a0,s0+(e0-s0)*c/tot))
    else:
        if len(ws)!=len(f):
            sys.exit(f"❌ الجملة {i}: وِسبر {len(ws)} كلمة، fixes.json {len(f)} — لازم يتساوون (أو اكتبها نص وحدة إذا وِسبر هلوس)")
        pairs=[(txt,w["start"],w["end"]) for w,txt in zip(ws,f) if txt]   # "" = الكلمة تنشال من الكابشن (الصوت يبقى)
    if not pairs: continue
    o=[]
    for txt,ws0,we0 in pairs:
        if pin: s1,e1=newt(ws0,si),newt(we0,si)
        else:
            # 🐛 v4.0.1: كل كلمة بقطعتها هي — القص الضيّق يقسم الجملة على عدة قطع، وربطها كلها بقطعة الوسط
            #    يلصق الكلمات اللي برّاها على طرفها فالكابشن يتأخر لين ~1.5 ث
            sw=seg_of(ws0); s1,e1=newt(ws0,sw),newt(we0,max(sw,seg_of(we0)))
        if e1<=s1: e1=s1+0.12
        _w={"t":txt,"s":round(s1,3),"e":round(e1,3),"hot":txt in HOT or txt in FXMAP or (HOT_LATIN and bool(LAT.search(txt)))}
        if txt in FXMAP: _w["fx"]=FXMAP[txt]
        o.append(_w)
    o=add_gloss(o)
    a,b=keep[si]; lo,hi=(off[si],off[si]+(b-a)) if pin else (0.0,acc)
    cs=max(o[0]["s"]-0.10, lo)
    ce=min(max(x["e"] for x in o)+0.28, hi)
    cards.append({"s":round(cs,3),"e":round(ce,3),"w":o})
cards.sort(key=lambda c:c["s"])
for i in range(len(cards)-1):
    if cards[i]["e"]>cards[i+1]["s"]: cards[i]["e"]=round(cards[i+1]["s"]-0.02,3)
_tail=float(json.load(open(os.path.join(W,"cut.json"))).get("tail",0) or 0)
json.dump({"total":round(acc+_tail,3),"cards":cards},open(os.path.join(W,"caps.json"),"w"),ensure_ascii=False,indent=1)
print("كروت:",len(cards)," المدة:",round(acc,2))
for c in cards: print(f"{c['s']:6.2f}-{c['e']:6.2f}  "+" ".join(x['t'] for x in c['w']))
if UNGLOSSED and ARABIC:
    print("⚠️ French/English terms without an Arabic gloss (add them to fixes.json → \"gloss\"): " + " · ".join(dict.fromkeys(UNGLOSSED)))

/* Example scenes from a real reel (wailzenz-video-dz house style). Copy the patterns, not the content:
   • w('word', n) finds the n-th time a word is said in caps.json — every scene is tied to word times
   • SCENES alternates R_UP (face top, panel bottom) / R_DOWN / R_LOWER / R_FULL — and, since v1.1, the overlay bands
     R_OVT / R_OVB (full-screen face, panel in a band on top or at the bottom; see sStep / sFlow at the end)
   • panels are visuals only — they never repeat the caption. Load it in compose.html after motion-kit.js. */
/* test1 v3 — مشاهد الريل بقواعد المستخدم (20 أكتوبر):
   1) اللوحة ما تكرر كلمات الكابشن — رسوم بس (أيقونات، واجهات، لوحات)   2) القص في السكوت بس   3) اللوحة مرة فوق ومرة تحت.
   كل توقيت من كلماته بـcaps.json (w(...)) — لو تغيّر القص، المشاهد تمشي معه. */

const CW = () => CAPS.flatMap(c => c.w.filter(x => !x.gloss));            // كلماته (بلا الترجمات)
const w = (txt, n = 0) => { const L = CW().filter(x => x.t.replace(/[،.؟"]/g, '').trim() === txt); return (L[n] || L[L.length - 1] || { s: 0 }).s; };
const cs = i => CAPS[i].s, ce = i => CAPS[i].e;
let T0 = {};   // كل اللحظات، تنحسب مرة وحدة بعد ما caps.json يوصل

MV.ready(() => {
  T0 = {
    team: cs(1) - 0.02, term: cs(2) - 0.02, tl: cs(3), kh: cs(4) - 0.06, khOut: w('الخلاصة') + 0.42, vibe: w('من') + 0.2,
    tools: cs(5) - 0.02, bdoun: w('بدون') - 0.05, board: w('الوضع') - 0.3,
  };
  SCENES = [
    { s: 0, e: T0.team, m: R_FULL },                          // الهوك: «طبقات» ورا الراس
    { s: T0.team, e: T0.term, m: R_UP },                      // وجهه فوق · الفريق تحت
    { s: T0.term, e: T0.kh, m: R_LOWER },                     // طرفية ← تايملاين (فوق، كبير)
    { s: T0.kh, e: T0.vibe, m: R_FULL, nocap: true },         // «الخلاصة» والفيديو داخل حروفها
    { s: T0.vibe, e: T0.tools, m: R_UP },                     // وجهه فوق · وصف ← ذكاء ← كود تحت
    { s: T0.tools, e: T0.bdoun, m: R_DOWN, gb: 470 },         // أدوات تتركّب فوق · وجهه تحت
    { s: T0.bdoun, e: T0.board, m: R_UP },                    // وجهه فوق · الفريق ينشطب تحت
    { s: T0.board, e: 99, m: R_LOWER },                       // لوحة المقارنة (فوق، كبير)
  ];
});

/* ── أدوات رسم صغيرة (ألوان الثيم) ── */
function node(cx, cy, r, k, drawIcon) {
  if (k <= 0) return; X.save(); X.globalAlpha *= ease(k); X.translate(cx, cy); const s = lerp(0.92, 1, ease(k)); X.scale(s, s);
  sh(30, 12, 0.22); X.fillStyle = cINK(0.08); X.beginPath(); X.arc(0, 0, r, 0, 7); X.fill(); nsh();
  X.strokeStyle = ACC; X.lineWidth = 4; X.beginPath(); X.arc(0, 0, r, 0, 7); X.stroke(); drawIcon(r); X.restore();
}
function arrow(x0, x1, y, k) {
  if (k <= 0) return; const x = lerp(x0, x1, ease(k)); X.save(); X.strokeStyle = cINK(0.55); X.lineWidth = 5; X.lineCap = 'round';
  X.setLineDash([2, 14]); X.beginPath(); X.moveTo(x0, y); X.lineTo(x, y); X.stroke(); X.setLineDash([]);
  if (k > 0.95) { X.fillStyle = cINK(0.55); X.beginPath(); X.moveTo(x1 + 4, y); X.lineTo(x1 - 14, y - 11); X.lineTo(x1 - 14, y + 11); X.fill(); } X.restore();
}
function bubbleIcon(r) { X.fillStyle = INK; rr(-r * 0.5, -r * 0.38, r, r * 0.66, 16); X.fill(); X.beginPath(); X.moveTo(-r * 0.2, r * 0.26); X.lineTo(-r * 0.36, r * 0.5); X.lineTo(r * 0.02, r * 0.27); X.fill();
  X.fillStyle = BG; [-0.22, 0, 0.22].forEach(d => { X.beginPath(); X.arc(d * r, -r * 0.05, r * 0.07, 0, 7); X.fill(); }); }
function codeIcon(r) { X.strokeStyle = INK; X.lineWidth = r * 0.12; X.lineCap = 'round'; X.lineJoin = 'round';
  X.beginPath(); X.moveTo(-r * 0.2, -r * 0.32); X.lineTo(-r * 0.48, 0); X.lineTo(-r * 0.2, r * 0.32); X.stroke();
  X.beginPath(); X.moveTo(r * 0.2, -r * 0.32); X.lineTo(r * 0.48, 0); X.lineTo(r * 0.2, r * 0.32); X.stroke();
  X.beginPath(); X.moveTo(r * 0.08, -r * 0.4); X.lineTo(-r * 0.08, r * 0.4); X.stroke(); }
function appIcon(cx, cy, s, c) { X.save(); X.strokeStyle = c; X.lineWidth = s * 0.07; X.lineJoin = 'round'; rr(cx - s / 2, cy - s * 0.38, s, s * 0.76, s * 0.1); X.stroke();
  X.beginPath(); X.moveTo(cx - s / 2, cy - s * 0.18); X.lineTo(cx + s / 2, cy - s * 0.18); X.stroke();
  X.fillStyle = c; [0, 1, 2].forEach(i => { X.beginPath(); X.arc(cx - s * 0.36 + i * s * 0.1, cy - s * 0.28, s * 0.03, 0, 7); X.fill(); }); X.restore(); }
function stackIcon(cx, cy, s, n, c) { X.save(); X.strokeStyle = c; X.lineWidth = s * 0.06; X.lineJoin = 'round';
  for (let i = 0; i < n; i++) { const y = cy + s * 0.32 - i * s * 0.22; X.beginPath(); X.moveTo(cx - s * 0.5, y); X.lineTo(cx, y - s * 0.16); X.lineTo(cx + s * 0.5, y); X.lineTo(cx, y + s * 0.16); X.closePath(); X.stroke(); } X.restore(); }
function gearIcon(cx, cy, s, c) { X.save(); X.translate(cx, cy); X.strokeStyle = c; X.lineWidth = s * 0.1; for (let i = 0; i < 8; i++) { X.rotate(Math.PI / 4); X.beginPath(); X.moveTo(0, -s * 0.34); X.lineTo(0, -s * 0.5); X.stroke(); }
  X.beginPath(); X.arc(0, 0, s * 0.3, 0, 7); X.stroke(); X.beginPath(); X.arc(0, 0, s * 0.1, 0, 7); X.stroke(); X.restore(); }
function warnIcon(cx, cy, s, c, k) {
  X.save(); X.globalAlpha *= k; X.strokeStyle = c; X.lineWidth = s * 0.09; X.lineJoin = 'round'; X.lineCap = 'round';
  X.beginPath(); X.moveTo(cx, cy - s * 0.48); X.lineTo(cx + s * 0.52, cy + s * 0.42); X.lineTo(cx - s * 0.52, cy + s * 0.42); X.closePath(); X.stroke();
  X.beginPath(); X.moveTo(cx, cy - s * 0.16); X.lineTo(cx, cy + s * 0.12); X.stroke();
  X.beginPath(); X.arc(cx, cy + s * 0.27, s * 0.045, 0, 7); X.fillStyle = c; X.fill(); X.restore();
}

/* 1 — (وجهه فوق) فريق من 6 developers، وعلى «أنا» يتلوّن واحد بس */
function sTeam(t) {
  if (!T0.team || t < T0.team || t > T0.term) return;
  panelIn(t, T0.team, T0.term, () => {
    MK.iconArray(t, { s: w('developers'), e: T0.term, box: { x: 200, y: 290, w: 680, h: 150 }, total: 6, cols: 6, hot: 1, fill: 0.8, hotAt: w('أنا'), pick: 'first' });
  });
}

/* 2 — طرفية (بلا كلمات الكابشن) */
function sTerminal(t) {
  if (!T0.term || t < T0.term || t > T0.tl) return;
  FX.terminalType(MV, t, { s: w('Claude'), out: T0.tl - 0.12, y: 600, title: 'zsh', cmd: 'claude "make my reels editor"',
    lines: ['› reading the project', '› writing the skills', '› captions · motion · sound'], done: 'Done', note: null });
}

/* 3 — تايملاين المونتاج: الخطوات تصوير ← قص ← نشر، و«رندر» ينضغط على «هذا» */
function sTimeline(t) {
  if (!T0.tl || t < T0.tl || t > T0.kh) return;
  MK.timeline(t, { s: T0.tl + 0.1, e: T0.kh, box: { x: 70, y: 330, w: 940, h: 470 }, title: 'reel.mp4', steps: ['تصوير', 'قص', 'نشر'], clickAt: w('هذا') });
}

/* 4 — «الخلاصة»: الكلمة ضخمة والفيديو داخل حروفها (الجملة nocap بهالنافذة) */
function sKhulasa(t) {
  if (!T0.kh || t < T0.kh || t > T0.vibe) return;
  FX.videoText(MV, t, { text: 'الخلاصة', s: T0.kh + 0.04, out: T0.khOut, video: Y => MV.video(Y) });
}

/* 5 — (وجهه فوق) vibe coding بالرسم: وصف ← ذكاء ← كود */
function sVibe(t) {
  if (!T0.vibe || t < T0.vibe || t > T0.tools) return;
  const aAI = w('AI'), a1 = T0.vibe + 0.15;
  panelIn(t, T0.vibe, T0.tools, () => {
    node(260, 368, 74, pr(t, a1, a1 + 0.3), bubbleIcon);
    arrow(350, 450, 368, pr(t, a1 + 0.6, a1 + 1.2));
    node(540, 368, 74, pr(t, aAI - 0.1, aAI + 0.2), r => iSpark(0, 0, r * 1.05, ACC));
    arrow(630, 730, 368, pr(t, aAI + 0.35, aAI + 0.8));
    node(820, 368, 74, pr(t, aAI + 0.8, aAI + 1.1), codeIcon);
  });
}

/* 6 — (وجهه تحت) أدوات تتركّب: 6 مربعات أيقونات تطلع مع «نبني»، أول 3 تنوّر مع «أداة» والباقي مع «software» */
const TOOL_ICONS = [iFile, iCut, iZoom, iCaption, iSpark, iCheck];
function sTools(t) {
  if (!T0.tools || t < T0.tools || t > T0.bdoun) return;
  const s0 = w('نبني'), hA = w('أداة'), hB = w('software', 2);
  panelIn(t, T0.tools, T0.bdoun, () => {
    TOOL_ICONS.forEach((ic, i) => {
      const k = pr(t, s0 + i * 0.12, s0 + i * 0.12 + 0.28); if (k <= 0) return;
      const cx = 540 + (2.5 - i) * 130, cy = 368, sz = 108, lit = t >= (i < 3 ? hA : hB);
      X.save(); X.globalAlpha *= ease(k); X.translate(cx, cy + (1 - ease(k)) * 18);
      X.fillStyle = lit ? ACC : cINK(0.07); rr(-sz / 2, -sz / 2, sz, sz, 26); X.fill();
      ic(0, 0, 60, lit ? onACC() : INK, 1); X.restore();
    });
  });
}

/* 7 — (وجهه فوق) الفريق يرجع رمادي، و✕ تخبط عليه مع «developers» */
function sNoDevs(t) {
  if (!T0.bdoun || t < T0.bdoun || t > T0.board) return;
  const hit = w('developers', 1);
  panelIn(t, T0.bdoun, T0.board, () => {
    MK.iconArray(t, { s: T0.bdoun + 0.05, e: T0.board, box: { x: 200, y: 290, w: 680, h: 150 }, total: 6, cols: 6, hot: 0, fill: 0.6, color: cINK(0.45) });
    const k = pr(t, hit, hit + 0.22); if (k <= 0) return;
    const sc = lerp(1.6, 1, ease(k)); X.save(); X.translate(540, 368); X.scale(sc, sc); X.globalAlpha *= ease(k);
    X.strokeStyle = ACC; X.lineWidth = 22; X.lineCap = 'round';
    X.beginPath(); X.moveTo(-300, -80); X.lineTo(300, 80); X.moveTo(300, -80); X.lineTo(-300, 80); X.stroke(); X.restore();
  });
}

/* 8 — المقارنة بالرسم: تطبيق بسيط ✓ (يمين) · نظام كبير بطبقات ⚠ (يسار) — الكلمات تبقى بالكابشن بس */
function sBoard(t) {
  if (!T0.board || t < T0.board || t > 46) return;
  const out = 1 - pr(t, ce(CAPS.length - 1) + 0.4, ce(CAPS.length - 1) + 0.7);
  const aN = w('العادي'), aD = w('مش'), aS = w('softwares'), aK = w('skills'), aDev = w('development');
  X.save(); X.globalAlpha *= out;
  const kA = ease(pr(t, T0.board + 0.3, T0.board + 0.65));
  if (kA > 0) { const x = 565, y = 300, ww = 445, h = 600; X.save(); X.globalAlpha *= kA; X.translate(0, (1 - kA) * 24);
    card(x, y, ww, h, 40, 1); appIcon(x + ww / 2, y + 190, 190, INK); iCheck(x + ww / 2, y + 430, 150, ACC, cl(pr(t, aN, aN + 0.4), 0, 1)); X.restore(); }
  const kD = ease(pr(t, aD, aD + 0.4));
  if (kD > 0) { X.save(); X.globalAlpha *= 0.5; X.fillStyle = ACC; rr(538, 600 - 300 * kD, 4, 600 * kD, 2); X.fill(); X.restore(); }
  const kB = ease(pr(t, aS, aS + 0.35));
  if (kB > 0) { const x = 70, y = 300, ww = 445, h = 600; X.save(); X.globalAlpha *= kB; X.translate(0, (1 - kB) * 24);
    card(x, y, ww, h, 40, 1); stackIcon(x + ww / 2, y + 200, 210, 3, INK);
    warnIcon(x + ww / 2, y + 400, 110, ACC, cl(pr(t, aS + 0.3, aS + 0.7), 0, 1));
    const kG = pr(t, aK, aK + 0.3); if (kG > 0) { X.save(); X.globalAlpha *= ease(kG); gearIcon(x + 110, y + 520, 80, ACC); X.restore(); }
    const kC = pr(t, aDev, aDev + 0.3); if (kC > 0) { X.save(); X.globalAlpha *= ease(kC); X.translate(x + ww - 110, y + 520); codeIcon(46); X.restore(); }
    X.restore(); }
  X.restore();
}

/* ── v1.1 — overlay bands: his face keeps the whole frame, the panel sits in a band, no black background ──
   Add them to SCENES like any layout, from word times, e.g. inside MV.ready:
     BANDS.top    = { s: w('أول'), e: w('ثاني'), step: 1, of: 3 };   SCENES.push({ s: BANDS.top.s, e: BANDS.top.e, m: R_OVT });
     BANDS.bottom = { s: w('ثاني'), e: w('ثالث') };                  SCENES.push({ s: BANDS.bottom.s, e: BANDS.bottom.e, m: R_OVB });
   (keep SCENES sorted by time). R_OVB lifts the caption above the band — on a close-up use R_OVT instead. */
const BANDS = { top: null, bottom: null };

/* top band · glass card — step pill, two icons, a segmented progress bar (the idea, never the caption words) */
function sStep(t) {
  const B = BANDS.top; if (!B || t < B.s || t > B.e) return;
  panelIn(t, B.s, B.e, () => {
    glass(150, 270, 780, 196, 34, 0.58);                                   // semi-transparent card in the theme colour
    X.fillStyle = ACC; rr(190, 298, 118, 46, 23); X.fill();
    const two = n => String(n).padStart(2, '0');
    T(two(B.step) + ' / ' + two(B.of), 249, 322, '800 28px ' + FONT, BG, 'center', 'ltr');   // numbers → 'ltr', or «03 / 01»
    const k1 = pr(t, B.s + 0.3, B.s + 0.8), k2 = pr(t, B.s + 0.9, B.s + 1.4);
    node(430, 350, 46, k1, bubbleIcon); arrow(486, 604, 350, k2); node(660, 350, 46, k2, codeIcon);
    const n = B.of, sw = (700 - (n - 1) * 12) / n, f = lerp(B.step - 1, B.step, ease(pr(t, B.s + 0.4, B.s + 1.0)));
    for (let q = 0; q < n; q++) {
      const x = 190 + q * (sw + 12); X.fillStyle = cINK(0.22); rr(x, 428, sw, 12, 6); X.fill();
      const k = cl(f - q, 0, 1); if (k > 0) { X.fillStyle = ACC; rr(x, 428, sw * k, 12, 6); X.fill(); }
    }
  });
}

/* bottom band · transparent — icons straight on the video, a dark soft shadow (dsh) for contrast */
function sFlow(t) {
  const B = BANDS.bottom; if (!B || t < B.s || t > B.e) return;
  panelIn(t, B.s, B.e, () => {
    const k = i => ease(pr(t, B.s + 0.25 + i * 0.45, B.s + 0.6 + i * 0.45));
    X.save(); dsh();
    X.globalAlpha *= k(0); appIcon(330, 368, 120, INK); X.restore();
    X.save(); dsh(); X.globalAlpha *= k(1); stackIcon(540, 368, 110, 3, ACC); X.restore();
    X.save(); dsh(); X.globalAlpha *= k(2); gearIcon(750, 368, 110, INK); X.restore();
    arrow(400, 470, 368, pr(t, B.s + 0.5, B.s + 0.9)); arrow(610, 680, 368, pr(t, B.s + 0.95, B.s + 1.35));
  });
}

SCENE_LIST.push(['sTeam', sTeam], ['sTerminal', sTerminal], ['sTimeline', sTimeline], ['sVibe', sVibe], ['sTools', sTools],
                ['sNoDevs', sNoDevs], ['sBoard', sBoard], ['sKhulasa', sKhulasa], ['sStep', sStep], ['sFlow', sFlow]);

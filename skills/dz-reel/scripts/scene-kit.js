/* ═══ wailzenz-video-dz scene kit — the house style as ready-made blocks (2026-10-20) ═══
   One short list per video instead of hand-written scene code. Loaded after the engine, before scenes.js:
     <script src="scene-kit.js"></script><script src="scenes.js"></script>        (reel.py does this)

   KIT.reel([ scene, scene, … ])   — scenes play in order; each runs until `to` (the last one to the end).
   Times are spoken words from caps.json: 'hour' (1st time) · 'hour#1' (2nd time) · 'hour+0.2' · "doesn't-0.1" · '^1' (sentence 1 starts)
   or plain seconds.

   scene = {
     layout: 'R_OVT' | 'R_OVB' | 'R_UP' | 'R_DOWN' | 'R_LOWER' | 'R_FULL' | 'R_OFF',  to: <time>,  nocap: true?,
     snap:  <time> | {at, back, to:1.16},      // snap zoom on a word (hook energy) — video layer
     panel: {                                    // a panel in the layout's slot (band / split half), drawn with panelIn
       from, to,                                 // default: the scene's own window
       glass: true,                              // semi-transparent card (default on for R_OVT / R_OVB / R_FULL)
       pill: '+1h',                              // short label / number (from facts.md) — never the caption words
       icons: [['clock', 'spend'], ['chip', 'AI']],  flow: true,   // icons pop on their words, dotted arrows between
       progress: 6,                              // segmented bar that fills over the panel's time
       compare: { a: {icon:'person', n:4, plus:'hour#1'}, b: {icon:'person', n:4, minus:"doesn't"} },  // you vs them
     },
     full: {                                     // a full-screen panel (use layout 'R_OFF'); enter/exit: 'flip'
       chart: [{icon:'book', from:'knowledge', to:'others'}, {icon:'coin', from:'compound#1', to:'money', grow:'slow'}],
       gap: 'money',                             // dashed gap between the first two curve ends
       icons: [['code','AI'], ['clock','hour']], // or a big row of icons
     },
     enter: 'flip', exit: 'flip',
   }
   House rules built in: no caption words in panels (only icons, a pill, bars) · no freeze-frame of the face (no stickerFreeze /
   scanLine here) · positions alternate because you choose the layouts. Sound cues and preview times are collected for reel.py
   (04_render_frames.js writes them to kit_cues.json). */
const KIT = (() => {
  const words = () => CAPS.flatMap(c => c.w.filter(x => !x.gloss));
  const norm = s => String(s).replace(/[.,!?؟،"«»:;…]/g, '').trim().toLowerCase();
  function at(ref, dflt) {
    if (ref == null) return dflt;
    if (typeof ref === 'number') return ref;
    const m = /^(.*?)(?:#(\d+))?(?:([+-]\d*\.?\d+))?$/.exec(String(ref).trim()); const txt = m[1], n = +(m[2] || 0), off = m[3] ? parseFloat(m[3]) : 0;
    if (/^\^\d+$/.test(txt)) { const c = CAPS[+txt.slice(1)]; return (c ? c.s : 0) + off; }
    const L = words().filter(x => norm(x.t) === norm(txt));
    if (!L.length) { console.error('⚠️ KIT: «' + txt + '» is not in caps.json'); return dflt != null ? dflt : 0; }
    return (L[n] || L[L.length - 1]).s + off;
  }

  /* ── icons, drawn around (0,0) inside radius r, theme colours ── */
  const rrc = (c, x, y, w, h, r) => { r = Math.min(r, w / 2, h / 2); c.beginPath(); c.moveTo(x + r, y); c.arcTo(x + w, y, x + w, y + h, r); c.arcTo(x + w, y + h, x, y + h, r); c.arcTo(x, y + h, x, y, r); c.arcTo(x, y, x + w, y, r); c.closePath(); };
  const txt = (c, s, x, y, font, col, al, dir) => { c.save(); c.font = font; c.fillStyle = col; c.textAlign = al || 'center'; c.textBaseline = 'middle'; if (dir) c.direction = dir; c.fillText(s, x, y); c.restore(); };
  let c = X;   /* the canvas the icon helpers draw on — X, or the flip's offscreen frame */
  const L = (w) => { c.lineWidth = w; c.lineCap = 'round'; c.lineJoin = 'round'; };
  const ICON = {
    clock(r, t) { c.strokeStyle = INK; L(r * 0.08); c.beginPath(); c.arc(0, 0, r * 0.6, 0, 7); c.stroke();
      for (let i = 0; i < 4; i++) { const a = i * Math.PI / 2; c.beginPath(); c.moveTo(Math.sin(a) * r * 0.46, -Math.cos(a) * r * 0.46); c.lineTo(Math.sin(a) * r * 0.54, -Math.cos(a) * r * 0.54); c.stroke(); }
      const h = -Math.PI / 3, m = (t || 0) * 4; L(r * 0.11); c.beginPath(); c.moveTo(0, 0); c.lineTo(Math.sin(h) * r * 0.26, -Math.cos(h) * r * 0.26); c.stroke();
      c.strokeStyle = ACC; L(r * 0.07); c.beginPath(); c.moveTo(0, 0); c.lineTo(Math.sin(m) * r * 0.42, -Math.cos(m) * r * 0.42); c.stroke(); },
    chip(r) { const s = r * 0.5; c.strokeStyle = INK; L(r * 0.09); rrc(c, -s, -s, 2 * s, 2 * s, r * 0.12); c.stroke(); c.fillStyle = ACC; rrc(c, -s * 0.45, -s * 0.45, s * 0.9, s * 0.9, r * 0.06); c.fill();
      for (const d of [-0.5, 0, 0.5]) for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) { const px = dx ? dx * s : d * s, py = dy ? dy * s : d * s; c.beginPath(); c.moveTo(px, py); c.lineTo(px + dx * r * 0.18, py + dy * r * 0.18); c.stroke(); } },
    person(r, t, col) { c.fillStyle = col || INK; c.beginPath(); c.arc(0, -r * 0.24, r * 0.24, 0, 7); c.fill(); c.beginPath(); c.ellipse(0, r * 0.42, r * 0.44, r * 0.34, 0, Math.PI, 0); c.fill(); },
    people(r) { c.save(); c.globalAlpha *= 0.6; c.translate(-r * 0.3, 0); ICON.person(r * 0.8); c.restore(); c.save(); c.translate(r * 0.22, r * 0.05); ICON.person(r * 0.9); c.restore(); },
    book(r) { c.strokeStyle = INK; L(r * 0.09); const w = r * 0.5, h = r * 0.34; c.beginPath(); c.moveTo(0, -h * 0.8); c.quadraticCurveTo(-w * 0.5, -h * 1.2, -w, -h); c.lineTo(-w, h);
      c.quadraticCurveTo(-w * 0.5, h * 0.7, 0, h * 1.1); c.quadraticCurveTo(w * 0.5, h * 0.7, w, h); c.lineTo(w, -h); c.quadraticCurveTo(w * 0.5, -h * 1.2, 0, -h * 0.8); c.lineTo(0, h * 1.1); c.stroke(); },
    coin(r) { c.strokeStyle = INK; L(r * 0.08); c.beginPath(); c.arc(0, 0, r * 0.55, 0, 7); c.stroke(); txt(c, '$', 0, r * 0.03, '900 ' + Math.round(r * 0.7) + 'px ' + FONT, INK, 'center', 'ltr'); },
    code(r) { c.strokeStyle = INK; L(r * 0.12); c.beginPath(); c.moveTo(-r * 0.2, -r * 0.32); c.lineTo(-r * 0.48, 0); c.lineTo(-r * 0.2, r * 0.32); c.stroke();
      c.beginPath(); c.moveTo(r * 0.2, -r * 0.32); c.lineTo(r * 0.48, 0); c.lineTo(r * 0.2, r * 0.32); c.stroke(); c.strokeStyle = ACC; c.beginPath(); c.moveTo(r * 0.08, -r * 0.4); c.lineTo(-r * 0.08, r * 0.4); c.stroke(); },
    chat(r) { c.fillStyle = INK; rrc(c, -r * 0.5, -r * 0.38, r, r * 0.66, r * 0.16); c.fill(); c.beginPath(); c.moveTo(-r * 0.2, r * 0.26); c.lineTo(-r * 0.36, r * 0.5); c.lineTo(r * 0.02, r * 0.27); c.fill();
      c.fillStyle = BG; [-0.22, 0, 0.22].forEach(d => { c.beginPath(); c.arc(d * r, -r * 0.05, r * 0.07, 0, 7); c.fill(); }); },
    gear(r) { c.strokeStyle = INK; L(r * 0.1); c.save(); for (let i = 0; i < 8; i++) { c.rotate(Math.PI / 4); c.beginPath(); c.moveTo(0, -r * 0.34); c.lineTo(0, -r * 0.5); c.stroke(); } c.restore();
      c.beginPath(); c.arc(0, 0, r * 0.3, 0, 7); c.stroke(); c.strokeStyle = ACC; c.beginPath(); c.arc(0, 0, r * 0.1, 0, 7); c.stroke(); },
    stack(r) { c.strokeStyle = INK; L(r * 0.07); for (let i = 0; i < 3; i++) { const y = r * 0.3 - i * r * 0.22; c.strokeStyle = i === 2 ? ACC : INK;
      c.beginPath(); c.moveTo(-r * 0.5, y); c.lineTo(0, y - r * 0.16); c.lineTo(r * 0.5, y); c.lineTo(0, y + r * 0.16); c.closePath(); c.stroke(); } },
    app(r) { c.strokeStyle = INK; L(r * 0.07); rrc(c, -r * 0.5, -r * 0.38, r, r * 0.76, r * 0.1); c.stroke(); c.beginPath(); c.moveTo(-r * 0.5, -r * 0.18); c.lineTo(r * 0.5, -r * 0.18); c.stroke();
      c.fillStyle = ACC; [0, 1, 2].forEach(i => { c.beginPath(); c.arc(-r * 0.36 + i * r * 0.1, -r * 0.28, r * 0.03, 0, 7); c.fill(); }); },
    check(r) { c.strokeStyle = ACC; L(r * 0.14); c.beginPath(); c.moveTo(-r * 0.32, 0); c.lineTo(-r * 0.08, r * 0.24); c.lineTo(r * 0.36, -r * 0.24); c.stroke(); },
    cross(r) { c.strokeStyle = INK; L(r * 0.13); c.beginPath(); c.moveTo(-r * 0.28, -r * 0.28); c.lineTo(r * 0.28, r * 0.28); c.moveTo(r * 0.28, -r * 0.28); c.lineTo(-r * 0.28, r * 0.28); c.stroke(); },
    bolt(r) { c.fillStyle = ACC; c.beginPath(); c.moveTo(r * 0.08, -r * 0.5); c.lineTo(-r * 0.3, r * 0.06); c.lineTo(-r * 0.02, r * 0.06); c.lineTo(-r * 0.1, r * 0.5); c.lineTo(r * 0.3, -r * 0.08); c.lineTo(r * 0.02, -r * 0.08); c.closePath(); c.fill(); },
    up(r) { c.strokeStyle = ACC; L(r * 0.12); c.beginPath(); c.moveTo(-r * 0.45, r * 0.3); c.lineTo(-r * 0.1, -r * 0.02); c.lineTo(r * 0.08, r * 0.14); c.lineTo(r * 0.42, -r * 0.22); c.stroke();
      c.beginPath(); c.moveTo(r * 0.18, -r * 0.24); c.lineTo(r * 0.44, -r * 0.24); c.lineTo(r * 0.44, r * 0.02); c.stroke(); },
    down(r) { c.save(); c.scale(1, -1); c.strokeStyle = INK; ICON.up(r); c.restore(); },
    heart(r) { c.fillStyle = ACC; c.beginPath(); c.moveTo(0, r * 0.4); c.bezierCurveTo(-r * 0.7, -r * 0.05, -r * 0.35, -r * 0.6, 0, -r * 0.22); c.bezierCurveTo(r * 0.35, -r * 0.6, r * 0.7, -r * 0.05, 0, r * 0.4); c.fill(); },
    star(r) { c.fillStyle = ACC; c.beginPath(); for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, q = i % 2 ? r * 0.22 : r * 0.52; c.lineTo(Math.cos(a) * q, Math.sin(a) * q); } c.closePath(); c.fill(); },
    play(r) { c.fillStyle = ACC; c.beginPath(); c.moveTo(-r * 0.2, -r * 0.32); c.lineTo(r * 0.36, 0); c.lineTo(-r * 0.2, r * 0.32); c.closePath(); c.fill(); },
    mic(r) { c.strokeStyle = INK; L(r * 0.09); rrc(c, -r * 0.16, -r * 0.46, r * 0.32, r * 0.56, r * 0.16); c.stroke(); c.beginPath(); c.arc(0, 0, r * 0.3, 0.15, Math.PI - 0.15); c.stroke();
      c.beginPath(); c.moveTo(0, r * 0.3); c.lineTo(0, r * 0.46); c.stroke(); },
    camera(r) { c.strokeStyle = INK; L(r * 0.08); rrc(c, -r * 0.5, -r * 0.28, r * 0.72, r * 0.56, r * 0.1); c.stroke(); c.fillStyle = ACC; c.beginPath(); c.moveTo(r * 0.26, -r * 0.08); c.lineTo(r * 0.5, -r * 0.24); c.lineTo(r * 0.5, r * 0.24); c.lineTo(r * 0.26, r * 0.08); c.fill(); },
    bulb(r) { c.strokeStyle = INK; L(r * 0.08); c.beginPath(); c.arc(0, -r * 0.1, r * 0.32, Math.PI * 0.8, Math.PI * 2.2); c.lineTo(r * 0.12, r * 0.3); c.lineTo(-r * 0.12, r * 0.3); c.closePath(); c.stroke();
      c.beginPath(); c.moveTo(-r * 0.12, r * 0.42); c.lineTo(r * 0.12, r * 0.42); c.stroke(); c.fillStyle = ACC; c.beginPath(); c.arc(0, -r * 0.1, r * 0.12, 0, 7); c.fill(); },
    lock(r) { c.strokeStyle = INK; L(r * 0.09); rrc(c, -r * 0.34, -r * 0.06, r * 0.68, r * 0.5, r * 0.08); c.stroke(); c.beginPath(); c.arc(0, -r * 0.06, r * 0.22, Math.PI, 0); c.stroke(); c.fillStyle = ACC; c.beginPath(); c.arc(0, r * 0.18, r * 0.07, 0, 7); c.fill(); },
    globe(r) { c.strokeStyle = INK; L(r * 0.07); c.beginPath(); c.arc(0, 0, r * 0.5, 0, 7); c.stroke(); c.beginPath(); c.ellipse(0, 0, r * 0.22, r * 0.5, 0, 0, 7); c.stroke();
      c.beginPath(); c.moveTo(-r * 0.5, 0); c.lineTo(r * 0.5, 0); c.stroke(); },
    money(r) { c.strokeStyle = INK; L(r * 0.07); rrc(c, -r * 0.52, -r * 0.3, r * 1.04, r * 0.6, r * 0.08); c.stroke(); c.strokeStyle = ACC; c.beginPath(); c.arc(0, 0, r * 0.15, 0, 7); c.stroke(); },
  };
  ICON.ai = ICON.chip; ICON.time = ICON.clock; ICON.idea = ICON.bulb; ICON.user = ICON.person; ICON.team = ICON.people;
  const icon = (name, r, t, col, on) => { const f = ICON[name] || ICON.star; if (!ICON[name]) console.error('⚠️ KIT: no icon «' + name + '» — have: ' + Object.keys(ICON).join(' '));
    const c0 = c; if (on) c = on; c.save(); try { f(r, t, col); } finally { c.restore(); c = c0; } };

  function node(cx, cy, r, k, name, t, on) { const c0 = c; if (on) c = on; try {
    if (k <= 0) return; c.save(); c.globalAlpha *= ease(k); c.translate(cx, cy); const s = lerp(0.92, 1, ease(k)); c.scale(s, s);
    c.fillStyle = cBG(0.6); c.beginPath(); c.arc(0, 0, r, 0, 7); c.fill(); c.strokeStyle = ACC; c.lineWidth = 4; c.beginPath(); c.arc(0, 0, r, 0, 7); c.stroke();
    icon(name, r, t); c.restore(); } finally { c = c0; }
  }
  function dots(x0, x1, y, k) {
    if (k <= 0) return; const x = lerp(x0, x1, ease(k)); c.save(); c.strokeStyle = cINK(0.55); c.lineWidth = 5; c.lineCap = 'round';
    c.setLineDash([2, 14]); c.beginPath(); c.moveTo(x0, y); c.lineTo(x, y); c.stroke(); c.setLineDash([]);
    if (k > 0.95) { c.fillStyle = cINK(0.55); c.beginPath(); c.moveTo(x1 + 4, y); c.lineTo(x1 - 14, y - 11); c.lineTo(x1 - 14, y + 11); c.fill(); } c.restore();
  }
  function block(x, y, s, k, fill, dashed) {
    if (k <= 0) return; c.save(); c.globalAlpha *= cl(k * 2, 0, 1); const z = lerp(0.92, 1, ease(k)), h2 = s / 2; c.translate(x + h2, y + h2); c.scale(z, z);
    if (dashed) { c.strokeStyle = cINK(0.5); c.lineWidth = 3; c.setLineDash([8, 8]); rrc(c, -h2, -h2, s, s, 12); c.stroke(); c.setLineDash([]); }
    else { c.fillStyle = fill; rrc(c, -h2, -h2, s, s, 12); c.fill(); } c.restore();
  }

  /* ── a panel inside panelIn's box (x 130..950 · y 278..458, centre y 368) ── */
  function panel(P, t, p0, p1) {
    if (P.glass) glass(150, 282, 780, 172, 34, 0.56);
    let x0 = 190;
    if (P.pill) { X.font = '800 28px ' + FONT; const w = Math.max(118, X.measureText(P.pill).width + 44); X.fillStyle = ACC; rr(190, 300, w, 46, 23); X.fill();
      T(P.pill, 190 + w / 2, 324, '800 28px ' + FONT, typeof ONACC === 'string' && ONACC ? ONACC : BG, 'center', 'ltr'); x0 = 190 + w + 60; }
    const hasBar = !!P.progress, cy = hasBar ? 352 : 368;
    if (P.icons && P.icons.length) {
      const n = P.icons.length, r = n > 4 ? 36 : 44, span = 890 - x0, step = n > 1 ? Math.min(220, (span - 2 * r) / (n - 1)) : 0, xs = x0 + r + (span - 2 * r - step * (n - 1)) / 2;
      P.icons.forEach(([name, ref], i) => { const ta = at(ref, p0), x = xs + i * step;
        if (i && P.flow !== false) dots(x - step + r + 12, x - r - 12, cy, pr(t, ta - 0.35, ta));
        node(x, cy, r, pr(t, ta - 0.05, ta + 0.3), name, t); });
    }
    if (hasBar) { const n = P.progress === true ? 6 : P.progress, sw = (700 - (n - 1) * 12) / n, f = n * ease(pr(t, p0 + 0.3, p1 - 0.2));
      for (let q = 0; q < n; q++) { const x = 190 + q * (sw + 12); X.fillStyle = cINK(0.2); rr(x, 420, sw, 12, 6); X.fill();
        const k = cl(f - q, 0, 1); if (k > 0) { X.fillStyle = ACC; rr(x, 420, sw * k, 12, 6); X.fill(); } } }
    if (P.compare) {
      const S = 44, g = 10, y0 = 368 - S / 2, side = (c, px, xb, colP, colB, d) => {
        X.save(); X.translate(px, 368); X.globalAlpha *= ease(pr(t, p0 + d, p0 + d + 0.3)); icon(c.icon || 'person', 92, t, colP); X.restore();
        const n = c.n ?? 4;   /* n: 0 = no grey blocks */ for (let i = 0; i < n; i++) block(xb + i * (S + g), y0, S, pr(t, p0 + d + 0.1 + i * 0.06, p0 + d + 0.35 + i * 0.06), colB);
        const gx = xb + n * (S + g);
        if (c.plus) block(gx, y0, S, pr(t, at(c.plus), at(c.plus) + 0.3), ACC);
        if (c.minus) { const k = pr(t, at(c.minus), at(c.minus) + 0.3); block(gx + 3, y0 + 3, S - 6, k, null, true);
          if (k > 0.6) { X.save(); X.globalAlpha *= cl((k - 0.6) * 2.5, 0, 1); X.strokeStyle = ACC; X.lineWidth = 5; X.lineCap = 'round'; X.beginPath(); X.moveTo(gx + 10, y0 + 10); X.lineTo(gx + S - 10, y0 + S - 10); X.stroke(); X.restore(); } } };
      side(P.compare.a || {}, 172, 222, ACC, cINK(0.85), 0.1);
      T(P.compare.label || 'vs', 540, 370, '800 30px ' + FONT, cINK(0.45), 'center', 'ltr');
      side(P.compare.b || {}, 602, 652, cINK(0.45), cINK(0.3), 0.2);
    }
  }

  /* ── a full-screen panel (theme background), drawn on Y ── */
  function full(F, Y, t, s0) {
    MV.panel(Y, () => {
      const kin = pr(t, s0, s0 + 0.5);
      if (F.chart) {
        const x0 = 150, x1 = 930, yb = 1130, yt = 400, H = yb - yt;
        Y.save(); Y.globalAlpha *= ease(kin); Y.strokeStyle = cINK(0.1); Y.lineWidth = 2;
        for (let i = 1; i <= 4; i++) { const y = yb - H * i / 4; Y.setLineDash([6, 14]); Y.beginPath(); Y.moveTo(x0, y); Y.lineTo(x1, y); Y.stroke(); }
        Y.setLineDash([]); Y.strokeStyle = cINK(0.45); Y.lineWidth = 4; Y.lineCap = 'round'; Y.beginPath(); Y.moveTo(x0, yt - 20); Y.lineTo(x0, yb); Y.lineTo(x1 + 20, yb); Y.stroke();
        Y.fillStyle = cINK(0.45); Y.beginPath(); Y.moveTo(x1 + 34, yb); Y.lineTo(x1 + 14, yb - 12); Y.lineTo(x1 + 14, yb + 12); Y.fill();
        Y.beginPath(); Y.moveTo(x0, yt - 34); Y.lineTo(x0 - 12, yt - 14); Y.lineTo(x0 + 12, yt - 14); Y.fill(); Y.restore();
        const G = { exp: u => (Math.exp(3.2 * u) - 1) / (Math.exp(3.2) - 1) * 0.92, slow: u => 0.22 * (Math.exp(1.1 * u) - 1) / (Math.exp(1.1) - 1), linear: u => 0.5 * u, down: u => 0.7 - 0.5 * u };
        const ends = [];
        F.chart.forEach((cv, i) => {
          const f = G[cv.grow || (i ? 'slow' : 'exp')] || G.exp, k = ease(pr(t, at(cv.from, s0), at(cv.to, s0 + 1.5))), col = cv.color || (i ? cINK(0.7) : ACC);
          if (k <= 0) { ends.push(null); return; } const N = 60, pts = [];
          for (let j = 0; j <= N * k; j++) { const u = j / N; pts.push([x0 + (x1 - x0) * u, yb - H * f(u)]); }
          const e = [x0 + (x1 - x0) * k, yb - H * f(k)]; pts.push(e); ends.push(e);
          if (!i) { Y.save(); Y.fillStyle = col; Y.globalAlpha *= 0.12; Y.beginPath(); Y.moveTo(x0, yb); pts.forEach(p => Y.lineTo(p[0], p[1])); Y.lineTo(e[0], yb); Y.closePath(); Y.fill(); Y.restore(); }
          Y.save(); Y.strokeStyle = col; Y.lineWidth = i ? 7 : 11; Y.lineCap = 'round'; Y.lineJoin = 'round'; Y.beginPath(); pts.forEach((p, j) => j ? Y.lineTo(p[0], p[1]) : Y.moveTo(p[0], p[1])); Y.stroke(); Y.restore();
          if (cv.icon) { Y.save(); Y.translate(e[0], e[1]); Y.fillStyle = i ? cINK(0.85) : ACC; Y.beginPath(); Y.arc(0, 0, 40, 0, 7); Y.fill();
            const ink = INK; INK = BG; try { icon(cv.icon, 46, t, null, Y); } finally { INK = ink; } Y.restore(); }
        });
        if (F.gap && ends[0] && ends[1]) { const kG = pr(t, at(F.gap), at(F.gap) + 0.4);
          if (kG > 0) { Y.save(); Y.globalAlpha *= ease(kG); Y.strokeStyle = ACC; Y.lineWidth = 4; Y.setLineDash([4, 12]); Y.lineCap = 'round'; const gx = x1 + 6;
            Y.beginPath(); Y.moveTo(gx, ends[0][1] + 48); Y.lineTo(gx, lerp(ends[0][1] + 48, ends[1][1] - 44, ease(kG))); Y.stroke(); Y.restore(); } }
      }
      if (F.icons) { const n = F.icons.length, r = 92, step = Math.min(300, 760 / Math.max(1, n - 1)), xs = 540 - step * (n - 1) / 2;
        F.icons.forEach(([name, ref], i) => node(xs + i * step, 760, r, pr(t, at(ref, s0) - 0.05, at(ref, s0) + 0.3), name, t, Y)); }
    });
  }

  const cues = { thud: [], whoosh_up: [], whoosh_down: [], pop: [], tap: [], soft: [], riser: [] }, preview = [];
  const used = new Set(), icons = new Set(), BUILTIN = new Set(SCENE_LIST.map(x => x[0]));   /* engine scenes present before scenes.js */   /* what this video uses — reel.py compares it with the last videos (rule 15) */
  const SPLIT = m => m === R_UP || m === R_DOWN || m === R_LOWER || (m && m.up);
  function reel(list) {
    MV.ready(() => {
      SCENES = []; let cur = 0, prev = null;
      list.forEach((sc, i) => {
        const s = cur;   /* per scene — the drawers below keep their own start */
        const e = i === list.length - 1 ? 99 : at(sc.to, s + 2), m = typeof sc.layout === 'string' ? rectByName(sc.layout) : (sc.layout || R_FULL);
        SCENES.push(sc.nocap ? { s, e, m, nocap: true } : { s, e, m });
        const end = Math.min(e, VEND || e), ovl = m === R_OVT || m === R_OVB || m === R_FULL;
        if (i && prev !== m && (SPLIT(m) || SPLIT(prev)) && !sc.full) cues.whoosh_down.push(+s.toFixed(2));
        if (sc.snap != null) used.add('snap');
        if (sc.snap != null) { const o = typeof sc.snap === 'object' ? sc.snap : { at: sc.snap }, a = at(o.at) - 0.05, b = at(o.back, a + 0.6);
          const f = t => { if (t < a || t > b + 0.5) return; FX.snapZoom(MV, t, { s: a, to: o.to || 1.16, focus: [540, 800], back: b, draw: Y => MV.video(Y) }); };
          f.layer = 'video'; SCENE_LIST.push(['kitSnap' + i, f, 'video']); cues.thud.push(+(a + 0.01).toFixed(2)); preview.push(+(a + 0.14).toFixed(2)); }
        if (sc.panel) { const P = { glass: ovl, ...sc.panel }, p0 = at(P.from, s), p1 = Math.min(at(P.to, e), e);
          for (const k of ['icons', 'progress', 'compare', 'pill']) if (P[k]) used.add(k === 'icons' ? 'icon flow' : k === 'compare' ? 'compare board' : k);
          if (P.glass) used.add('glass band');
          (P.icons || []).forEach(x => icons.add(x[0])); if (P.compare) [P.compare.a, P.compare.b].forEach(c => c && icons.add(c.icon || 'person'));
          SCENE_LIST.push(['kitPanel' + i, t => { if (t < p0 || t > p1) return; panelIn(t, p0, p1, () => panel(P, t, p0, p1)); }]);
          cues.soft.push([+(p0 + TR - 0.08).toFixed(2), 0.04]);
          if (P.compare) { for (const c of [P.compare.a, P.compare.b]) { if (c && c.plus) cues.pop.push(+at(c.plus).toFixed(2)); if (c && c.minus) cues.tap.push(+at(c.minus).toFixed(2)); } }
          else if (P.icons && P.icons.length) cues.pop.push(+at(P.icons[P.icons.length - 1][1], p0).toFixed(2));
          const late = Math.max(...(P.icons || []).map(x => at(x[1], p0)), ...([P.compare && P.compare.a && P.compare.a.plus, P.compare && P.compare.b && P.compare.b.minus].filter(Boolean).map(at)), p0 + 0.6);
          preview.push(+Math.min(p1 - 0.15, late + 0.4).toFixed(2)); }
        if (sc.full) { const F = sc.full, inF = sc.enter === 'flip', outF = sc.exit === 'flip';
          if (F.chart) { used.add('growth chart'); F.chart.forEach(c => c.icon && icons.add(c.icon)); }
          if (F.icons) { used.add('big icons'); F.icons.forEach(x => icons.add(x[0])); } if (inF || outF) used.add('flip');
          SCENE_LIST.push(['kitFull' + i, t => { if (t < s || t > e + (outF ? 0.62 : 0)) return;
            if (inF && t < s + 0.7) FX.flip(MV, t, { s, dur: 0.7, A: Y => MV.video(Y), B: Y => full(F, Y, t, s) });
            else if (t < e) full(F, X, t, s);
            else if (outF) FX.flip(MV, t, { s: e, dur: 0.6, A: Y => full(F, Y, t, s), B: Y => MV.video(Y) });
            bar(t); }]);
          if (inF) cues.whoosh_up.push(+s.toFixed(2)); if (outF && e < 90) cues.whoosh_down.push(+e.toFixed(2));
          if (F.chart && F.chart[0]) { const top = at(F.chart[0].to, s + 1.5); cues.riser.push([+top.toFixed(2), 1.1]); }
          if (F.gap) cues.tap.push(+at(F.gap).toFixed(2));
          const lastT = Math.max(...(F.chart || []).map(c => at(c.to, s + 1.5)), ...(F.icons || []).map(x => at(x[1], s)), s + 0.9);
          preview.push(+Math.min(end - 0.1, lastT + 0.1).toFixed(2)); }
        if (!sc.snap && !sc.panel && !sc.full) preview.push(+((s + end) / 2).toFixed(2));
        prev = m; cur = e;
      });
    });
  }
  function exportCues() {
    const out = {}; for (const k in cues) if (cues[k].length) out[k] = cues[k];
    let p = [...new Set(preview)].filter(t => t > 0 && t < (VEND || 1e9)).sort((a, b) => a - b);
    while (p.length > 6) { let bi = 1, bd = 1e9; for (let i = 1; i < p.length; i++) if (p[i] - p[i - 1] < bd) { bd = p[i] - p[i - 1]; bi = i; } p.splice(bi, 1); }
    const custom = SCENE_LIST.map(x => x[0]).filter(n => !/^kit/.test(n) && !BUILTIN.has(n) && n !== 'hookZoom').map(n => 'custom:' + n);   // your own MV.scene drawings
    return { sfx: out, preview: p, blocks: [...used, ...custom], icons: [...icons] };
  }
  /* KIT.cue('whoosh_up', 'tool') — a sound for a moment you drew yourself (call it inside MV.ready) */
  function cue(kind, ref, g) { const t = +at(ref).toFixed(2); (cues[kind] = cues[kind] || []).push(kind === 'soft' ? [t, g || 0.04] : kind === 'riser' ? [t, g || 1.1] : t); }
  return { reel, at, cue, ICON, export: exportCues };
})();
window.KIT = KIT;

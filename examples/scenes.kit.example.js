/* ⚠️ SYNTAX example, not a design to copy (house-style rule 15): plan every visual from YOUR script's sentences first
   (<work>/scene-plan.md), then pick the tool. Reusing this compare board / chart / flip on another video is exactly what not to do.
   A whole reel's scenes with the scene kit (wailzenz-video-dz) — the English test reel, 10 s:
   «Every hour you spend learning AI becomes an hour someone else doesn't have.
    The future belongs to people who compound knowledge faster than others compound money.»
   Times are spoken words ('hour#1' = the 2nd «hour», '^1' = sentence 1 starts, '+0.2' / '-0.1' offsets).
   Layouts change every scene; panels show icons, a pill and bars — never the caption words; his face is never frozen. */
KIT.reel([
  { layout: 'R_OVT', to: 'becomes-0.05', snap: { at: 'hour', back: 'you+0.42' },                  // hook: snap zoom · top glass band
    panel: { from: 'spend-0.1', pill: '+1h', icons: [['clock', 'spend'], ['chip', 'AI']], progress: 6 } },
  { layout: 'R_UP', to: '^1-0.05',                                                                 // face on top · you vs them below
    panel: { compare: { a: { icon: 'person', n: 4, plus: 'hour#1' }, b: { icon: 'person', n: 4, minus: "doesn't" } } } },
  { layout: 'R_DOWN', to: 'compound-0.15',                                                         // panel on top · face below
    panel: { icons: [['bulb', 'future'], ['people', 'people'], ['up', 'who']] } },
  { layout: 'R_OFF', to: 'money+0.4', enter: 'flip', exit: 'flip',                                 // full chart, his voice goes on
    full: { chart: [{ icon: 'book', from: 'knowledge-0.2', to: 'others-0.05' },
                    { icon: 'coin', from: 'compound#1-0.1', to: 'money+0.3', grow: 'slow' }], gap: 'money+0.05' } },
  { layout: 'R_FULL' },                                                                            // his face for the last beat
]);

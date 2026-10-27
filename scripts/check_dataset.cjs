const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync('index.html', 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
new vm.Script(script);
const nodes = new Map();
function node(id) {
  if (!nodes.has(id)) nodes.set(id, {innerHTML:'', className:'', style:{}, value:'',
    scrollTop:0, classList:{add(){},remove(){},toggle(){},contains(){return false}},
    addEventListener(){}, querySelectorAll(){return []}, focus(){}});
  return nodes.get(id);
}
const ctx = vm.createContext({document:{getElementById:node,body:{style:{}},
  querySelectorAll(){return []},addEventListener(){}},setTimeout(){}});
vm.runInContext(script, ctx);
const d = ctx.DATA;
assert.equal(d.defense.length, 49);
assert.equal(Object.keys(d.counters).length, 89);
assert.equal(d.research.defenseVariants, 67);
assert.equal(d.research.offenseVariants, 127);
assert.equal(d.research.matchups, 136);
assert.equal(d.research.teamMatchups, 131);
assert.equal(Object.keys(ctx.PROPOSED_DEFENSE).length, 0);

// The sole user-facing outgoing link is the community fanpage. This includes
// dynamic detail views below, not just anchors in the initial HTML.
const anchors = [...html.matchAll(/<a\s[^>]*href="([^"]+)"/g)].map(m=>m[1]);
assert.deepEqual(anchors, ['https://www.facebook.com/7krbvn']);
for (const panels of [ctx.HERO_PANELS, ctx.PET_PANELS]) {
  assert.ok(Object.values(panels).every(p=>!('source' in p)));
}
assert.ok(!JSON.stringify(d).match(/https?:\/\/(?:7k-note\.pages\.dev|7katlas\.com|gamewith\.(?:jp|net))/));

const all = [...d.defense, ...Object.values(d.counters)];
const trio = t=>JSON.stringify(t.heroes.map(h=>h.name).sort());
for (const groups of [d.defense, Object.values(d.counters)]) {
  assert.equal(new Set(groups.map(trio)).size, groups.length, 'each trio appears once per library');
}
for (const t of all) {
  assert.equal(new Set(t.heroes.map(h=>h.name)).size, 3, t.code);
  assert.ok(t.variants.length, t.code);
  for (const v of t.variants) {
    assert.equal(trio(v), trio(t), v.code);
    const names = v.heroes.map(h=>h.name);
    assert.deepEqual([...v.front,...v.back].sort(), [...names].sort(), v.code);
    const cap = ctx.TEMPLATES[ctx.fmtShort(v)];
    assert.ok(v.front.length<=cap[0] && v.back.length<=cap[1], v.code);
    for (const p of [v.pet,...v.petBackup]) assert.ok(ctx.PETS[p],p);
    for (const s of v.skills) {
      assert.ok(names.includes(s.hero),v.code);
      assert.ok(['Skill 1','Skill 2','Awakening'].includes(s.slot),v.code);
      assert.ok(ctx.panelSec(s.hero,s.slot),`${v.code}: missing ${s.hero} ${s.slot}`);
    }
  }
}
const multiCategory = d.defense.find(t=>t.code==='T41');
assert.ok(multiCategory.groups.includes('tank') && multiCategory.groups.includes('status'));
ctx.state.tab='status';
ctx.state.q='Radgrid';
ctx.render();
assert.ok(node('list').innerHTML.includes('data-team="T41"'));
ctx.state.tab='all';
ctx.state.q='';

let edges = 0;
for (const team of d.defense) {
  assert.equal(new Set(team.counters).size,team.counters.length);
  assert.deepEqual(Object.keys(team.matchups).sort(),[...team.counters].sort());
  for (const c of team.counters) {
    const attack = d.counters[c];
    assert.ok(attack, c);
    assert.ok(team.matchups[c].length);
    for (const m of team.matchups[c]) {
      assert.ok(team.variants.some(v=>v.code===m.defenseVariant));
      assert.ok(attack.variants.some(v=>v.code===m.attackVariant));
      edges++;
    }
  }
  ctx.openTeam(team.code);
  const rendered = node('sheet').innerHTML;
  assert.equal((rendered.match(/class="counter-block ally"/g)||[]).length,team.counters.length);
  assert.ok(!rendered.includes('undefined') && !/<a\s/i.test(rendered),team.code);
}
assert.equal(edges, 136);
for (const c of Object.keys(d.counters)) {
  ctx.openCounter(c);
  const rendered = node('sheet').innerHTML;
  assert.equal((rendered.match(/class="def-block"/g)||[]).length,(ctx.beatsMap[c]||[]).length);
  assert.ok(!rendered.includes('undefined') && !/<a\s/i.test(rendered),c);
}

// These two original formations have different counters; merging must retain
// all three counters and attribute each to the correct original formation.
const combined = d.defense.find(t=>t.code==='P44');
assert.deepEqual(Array.from(combined.variants,v=>v.code), ['P44','P38']);
assert.equal(combined.counters.length,3);
assert.equal(combined.matchups.C95[0].defenseVariant,'P44');
assert.ok(combined.matchups.C95[0].notes[0].includes('Rudy > Platin > Clemyth'));
assert.ok(Object.values(combined.matchups).flat().some(m=>m.defenseVariant==='P38'));
ctx.openTeam('P38');
assert.ok(node('sheet').innerHTML.includes('Bố trí thủ 2'));
assert.ok(node('sheet').innerHTML.includes('Áp dụng cho thủ 1'));
assert.ok(node('sheet').innerHTML.includes('Áp dụng cho thủ 2'));
const emptyQueue = d.defense.find(t=>t.code==='M32').variants.find(v=>v.code==='M32');
assert.equal(emptyQueue.front.length,0);
assert.equal(emptyQueue.skills.length,0,'Do not invent an unset queue');

// Older variant codes and alternative pets still find their consolidated team.
ctx.state.q='P38';
assert.ok(ctx.matches(combined,false));
ctx.state.q='Yu';
assert.ok(ctx.matches(d.defense.find(t=>t.code==='M32'),false));
ctx.state.q='';
const alternateCounter = Object.values(d.counters).find(t=>t.variants.length>1).variants[1].code;
ctx.openCounter(alternateCounter);
assert.ok(node('sheet').innerHTML.includes('Các cách bố trí tấn công'));

assert.notEqual(all.find(t=>t.heroes.some(h=>h.name==='Radgrid')).heroes.find(h=>h.name==='Radgrid').img,
  all.find(t=>t.heroes.some(h=>h.name==='Randgrid')).heroes.find(h=>h.name==='Randgrid').img);
ctx.openHeroPanel('Eileene');
let panel=node('psheet').innerHTML;
assert.ok(panel.indexOf('ss-slot">Awakening')<panel.indexOf('ss-slot">Skill 2'));
assert.ok(panel.indexOf('ss-slot">Skill 2')<panel.indexOf('ss-slot">Skill 1'));
assert.ok(!/<a\s/i.test(panel));
ctx.openSkillPanel('Eileene','Skill 1');
assert.ok(!/<a\s/i.test(node('psheet').innerHTML));
assert.ok(ctx.openerHTML([{hero:'Eileene',slot:'Skill 1'}]).includes('op-slot">Skill 1'));
assert.ok(ctx.heroImgByName('Rook') && ctx.heroImgByName('Lina'));
ctx.openPetPanel('Nezuko Kamado');
assert.ok(node('psheet').innerHTML.includes('Demon Slayer'));
assert.ok(node('psheet').innerHTML.includes('chưa đối chiếu'));
assert.ok(!/<a\s/i.test(node('psheet').innerHTML));
console.log(`PASS: ${d.defense.length} defense trios, ${Object.keys(d.counters).length} offense trios, ${edges} configuration-specific matchups; all details and skill slots render.`);

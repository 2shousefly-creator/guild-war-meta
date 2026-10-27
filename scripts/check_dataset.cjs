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
assert.equal(d.defense.length,67);
assert.equal(Object.keys(d.counters).length,127);
assert.equal(d.research.noteMatchups,104);
assert.equal(d.research.matchups,136);
assert.equal(ctx.PROPOSED_DEFENSE && Object.keys(ctx.PROPOSED_DEFENSE).length,0);
const all = [...d.defense,...Object.values(d.counters)];
for (const t of all) {
  const names = t.heroes.map(h=>h.name);
  assert.equal(new Set(names).size,3,t.code);
  assert.deepEqual([...t.front,...t.back].sort(),[...names].sort(),t.code);
  const cap=ctx.TEMPLATES[ctx.fmtShort(t)];
  assert.ok(t.front.length<=cap[0] && t.back.length<=cap[1],t.code);
  assert.ok(ctx.PETS[t.pet],t.pet);
  for (const p of t.petBackup) assert.ok(ctx.PETS[p],p);
  for (const s of t.skills) {
    assert.ok(names.includes(s.hero),t.code);
    assert.ok(['Skill 1','Skill 2','Awakening'].includes(s.slot),t.code);
    assert.ok(ctx.panelSec(s.hero,s.slot),`${t.code}: missing ${s.hero} ${s.slot}`);
  }
  assert.ok(t.sources.length,t.code);
  for(const s of t.sources) assert.match(s.url,/^https:\/\/(7k-note\.pages\.dev|7katlas\.com)\//);
}
for(const team of d.defense) {
  assert.equal(new Set(team.counters).size,team.counters.length);
  for(const c of team.counters) {
    assert.ok(d.counters[c],c);
    assert.ok(team.matchups[c].sources.length);
  }
  ctx.openTeam(team.code);
  assert.ok(node('sheet').innerHTML.includes('Nguồn cấu hình'));
  assert.ok(!node('sheet').innerHTML.includes('undefined'));
}
for(const c of Object.keys(d.counters)) {
  ctx.openCounter(c);
  assert.ok(node('sheet').innerHTML.includes('Nguồn cấu hình'));
  assert.ok(!node('sheet').innerHTML.includes('undefined'));
}
const noteById = id=>d.defense.find(t=>t.sources.some(s=>s.url.endsWith('/'+id)));
assert.equal(noteById('3LZMb7xvTj').front.length,0);
assert.equal(noteById('3LZMb7xvTj').skills.length,0,'Do not invent an unset queue');
assert.equal(noteById('RvEePzqTuN').back[0],'Sunran');
assert.equal(ctx.heroImg({img:'chara_435.png'}).endsWith('chara_435.png'),true);
assert.notEqual(all.find(t=>t.heroes.some(h=>h.name==='Radgrid')).heroes.find(h=>h.name==='Radgrid').img,
  all.find(t=>t.heroes.some(h=>h.name==='Randgrid')).heroes.find(h=>h.name==='Randgrid').img);
ctx.openHeroPanel('Eileene');
let panel=node('psheet').innerHTML;
assert.ok(panel.indexOf('ss-slot">Awakening')<panel.indexOf('ss-slot">Skill 2'));
assert.ok(panel.indexOf('ss-slot">Skill 2')<panel.indexOf('ss-slot">Skill 1'));
assert.ok(ctx.openerHTML([{hero:'Eileene',slot:'Skill 1'}]).includes('op-slot">Skill 1'));
assert.ok(ctx.PETS['Nezuko Kamado']);
assert.ok(ctx.heroImgByName('Rook'));
assert.ok(ctx.heroImgByName('Lina'));
ctx.openPetPanel('Nezuko Kamado');
assert.ok(node('psheet').innerHTML.includes('Demon Slayer'));
assert.ok(node('psheet').innerHTML.includes('chưa đối chiếu'));
let unknownPet = all.flatMap(t=>[t.pet,...t.petBackup]).filter(p=>!ctx.PETS[p]);
assert.equal(unknownPet.length,0);
console.log(`PASS: ${d.defense.length} defense, ${Object.keys(d.counters).length} offense, ${d.research.matchups} directed matchups; all detail views and skill slots render.`);

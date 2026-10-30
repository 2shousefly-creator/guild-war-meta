const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const html=fs.readFileSync('index.html','utf8'),script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
new vm.Script(script);
const nodes=new Map(),listeners=new Map();
function node(id){
  if(!nodes.has(id)){
    const classes=new Set(),attrs=new Map();
    nodes.set(id,{id,innerHTML:'',textContent:'',style:{},value:'',scrollTop:0,isConnected:true,
      classList:{add(...xs){xs.forEach(x=>classes.add(x));},remove(...xs){xs.forEach(x=>classes.delete(x));},toggle(){},contains(x){return classes.has(x);}},
      setAttribute(k,v){attrs.set(k,String(v));},getAttribute(k){return attrs.get(k)||null;},removeAttribute(k){attrs.delete(k);},
      addEventListener(){},querySelectorAll(){return [];},querySelector(){return null;},getClientRects(){return [{}];},
      closest(){return null;},contains(e){return e===this;},focus(){document.activeElement=this;},select(){}});
  }
  return nodes.get(id);
}
const document={getElementById:node,body:{style:{}},activeElement:null,querySelectorAll(){return [];},
  addEventListener(k,fn){if(!listeners.has(k))listeners.set(k,[]);listeners.get(k).push(fn);}};
const window={location:{href:'https://example.test/'},addEventListener(){}};
window.history={state:null,replaceState(s,_,url){this.state=s;window.location.href=new URL(url,window.location.href).href;},
  pushState(s,_,url){this.replaceState(s,_,url);},go(){},back(){}};
const ctx=vm.createContext({document,window,URL,navigator:{},setTimeout(){}});
vm.runInContext(script,ctx);
const d=ctx.DATA,all=[...d.defense,...Object.values(d.counters)],trio=t=>JSON.stringify(t.heroes.map(h=>h.name).sort());
assert.equal(d.defense.length,51);assert.equal(Object.keys(d.counters).length,93);
assert.equal(d.research.matchups,141,'Configuration-specific source matchups');
assert.deepEqual([...html.matchAll(/<a\s[^>]*href="([^"]+)"/g)].map(m=>m[1]),['https://www.facebook.com/7krbvn']);
for(const library of [d.defense,Object.values(d.counters)])assert.equal(new Set(library.map(trio)).size,library.length);
for(const t of all)for(const v of t.variants){
  assert.equal(new Set(v.heroes.map(h=>h.name)).size,3,v.code);assert.equal(trio(v),trio(t),v.code);
  assert.deepEqual([...v.front,...v.back].sort(),Array.from(v.heroes,h=>h.name).sort(),v.code);
  const cap=ctx.TEMPLATES[ctx.fmtShort(v)];assert.ok(v.front.length<=cap[0]&&v.back.length<=cap[1],v.code);
  for(const p of [v.pet,...v.petBackup])assert.ok(ctx.PETS[p],p);
  for(const s of v.skills){assert.ok(v.heroes.some(h=>h.name===s.hero),v.code);assert.ok(ctx.panelSec(s.hero,s.slot),v.code);}
}
let edges=0;
for(const team of d.defense){
  assert.deepEqual(Object.keys(team.matchups).sort(),[...team.counters].sort());
  for(const c of team.counters)for(const m of team.matchups[c]){
    assert.ok(!m.untested);assert.ok(d.counters[c]);edges++;
    for(const [kind,code,variant,against,againstVariant] of [
      ['attack',c,m.attackVariant,team.code,m.defenseVariant],['defense',team.code,m.defenseVariant,c,m.attackVariant]]){
      const view=ctx.normaliseView({kind,code,variant,against,againstVariant});
      assert.equal(view.variant,variant);assert.equal(view.againstVariant,againstVariant);
      ctx.currentView=view;if(kind==='attack')ctx.renderAttack(view);else ctx.renderDefense(view);
      const sheet=node('sheet').innerHTML;
      assert.ok(sheet.includes(`id="lineup-${variant}" open`),`${code}: exact variant expanded`);
      assert.ok(!sheet.includes('undefined'),code);
      assert.equal((sheet.match(/class="variant match-case"[^>]*\bopen\b/g)||[]).length,0,'Matchups start compact');
    }
  }
  const view=ctx.normaliseView({kind:'defense',code:team.code});ctx.currentView=view;ctx.renderDefense(view);
  assert.equal((node('sheet').innerHTML.match(/class="counter-block ally matchup-card"/g)||[]).length,team.counters.length);
}
assert.equal(edges,139,'Existing runtime excludes the 2 untested source cases');
for(const c of Object.keys(d.counters)){
  const view=ctx.normaliseView({kind:'attack',code:c});ctx.currentView=view;ctx.renderAttack(view);
  assert.equal((node('sheet').innerHTML.match(/class="def-block matchup-victim"/g)||[]).length,(ctx.beatsMap[c]||[]).length);
}
const p44=d.defense.find(t=>t.code==='P44');
assert.deepEqual(Array.from(p44.variants,v=>v.code),['P44','P38']);
for(const query of ['Hayeon Sunran','Sunran Hayeon','SUNRAN, HAYEON','Hayeon; Sunran','  Hayeon   Sunran  ','P38','Eirin']){
  ctx.state.q=query;assert.ok(ctx.matches(p44,false),query);
}
ctx.state.q='Hayeon Yoongun';assert.ok(!ctx.matches(p44,false));ctx.state.q='';
assert.equal(ctx.searchText('Đội HÌNH'),'doi hinh');
assert.equal(ctx.normaliseView({kind:'defense',code:'P10'}).variant,'P10');
assert.equal(ctx.normaliseView({kind:'attack',code:'C239'}).variant,'C239');
assert.equal(ctx.normaliseView({kind:'attack',code:'C41',variant:'P44'}).variant,null);
assert.equal(ctx.normaliseView({kind:'attack',code:'missing'}),null);
assert.equal(ctx.normaliseView({kind:'attack',code:'C41',variant:'C239',against:'P44',againstVariant:'P44'}).against,null);
const card=ctx.counterBlockHTML('C41',0,'P44','P38');
assert.ok(card.includes('data-variant="C239" data-against="P44" data-against-variant="P38"'));
assert.equal(ctx.counterBlockHTML('C41',0,'P44','P44'),'');
const speed=ctx.counterBlockHTML('C95',0,'P44',null);
assert.ok(speed.indexOf('Rudy &gt; Platin &gt; Clemyth')<speed.indexOf('</summary>'),'Speed conditions visible while collapsed');

// The reviewed 30 October data must map every exact front/back arrangement,
// pet, backup, opener, note and reference build to its recorded opponent.
const update=JSON.parse(fs.readFileSync('data/note-2026-10-30.json','utf8'));
const targetCodes={ANkCEbT3BL:'P60','8vpyxcVCAL':'M42','3LZMb7xvTj':'M32',UjAyf9qTnk:'M33',cFn39snCJe:'T38',XMJPSixPsc:'P25'};
const aliases={Tanjiro:'Tanjiro Kamado',Zenitsu:'Zenitsu Agatsuma',Shinobu:'Shinobu Kocho',Giyu:'Giyu Tomioka'};
const canon=s=>aliases[s]||s, sorted=a=>JSON.stringify(Array.from(a,canon).sort());
const formats={Defense:'Defense (4-1)',Attack:'Attack (1-4)',Basic:'Basic (2-3)',Balanced:'Balanced (3-2)'};
let newCases=0;
for(const entry of update.targets){
  const target=d.defense.find(t=>t.code===targetCodes[entry.id]);assert.ok(target,entry.id);
  assert.equal(target.updatedAt,'2026-10-30');
  if(entry.defense){
    assert.equal(target.addedOn,'2026-10-30');
    assert.equal(sorted(target.variants[0].front),sorted(entry.defense.front));
    assert.equal(sorted(target.variants[0].back),sorted(entry.defense.back));
  }
  for(const a of entry.attacks){
    const composition=sorted([...a.front,...a.back]);
    const counter=Object.values(d.counters).find(c=>sorted(c.heroes.map(h=>h.name))===composition);
    assert.ok(counter,`${entry.id}: missing offense trio`);
    const v=counter.variants.find(v=>sorted(v.front)===sorted(a.front)&&sorted(v.back)===sorted(a.back)
      &&v.formation.startsWith(formats[a.formation]+' — ')&&v.pet===a.pet&&sorted(v.petBackup)===sorted(a.backup)
      &&JSON.stringify(Array.from(v.skills,s=>[s.hero,s.slot]))===JSON.stringify(a.skills.map(([h,s])=>[canon(h),s==='S1'?'Skill 1':'Skill 2'])));
    assert.ok(v,`${entry.id}: missing exact offense configuration`);
    const matchup=(target.matchups[counter.code]||[]).find(m=>m.defenseVariant===targetCodes[entry.id]&&m.attackVariant===v.code);
    assert.ok(matchup,`${entry.id}: matchup missing for ${v.code}`);assert.equal(matchup.updatedAt,'2026-10-30');
    assert.equal(matchup.builds.length,3);assert.deepEqual(Array.from(matchup.notes),a.notes);
    for(const b of a.builds)assert.ok(matchup.builds.some(x=>x.hero===canon(b.hero)&&x.details===b.details));
    assert.ok(ctx.counterBlockHTML(counter.code,0,target.code,targetCodes[entry.id]).includes('Có chỉ số và trang bị tham khảo'));
    newCases++;
  }
}
assert.equal(newCases,9);
const p25=d.defense.find(t=>t.code==='P25');
for(const c of ['C33','C181','C37','C183']){
  assert.ok(d.counters[c],`${c}: preserve the existing offense team`);
  assert.ok(!p25.matchups[c],`${c}: remove the obsolete Note-only matchup`);
}
assert.equal(ctx.panelSec('Bai Jiao','Skill 1').n,'Centipede Poison');
assert.equal(ctx.panelSec('Bai Jiao','Skill 2').n,'Fiendish Decree');
assert.equal(ctx.panelSec('Colt','Skill 1').n,"Quick n' Easy");
ctx.state.q='Sunran Hayeon';ctx.state.tab='physical';
const url=new URL(ctx.viewURL({kind:'attack',code:'C41',variant:'C239',against:'P44',againstVariant:'P38'}),'https://example.test');
assert.equal(url.searchParams.get('variant'),'C239');assert.equal(url.searchParams.get('againstVariant'),'P38');
assert.equal(url.searchParams.get('q'),'Sunran Hayeon');assert.equal(url.searchParams.get('group'),'physical');
ctx.state.q='';ctx.state.tab='all';
ctx.openSkillPanel('Clemyth','Skill 1');
assert.equal(document.activeElement.id,'panel-title');assert.equal(node('app').inert,true);assert.equal(node('overlay').inert,true);
ctx.closePanel();assert.equal(node('overlay').inert,false);
const dialog=node('overlay'),first=node('first'),last=node('last');dialog.classList.add('open');dialog.querySelectorAll=()=>[first,last];
const trap=listeners.get('keydown')[0];let prevented=false;
document.activeElement=last;trap({key:'Tab',preventDefault(){prevented=true;}});assert.ok(prevented);assert.equal(document.activeElement,first);
document.activeElement=first;trap({key:'Tab',shiftKey:true,preventDefault(){}});assert.equal(document.activeElement,last);
assert.match(html,/aria-labelledby="sheet-title"/);assert.match(html,/aria-labelledby="panel-title"/);
assert.equal(d.defense.find(t=>t.code==='M32').variants.find(v=>v.code==='M32').skills.length,0);
assert.notEqual(all.find(t=>t.heroes.some(h=>h.name==='Radgrid')).heroes.find(h=>h.name==='Radgrid').img,
  all.find(t=>t.heroes.some(h=>h.name==='Randgrid')).heroes.find(h=>h.name==='Randgrid').img);
console.log(`PASS: 51 defense trios, 93 offense trios, ${edges} visible matchup cases; all 9 updates, conditions, reference builds, variants, search, URLs and focus.`);

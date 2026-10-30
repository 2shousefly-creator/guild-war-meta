"""Rebuild the inline site dataset from the reviewed source snapshots.

No runtime scraping: publishing index.html keeps the existing Cloudflare setup.
Teams are grouped by their three heroes; different formations, pets, queues,
and their exact recorded matchups remain separate variants within that group.
"""
import copy
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / 'index.html'
html = PAGE.read_text()

def inline(name):
    return json.loads(re.search(r'^var ' + name + r' = (.+);$', html, re.M)[1])

old = inline('DATA')
panels = inline('HERO_PANELS')
aliases = {'Tanjiro': 'Tanjiro Kamado', 'Zenitsu': 'Zenitsu Agatsuma',
           'Shinobu': 'Shinobu Kocho', 'Giyu': 'Giyu Tomioka'}
# Radgrid (Defense) and Randgrid (Attack) are different heroes. Never merge them.
def canon(name):
    return aliases.get(name, name)

formats = {'Defense': 'Defense (4-1)', 'Protective': 'Defense (4-1)',
           'Attack': 'Attack (1-4)', 'Basic': 'Basic (2-3)', 'Balanced': 'Balanced (3-2)'}
slots = {'S1': 'Skill 1', 'S2': 'Skill 2', 'AW': 'Awakening'}
keys = {'Skill 1': 's1', 'Skill 2': 's2', 'Awakening': 'aw'}
heroes = {h['name']: h for d in old['defense'] + list(old['counters'].values()) for h in d['heroes']}
heroes['Hellenia'] = {'name': 'Hellenia', 'img': 'chara_490.png'}
heroes['Lina'] = {'name': 'Lina', 'img': 'chara_147.png'}
heroes['Rook'] = {'name': 'Rook', 'img': 'chara_150.png'}
heroes['Bai Jiao'] = {'name': 'Bai Jiao', 'img': 'chara_405.png'}
heroes['Colt'] = {'name': 'Colt', 'img': 'chara_351.png'}
for name, source, definitions in [
    ('Lina', 'https://gamewith.jp/sevenknights-rebirth/513560',
     [('s1', 'Hành khúc (行進曲)', 'skill_192.png'), ('s2', 'Giai điệu chữa lành (癒しの旋律)', 'skill_193.png'), ('pa', 'Bất hòa (不協和音)', 'skill_194.png')]),
    ('Rook', 'https://gamewith.jp/sevenknights-rebirth/513561',
     [('s1', 'Ném giáo (槍投げ)', 'skill_196.png'), ('s2', 'Dàn trận (陣形作り)', 'skill_197.png'), ('pa', 'Khiên công thành (攻城の盾)', 'skill_198.png')])]:
    panels[name] = {'source': source, 'secs': {k: {'n': n, 'i': i} for k, n, i in definitions}}

# These panels describe base, enhanced and transcendence effects separately.
# The local source references are not added as links to the public site.
panels['Bai Jiao'] = {'type': 'Magic', 'secs': {
    's1': {'n': 'Centipede Poison', 'i': 'skill_497.png', 'ct': 60, 'tg': '1 địch', 'dt': 'Magic', 'vp': [
        [{'t': 'Cơ bản: 90% Magic Attack ×3; mỗi đòn có 60% xác suất gây Poison trong 3 lượt.'}],
        [{'t': 'Cường hóa skill: sát thương 110% ×3 và thêm 100% xác suất gây Unable to Recover trong 4 lượt. Siêu việt 6: xác suất Poison 70% mỗi đòn.'}]]},
    's2': {'n': 'Fiendish Decree', 'i': 'skill_498.png', 'ct': 60, 'tg': '1 địch và toàn đồng minh', 'dt': 'Magic', 'vp': [
        [{'t': 'Cơ bản: 80% Magic Attack ×3; mỗi đòn có 60% xác suất gây Bleed trong 3 lượt. Giải 1 debuff cho toàn đồng minh.'}],
        [{'t': 'Cường hóa skill: sát thương 110% ×3. Siêu việt 6: xác suất Bleed 70% mỗi đòn.'}]]},
    'pa': {'n': 'Dark Incantations', 'i': 'skill_499.png', 'tg': 'Bản thân và toàn đồng minh', 'dt': 'none', 'vp': [
        [{'t': 'Cơ bản: bản thân miễn mọi sát thương trong 2 lượt. Khi tấn công, hồi máu cho toàn đồng minh bằng 32% Magic Attack của bản thân 2 lần.'}],
        [{'t': 'Cường hóa skill: miễn sát thương 3 lượt. Siêu việt 2: bản thân tăng Effect Probability 22%.'}]]}
}}
panels['Colt'] = {'type': 'Physical', 'secs': {
    's1': {'n': "Quick n' Easy", 'i': 'skill_422.png', 'ct': 72, 'tg': '4 địch', 'dt': 'Physical', 'vp': [
        [{'t': 'Cơ bản: 40% Physical Attack ×2; mỗi đòn có 35% xác suất gây Bomb trong 3 lượt.'}],
        [{'t': 'Cường hóa skill: sát thương 50% ×2; xác suất Bomb 45% mỗi đòn.'}]]},
    's2': {'n': 'Time for a Show', 'i': 'skill_423.png', 'ct': 104, 'tg': 'Toàn địch', 'dt': 'Physical', 'vp': [
        [{'t': 'Cơ bản: 125% Physical Attack ×1; 50% xác suất gây Bomb trong 3 lượt; kích nổ Bomb ở 150% hiệu lực, tối đa 3 lượt. 100% xác suất giảm All Attack 13% trong 3 lượt.'}],
        [{'t': 'Cường hóa skill: sát thương 150% ×1; giảm All Attack 18%.'}]]},
    'pa': {'n': 'Wandering Gunslinger', 'i': 'skill_424.png', 'tg': 'Bản thân và toàn đồng minh', 'dt': 'none', 'vp': [
        [{'t': 'Cơ bản: bản thân nhận Camouflage 2 lượt; cứ 7 Speed tăng 120 Attack, tối đa 1.080. Toàn đồng minh tăng Effect Hit Rate 28%.'}],
        [{'t': 'Cường hóa skill: giới hạn Attack theo Speed là 1.320; Effect Hit Rate tăng 34%. Siêu việt 2: nhận Guts một lần và khi kích hoạt nhận khiên bằng 155% Physical Attack trong 3 lượt. Siêu việt 6: giảm 23 giây hồi skill khi một địch gục.'}]]}
}}

def fp(t, backup=True):
    return json.dumps([sorted(h['name'] for h in t['heroes']),
        t['formation'].split(' — ')[0], sorted(t['front']), sorted(t['back']),
        t['pet'], [(s['hero'], s['slot']) for s in t['skills']],
        sorted(t.get('petBackup', [])) if backup else []], ensure_ascii=False)

idpath = ROOT / 'data/stable-ids.json'
if idpath.exists():
    ids = json.loads(idpath.read_text())
else:
    ids = {'defense': {}, 'counters': {}, 'next': {'P': 44, 'M': 32, 'T': 34, 'ST': 2, 'C': 179}}
    for t in old['defense']:
        ids['defense'].setdefault(fp(t, False), t['code'])
    for code, t in old['counters'].items():
        ids['counters'].setdefault(fp(t, False), code)

translations = {
 'เรียงสปีด ดี้ > เพลตัน > เคลมิส': 'Thứ tự tốc độ bắt buộc: Rudy > Platin > Clemyth.',
 'ดี้ สปีด 1 กดสกิลตามโพย / ดี้สปีดไม่ 1 กด ล่างบน เคลมิส > บนดี้': 'Nếu Rudy nhanh nhất đội, dùng chuỗi hiển thị. Nếu không, đổi thành Clemyth S1 → Clemyth S2 → Rudy S2.',
 'เปิดก่อนได้ก็ดี': 'Nên giành lượt đi trước nếu có thể.',
 'ทำสปีดให้เปิดก่อน เรียงสปีด ทันจิโร่ เซนอิทสึ ลิโป้': 'Cần đi trước; thứ tự tốc độ: Tanjiro > Zenitsu > Lu Bu.',
 'ได้เริ่มก่อน': 'Cần giành lượt đi trước.',
 'สกัล มิเลีย คริ100(รวมสัตว์)': 'Skuld và Melia cần Crit Rate 100%, tính cả hiệu ứng pet.',
 'เปิดก่อน': 'Cần giành lượt đi trước.',
 'ต้องเปิดก่อน': 'Bắt buộc đi trước.',
 'เปิดก่อนเท่านั้น': 'Chỉ dùng khi đi trước.',
 'เปิดก่อนดีกว่า': 'Nên đi trước.',
 'ยังไม่ได้ลอง': 'CHƯA THỬ đội này; chưa có xác nhận thực chiến.',
 'จูนเลือด ซิลเวสต้า ให้มากกว่าไอลีน': 'Chỉnh HP của Silvesta cao hơn Eileene.',
 'เดลต้องมายืนหน้าเท่านั้น ถึงจะใช้ได้': 'Chỉ áp dụng khi Dellons của đội thủ đứng hàng trước.',
 'ใช้ก็ต่อเมื่อสัตว์ **ไม่ใช่ ยู เท่านั้น**': 'Chỉ dùng khi pet của đội thủ KHÔNG phải Yu.',
 'ต้าน 80+ ทั้งทีม': 'Cả đội cần Effect Resistance từ 80% trở lên.',
 'ใช้กรณี เซนอิทสึ เปิดบน ก่อน': 'Dùng khi Zenitsu của đội thủ mở đầu bằng S2.',
 'ถ้ายุนเปิดบน 1 ต้องเล่นไวกว่า / ถ้ายุนกดบน 2 ให้เล่นช้ากว่า': 'Nếu Yoongun địch dùng S2 ở ưu tiên #1, đội công phải nhanh hơn. Nếu S2 ở #2, đội công phải chậm hơn.',
 'เปิดหลังได้ เรียงสปีด โดยอง > ยอนฮี > ยุนกอน(ขอช้า)': 'Có thể đi sau. Thứ tự tốc độ: Dongyoung > Yeonhee > Yoongun; để Yoongun chậm.',
 'ถ้าแหวนเหลือ เหมาะกับเป็นไม้เปิด': 'Phù hợp làm lượt công mở đầu nếu còn đủ nhẫn cần thiết.',
 'ทันจิโร่สปีด no.1 ต้องเปิดก่อนเข้าบ้านช้าจะดีที่สุด': 'Tanjiro cần tốc độ cao nhất đội và giành lượt đi trước; nên chọn nhà thủ chậm.',
 '**เจอ 2 ตัวหลังไม่ใส่อำนาจ = GG': 'Kiểm tra Ring of Authority của hai tướng hàng sau; điều kiện cụ thể chưa được xác minh.',
 'เฉพาะบ้านที่เปิดยุนก่อน ถ้าบ้านไหนเปิดชิโนบุก่อน โอกาสลื่นสุง': 'Chỉ áp dụng khi đội thủ dùng Yoongun trước. Rủi ro thất bại cao nếu địch mở bằng Shinobu.',
 'เปิดก่อนดีสุด *ถ้าเปิดหลังให้จอง บนล่างซอรัน บนบาลิสต้า*': 'Ưu tiên đi trước. Nếu đi sau, đổi chuỗi thành Sunran S2 → Sunran S1 → Ballista S2.',
 'เปิดก่อนถ้าอยากชนะทีมนี้ชัวๆแหวนซ้อนทุกตัว': 'Cần đi trước và cấu hình nhẫn cho cả đội; chi tiết loại nhẫn chưa được xác minh.',
 'จูนสปีดให้ เปิดก่อน **ทันจิโร่ต้องเลือดน้อยสุด**\n*ถ้าเตียวเสี้ยนอ่อนไม่ 100 ให้สปีดชิโนบุนำเตียวเสี้ยน': 'Chỉnh tốc độ để đi trước; Tanjiro địch phải có HP thấp nhất. Shinobu cần nhanh hơn Diaochan khi cấu hình Diaochan chưa đủ; điều kiện chỉ số chưa được xác minh.',
 'ต้องรู้ข้อมูลก่อน - ถ้ายุนกอนเปิดบนก่อน กดบนวาแดงก่อน - ไม้แก้ถ้าเจอ ชิโนบุเปิดบนก่อน เล่นตามนี้ได้เลย': 'Phải biết chuỗi mở đầu của đội thủ: nếu Yoongun dùng S2 trước, mở bằng Hellenia S2. Nếu Shinobu dùng S2 trước, dùng chuỗi hiển thị.',
}

def translate(raw):
    if not raw:
        return ''
    if raw in translations:
        return translations[raw]
    if any(s in raw for s in ['จูนสปีดให้เปิดก่อน', 'ทำสปีดรวมให้เปิดก่อน', 'ทำสปีดให้เปิดก่อน', 'ปรับสปีดให้เปิดก่อน', 'พยายามดันสปีดให้เปิดก่อน']):
        return 'Chỉnh tổng tốc độ để giành lượt đi trước.'
    if raw.startswith('ดี้สปีด 1'):
        text = 'Nếu Rudy nhanh nhất đội, dùng chuỗi hiển thị. Nếu Rudy không nhanh nhất, đổi thành Clemyth S1 → Clemyth S2 → Rudy S2.'
        if 'สไป' in raw:
            text += ' Chỉ nên dùng như phương án cuối khi đã đầu tư Spike.'
        if 'เข้าเป้า' in raw:
            text += ' Nếu Gelidus/Aris địch có Effect Hit Rate 100% và gây nhiều CC, hãy cân nhắc counter khác.'
        return text
    raise ValueError('Missing translation: ' + raw)

def team(front, back, fmt, pets, queue, source, group):
    front, back = list(map(canon, front)), list(map(canon, back))
    assert len(front + back) == 3 and len(set(front + back)) == 3
    formation = formats[fmt]
    skills = []
    for hero, slot in queue:
        hero, slot = canon(hero), slots[slot]
        assert hero in front + back
        sec = panels.get(hero, {}).get('secs', {}).get(keys[slot])
        # An unknown skill keeps its slot, never guesses an effect or skill name.
        skills.append({'hero': hero, 'slot': slot, 'name': sec['n'] if sec else slot})
    t = {'heroes': [copy.deepcopy(heroes[n]) for n in front + back],
         'front': front, 'back': back, 'pet': pets[0], 'petBackup': pets[1:],
         'formation': formation + ' — Trước: ' + (', '.join(front) or '—') + ' | Sau: ' + (', '.join(back) or '—'),
         'skills': skills, 'sources': [source], 'group': group,
         'groupLabel': {'physical': 'Physical', 'magic': 'Magic', 'tank': 'Tank / Sustain', 'status': 'Status Ailment'}[group]}
    return t

data = {'defense': [], 'counters': {}}
maps = {'defense': {}, 'counters': {}}
used = set()
def add(t, kind):
    k = fp(t)
    if k in maps[kind]:
        found = maps[kind][k]
        for s in t['sources']:
            if s not in found['sources']:
                found['sources'].append(s)
        return found
    ik = fp(t, False)
    code = ids[kind].get(k) or ids[kind].get(ik)
    if not code or code in used:
        prefix = 'C' if kind == 'counters' else {'physical': 'P', 'magic': 'M', 'tank': 'T', 'status': 'ST'}[t['group']]
        while prefix + str(ids['next'][prefix]) in used:
            ids['next'][prefix] += 1
        code = prefix + str(ids['next'][prefix])
        ids['next'][prefix] += 1
    used.add(code)
    ids[kind][k] = code
    t['code'] = code
    if kind == 'defense':
        t['counters'] = []
        t['matchups'] = {}
        data[kind].append(t)
    else:
        data[kind][code] = t
    maps[kind][k] = t
    return t

def edge(d, c, source, raw='', notes=None, builds=None, updated=None):
    if c['code'] not in d['counters']:
        d['counters'].append(c['code'])
    m = d['matchups'].setdefault(c['code'], {'sources': [], 'notes': [], 'rawNotes': [], 'untested': False})
    if source not in m['sources']:
        m['sources'].append(source)
    if raw:
        note = translate(raw)
        if note not in m['notes']:
            m['notes'].append(note)
            m['rawNotes'].append(raw)
        if 'ยังไม่ได้ลอง' in raw:
            m['untested'] = True
    for note in notes or []:
        if note not in m['notes']:
            m['notes'].append(note)
    if builds:
        m['builds'] = [{'hero': canon(b['hero']), 'details': b['details']} for b in builds]
    if updated:
        m['updatedAt'] = updated

note = json.loads((ROOT / 'data/note-2026-10-27.json').read_text())
note_groups = ('physical physical physical physical tank magic magic magic tank physical '
               'tank physical tank tank tank tank tank magic magic magic physical physical '
               'physical physical physical physical physical physical physical tank magic physical '
               'magic tank physical physical physical tank magic tank physical tank tank').split()
assert len(note_groups) == len(note['records'])
supplement = json.loads((ROOT / 'data/note-2026-10-30.json').read_text())
note_targets = {}
for rec, group in zip(note['records'], note_groups):
    source = {'site': '7K Note', 'url': 'https://7k-note.pages.dev/g/4ZyeEGMZ/t/' + rec[0], 'label': 'Pandoara · ' + rec[0]}
    def decode(r, group):
        f, b, fmt, pet, q, backups, raw = r
        return team([note['names'][n] for n in f], [note['names'][n] for n in b], fmt,
                    [note['names'][pet]] + [note['names'][n] for n in backups],
                    [(note['names'][n], s) for n, s in q], source, group)
    d = add(decode(rec[1], group), 'defense')
    note_targets[rec[0]] = d
    for r in rec[2:]:
        c = add(decode(r, group), 'counters')
        removed = supplement['superseded'].get(rec[0], [])
        if any(set(canon(n) for n in names) == set(h['name'] for h in c['heroes']) for names in removed):
            continue
        edge(d, c, source, r[6])

atlas = json.loads((ROOT / 'data/atlas-2026-10-27.json').read_text())
atlas_teams = {}
for rec in atlas['records']:
    ident, f, b, fmt, pets, q, use = rec
    cat = ident.split('-')[0]
    source = {'site': '7K Atlas', 'url': 'https://7katlas.com/guildwar.html?view=teams&tab=' + cat,
              'label': ident + ' · Major · F1'}
    t = team([atlas['names'][n] for n in f], [atlas['names'][n] for n in b], fmt,
             [atlas['names'][n] for n in pets], [(atlas['names'][n], s) for n, s in q], source,
             'status' if cat == 'cc' else cat)
    t['tier'] = 'Major'
    entry = {'source': source, 'use': use}
    if 'Defense' in use:
        entry['d'] = add(copy.deepcopy(t), 'defense')
    if 'Offense' in use:
        entry['c'] = add(copy.deepcopy(t), 'counters')
    atlas_teams[ident] = entry

for ident, relations in json.loads((ROOT / 'data/atlas-matchups-2026-10-27.json').read_text()):
    current = atlas_teams[ident]
    for side, other_id in relations:
        other = atlas_teams.get(other_id, {})
        if side == 'offense' and 'c' in current and 'd' in other:
            edge(other['d'], current['c'], current['source'])
        elif side == 'defense' and 'd' in current and 'c' in other:
            edge(current['d'], other['c'], current['source'])

# Apply the scoped 30 October review after the historical imports. This keeps
# established IDs stable and attaches each configuration-specific matchup only
# to the target that was actually observed.
for target in supplement['targets']:
    source = {'site': '7K Note', 'url': 'https://7k-note.pages.dev/g/4ZyeEGMZ/t/' + target['id'],
              'label': 'Pandoara · ' + target['id']}
    def decode_update(r):
        return team(r['front'], r['back'], r['formation'], [r['pet']] + r['backup'], r['skills'], source, target['group'])
    if 'defense' in target:
        d = add(decode_update(target['defense']), 'defense')
        d['addedOn'] = supplement['reviewed']
    else:
        d = note_targets[target['id']]
    d['updatedAt'] = supplement['reviewed']
    for attack in target['attacks']:
        c = add(decode_update(attack), 'counters')
        edge(d, c, source, notes=attack['notes'], builds=attack['builds'], updated=supplement['reviewed'])

data['research'] = {'reviewed': '2026-10-27', 'atlasHeroSummaryDate': '2026-10-21',
                    'noteTargets': len(note['records']) + sum('defense' in t for t in supplement['targets']),
                    'noteMatchups': sum(len(r) - 2 for r in note['records']) - sum(map(len, supplement['superseded'].values())) + sum(len(t['attacks']) for t in supplement['targets']),
                    'noteSupplementReviewed': supplement['reviewed'],
                    'atlasMajorTeams': 48, 'atlasMatchupTeamsReviewed': 10,
                    'defenseVariants': len(data['defense']), 'offenseVariants': len(data['counters']),
                    'matchups': sum(len(d['counters']) for d in data['defense'])}
for t in data['defense'] + list(data['counters'].values()):
    assert all(h.get('img') for h in t['heroes'])
    cap = {'Defense (4-1)': [4, 1], 'Attack (1-4)': [1, 4], 'Basic (2-3)': [2, 3], 'Balanced (3-2)': [3, 2]}[t['formation'].split(' — ')[0]]
    assert len(t['front']) <= cap[0] and len(t['back']) <= cap[1]

# A visible team is identified only by its unordered trio. Keep every original
# configuration and every directed matchup so merging never implies that a
# counter for one formation also applies to the other formations.
def trio(t):
    return tuple(sorted(h['name'] for h in t['heroes']))

def public_variant(t):
    return {k: copy.deepcopy(v) for k, v in t.items()
            if k not in ('sources', 'counters', 'matchups')}

expected_edges = {
    (d['code'], c): (tuple(d['matchups'][c]['notes']), d['matchups'][c]['untested'], d['matchups'][c].get('builds', []))
    for d in data['defense'] for c in d['counters']}
grouped = {'defense': [], 'counters': {}}
def_groups, ctr_groups, ctr_by_variant = {}, {}, {}
for t in data['counters'].values():
    key = trio(t)
    if key not in ctr_groups:
        g = public_variant(t)
        g['variants'] = []
        grouped['counters'][g['code']] = g
        ctr_groups[key] = g
    g = ctr_groups[key]
    g['variants'].append(public_variant(t))
    ctr_by_variant[t['code']] = g['code']

for t in data['defense']:
    key = trio(t)
    if key not in def_groups:
        g = public_variant(t)
        g.update({'variants': [], 'groups': [], 'counters': [], 'matchups': {}})
        grouped['defense'].append(g)
        def_groups[key] = g
    g = def_groups[key]
    g['variants'].append(public_variant(t))
    if t.get('updatedAt'):
        g['updatedAt'] = max(g.get('updatedAt', ''), t['updatedAt'])
    if t.get('addedOn'):
        g['addedOn'] = t['addedOn']
    if t['group'] not in g['groups']:
        g['groups'].append(t['group'])
    for counter_code in t['counters']:
        counter_group = ctr_by_variant[counter_code]
        if counter_group not in g['counters']:
            g['counters'].append(counter_group)
        m = t['matchups'][counter_code]
        record = {
            'defenseVariant': t['code'], 'attackVariant': counter_code,
            'notes': copy.deepcopy(m['notes']), 'untested': m['untested']}
        for field in ('builds', 'updatedAt'):
            if field in m:
                record[field] = copy.deepcopy(m[field])
        g['matchups'].setdefault(counter_group, []).append(record)

research = copy.deepcopy(data['research'])
research.update({'defenseTeams': len(grouped['defense']),
                 'offenseTeams': len(grouped['counters']),
                 'teamMatchups': sum(len(g['counters']) for g in grouped['defense'])})
grouped['research'] = research
assert sum(len(g['variants']) for g in grouped['defense']) == len(data['defense'])
assert sum(len(g['variants']) for g in grouped['counters'].values()) == len(data['counters'])
assert sum(len(edges) for g in grouped['defense'] for edges in g['matchups'].values()) == research['matchups']
actual_edges = {
    (m['defenseVariant'], m['attackVariant']): (tuple(m['notes']), m['untested'], m.get('builds', []))
    for g in grouped['defense'] for edges in g['matchups'].values() for m in edges}
assert actual_edges == expected_edges, 'Grouping must preserve each exact matchup and its conditions.'

# T17's captured Basic formation has an empty front row. Preserve that
# observation, but lead with a clearly untested suggestion that gives Rudy's
# front-row passive a valid target. No captured matchup is attached to it.
t17 = next(g for g in grouped['defense'] if g['code'] == 'T17')
original = t17['variants'][0]
assert original['front'] == [] and set(original['back']) == {'Knox', 'Rudy', 'Aris'}
assert not t17['counters']
original['advice'] = 'Hàng trước trống nên không có tướng nhận hiệu ứng giảm sát thương dành riêng cho hàng trước của Rudy.'
suggested = copy.deepcopy(original)
suggested.update({'code': 'T17-GOIY', 'front': ['Knox', 'Rudy', 'Aris'], 'back': [],
                  'formation': 'Balanced (3-2) — Trước: Knox, Rudy, Aris | Sau: —',
                  'advice': 'Đề xuất theo cơ chế kỹ năng: cả ba ở hàng trước để nhận hiệu ứng của Rudy. Chưa kiểm chứng thực chiến.',
                  'recommended': True})
t17['variants'].insert(0, suggested)
for field in ('front', 'back', 'formation'):
    t17[field] = copy.deepcopy(suggested[field])
data = grouped

# References are retained in the local research snapshots, but the published
# page has no outgoing source links or source URLs in the panel metadata.
for panel in panels.values():
    panel.pop('source', None)
pet_panels = inline('PET_PANELS')
for panel in pet_panels.values():
    panel.pop('source', None)
if 'Nezuko Kamado' in pet_panels:
    pet_panels['Nezuko Kamado']['levelLabel'] = '6★ — mức cơ bản; chưa đối chiếu giá trị sau cường hóa skill'

html = re.sub(r'^var DATA = .+;$', lambda _: 'var DATA = ' + json.dumps(data, ensure_ascii=False) + ';', html, flags=re.M)
html = re.sub(r'^var HERO_PANELS = .+;$', lambda _: 'var HERO_PANELS = ' + json.dumps(panels, ensure_ascii=False) + ';', html, flags=re.M)
html = re.sub(r'^var PET_PANELS = .+;$', lambda _: 'var PET_PANELS = ' + json.dumps(pet_panels, ensure_ascii=False) + ';', html, flags=re.M)
pet_map = {code: list(dict.fromkeys(p for variant in c['variants'] for p in [variant['pet']] + variant['petBackup']))
           for code, c in data['counters'].items()}
html = re.sub(r'^var COUNTER_PETS = .+;$', lambda _: 'var COUNTER_PETS = ' + json.dumps(pet_map, ensure_ascii=False) + ';', html, flags=re.M)
html = re.sub(r'^var PROPOSED_(DEFENSE|COUNTER) = .+;$', lambda m: 'var PROPOSED_' + m[1] + ' = {};', html, flags=re.M)
PAGE.write_text(html)
idpath.write_text(json.dumps(ids, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(data['research'], ensure_ascii=False, indent=2))

# Guild War Meta — Seven Knights Re:BIRTH

Vietnamese reference site for Major League 3v3. Cloudflare deploys the static `index.html` from `main`.

## Lookup and navigation

- Search accepts multiple names in any order, ignores case/diacritics, and treats spaces, commas, semicolons, `+` and `|` as separators. All terms must match the same team. Team/variant codes and primary/backup pets remain searchable.
- Matchup links carry the exact offense variant, defense variant and opponent context. Variant-code suggestions expand the matching configuration instead of always opening configuration 1.
- Detail URLs preserve the current search/category and selected configuration. Browser Back/Forward and the in-sheet Back button restore the preceding view, expanded cases and modal scroll position. Close returns to the list; a fresh shared link gets a list entry so closing it stays on the site.
- Counter cases start collapsed on all screen sizes. Opening queues and recorded conditions remain visible in each summary; full formation/skill diagrams are expandable. Variant filters only show explicitly recorded matchups for that configuration.
- Dialogs manage initial focus, Tab/Shift+Tab containment, nested-panel Escape, background `inert`, scroll locking and focus restoration. Search suggestions expose their selected option to assistive technology, and category tabs support arrow keys/Home/End.

Example exact-pair URL:

```text
?view=attack&team=C41&variant=C239&against=P44&againstVariant=P38
```

Run `node scripts/check_dataset.cjs` to check data integrity, every visible configuration-specific matchup in both directions, the 30 October update, multi-name search, exact-variant links, compact summaries, URL state and modal focus. The current merged dataset contains 141 configuration-specific cases; the runtime excludes two explicitly untested historical cases, leaving 139 visible cases.

## Scoped update on 30 October 2026

`data/note-2026-10-30.json` records two newly observed defense trios and nine newly observed configuration-specific offense matchups. The four older P25 matchups no longer listed for the reviewed 7K Note target were supported only by that older Note snapshot, so their P25 links are removed; the offense teams themselves remain in the library. The separate Atlas relationships are retained. Existing team and variant IDs remain stable.

Stats, rings and gear displayed in the expandable reference-build section describe the individual recorded setups. They are examples associated with that exact matchup, not independently proven minimum requirements or measured win rates. The 30 October review covered these six targets; the other historical data retain their original review date. Source URLs stay in repository data and are not linked on the public site.

## Data reviewed on 27 October 2026

- [7K Note / Pandoara](https://7k-note.pages.dev/g/4ZyeEGMZ?tab=targets): 43 enemy entries, 104 listed counter occurrences. Research references remain in the repository and are not linked from the public site.
- [7K Atlas Guild War](https://7katlas.com/guildwar.html): 48 **Major** variants across Physical, Magic, Tank and CC. Formation **F1** is the captured variant; this snapshot does not claim to contain F2, Minor, Situational or Unused variants.
- Ten Physical matchup panels from Atlas were inspected. Only explicit **offense wins against defense** and **defense loses against offense** relations are imported, and only when both referenced configurations exist in this snapshot. This is not an exhaustive import of Atlas matchups.
- Result: **49 unique defense trios and 89 unique offense trios**, representing 67 defense configurations, 127 offense configurations, and 136 directed configuration-specific matchups. Configurations include primary pet, backup pets, formation, front/back rows and opening queue. Empty queues remain empty.

This is a dated manual research snapshot, not an automatic update service. Atlas's “Heroes Used in Guild War” summary displayed 21 October 2026; that label is not asserted to be the modification date of every team.

## Skill conventions

Visual order is **Awakening (if present), S2, S1**, from top to bottom. Two-icon heroes have S2 above S1. Priority #1/#2/#3 means usage order. Atlas reverses the DOM order using CSS: DOM order alone must never be interpreted as visual order. Explicit skill codes were checked against the displayed layout. Note's “Top skill” maps to S2; “Bottom skill” maps to S1. Do not add passive awakenings to an active queue.

**Radgrid and Randgrid are different heroes.** Do not normalize these names together. Short Demon Slayer names are normalized to their full English names.

## Updating

The two compact source snapshots have a `names` dictionary. Note records contain a target ID followed by defense and counter records: `[front, back, formation, primaryPet, queue, backupPets, originalNote]`. Atlas records contain `[sourceTeamId, front, back, formation, pets, queue, usage]`. Name and pet references are dictionary indexes.

Run from the repository root to rebuild both the historical data and the scoped 30 October supplement:

```sh
python scripts/build_dataset.py
node scripts/check_dataset.cjs
```

The builder groups teams by an unordered set of three heroes while preserving stable variant IDs, different configurations and their exact counter conditions. Each detail view identifies which defense and offense configurations a matchup applies to. The builder verifies all 136 recorded configuration-to-configuration relationships survive grouping. No external network is needed to rebuild. Do not infer extra counter pairs from overlapping heroes, pet substitutions, or reversing a recorded outcome.

T17 includes an explicitly untested Balanced suggestion with Rudy, Knox and Aris in front, so Rudy's front-row passive has recipients. Its recorded Basic layout is retained and labeled with the front-row limitation; no matchup is inferred for the suggestion.

Thai conditions are summarized in Vietnamese beside each matchup. Original wording is retained in the repository snapshots. Explicitly untested historical matchups are excluded from public counter lists. Display order is not a win-rate ranking. The public page links only to the 7krbvn fanpage; external image URLs are retained for illustrations.

## Illustrations and skill reference

Existing hero/pet/skill illustrations come from GameWith. Added references:

- [Lina](https://gamewith.jp/sevenknights-rebirth/513560): `chara_147.png`, skills 192–194.
- [Rook](https://gamewith.jp/sevenknights-rebirth/513561): `chara_150.png`, skills 196–198.
- [Nezuko Kamado pet](https://gamewith.net/sevenknights-rebirth/78031): `pet_102.png`. Its 6★ base effect is scoped to Demon Slayer allies; it is not labeled as an enhanced maximum.

The existing detailed hero and pet effect library was retained. This refresh does not assert that every pre-existing effect, enhancement value or translation was re-audited. Lina/Rook have verified icons and translated skill names, with missing numerical effects explicitly left unspecified.

Game images © Netmarble Corp. & Netmarble Nexus Inc. This fan site is not affiliated with Netmarble, GameWith, 7K Note or 7K Atlas.

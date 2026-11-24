# WARNING (2026-11-16): Ted edits the pages by hand on GitHub. Running this rewrites every page
# and wipes those edits. Edit the .html files directly instead.
import re, html, os, sys

# Builds every page of awesomesquad.fyi. Usage: python3 tools/build_site.py <site dir> <path to Constants.gd>
# Keystone text is read from the Telecrisis Chris game code. Telecrisis Revenge facts (classes, circuits,
# inputs, gear counts) come from data/revenge.json, exported from the Revenge repo with
#   godot --headless -s res://tools/export_site_data.gd -- <site dir>/data/revenge.json
# Everything else is in this file.
import json
OUT = sys.argv[1]
SRC = sys.argv[2] if len(sys.argv) > 2 else "../Telecrisis-Chris/scripts/autoloads/Constants.gd"
src = open(SRC, encoding="utf-8").read()
E = html.escape
RV = json.load(open(os.path.join(OUT, "data", "revenge.json"), encoding="utf-8"))
RV_VER = RV["version"]

# ---- keystones from the game code ----
pool = src[src.index("const KEYSTONE_POOL := {"):]
pool = pool[:pool.index("\n}\n")]
keystones = {}
for block in re.finditer(r'"(\w+)": \[(.*?)\n\t\]', pool, re.S):
    pid = block.group(1)
    keystones[pid] = [
        dict(name=m.group(1), desc=m.group(2), r2=m.group(3))
        for m in re.finditer(r'"name":"(.*?)".*?"desc":"(.*?)".*?"r2":"(.*?)"', block.group(2), re.S)
    ]

PILOTS = [
    # id, name, color, role, ability title, ability text, hull, shields, dice, unlock
    ("will", "Schmeckeldorf", "#4488FF", "Patient marksman. Lock-on builds while the Core sits in the attack window.",
     "Targeting Lock", "+1 attack die for each consecutive turn with the target in your attack arc (max +3).", 13, 5, 2, None),
    ("ted", "IMPACTO", "#FF2222", "Brawler. Likes it up close and personal.",
     "Firing Solution", "+1 attack die per turn within 240px of your target. At +2 or more, gain Evades as well.", 8, 3, 3, None),
    ("peter", "SpooderMoon", "#FF8811", "Precision alignment and speed.",
     "Precision Lock", "With velocity and facing within 30° of each other, attacks hit on 8+.", 10, 4, 2, None),
    ("cara", "LSP", "#E050E0", "Slow and steady. Surplus shields become harvest power.",
     "Harvest Conversion", "Each shield above max is +1 harvest die. Overload costs 2 energy.", 14, 7, 1, None),
    ("steven", "Axemodeus", "#1AD9D9", "Cool and calculated.",
     "Calculated Strike", "Hitting on consecutive turns from the same arc zone grants +1 die (max 3). Resets when you switch arcs.", 10, 5, 2, "Unlocks with progress"),
    ("covert", "Cobra", "#F2BF1A", "Gutsy and tricky.",
     "Rule Bender", "May fire outside the attack arc once per turn; misses deal 1 self damage.", 9, 4, 3, "Unlocks with progress"),
    ("kevin", "BlueJello", "#80E64D", "Methodical researcher. Gets more efficient the longer the fight runs.",
     "Prior Research", "+1 harvest die on turn 5, +2 on turn 10, +3 on turn 15. Overload gets cheaper as the star fight goes on.", 11, 6, 2, "Unlocks with progress"),
    ("ryan", "Bruce", "#D91A80", "Commander. Reads the board and adapts.",
     "Command Presence", "+1 attack die for each different arc fired from in a rolling 3 turns (max 3).", 11, 5, 2, "Unlocks with progress"),
]

NAV = [("index.html", "Home"), ("chris.html", "Telecrisis Chris"), ("pilots.html", "Pilots"),
       ("revenge.html", "Telecrisis Revenge"), ("classes.html", "Classes"),
       ("gallery.html", "Screenshots"), ("devlog.html", "Devlog"), ("team.html", "Team")]

# Links: set url to a real address to switch a button on. Empty = shown greyed out as "soon".
LINKS = [
    ("itch.io", "https://tsavagegames.itch.io/telecrisis-chris", "Play / download"),
    ("Steam", "", "Wishlist"),
    ("Discord", "", "Join the squad"),
    ("YouTube", "https://www.youtube.com/@SAVAGE-GAMES-LLC", "Videos"),
    ("Twitch", "", "Live streams"),
]

def link_btns(primary_first=True):
    out = []
    for i, (name, url, label) in enumerate(LINKS):
        cls = "btn primary" if (i == 0 and primary_first and url) else "btn"
        if url:
            out.append(f'<a class="{cls}" href="{E(url)}" target="_blank" rel="noopener">{E(label)} · {E(name)}</a>')
        else:
            out.append(f'<span class="btn off" title="Link coming soon">{E(name)} <span class="soon">soon</span></span>')
    return '<div class="btns">' + "".join(out) + "</div>"

# Site-only wording: hand edits to text that comes from the game data (pilot abilities etc.).
# Each (game text, site text) pair is swapped in when its page is written. If the game's text
# changes, the pair stops matching and the new game text shows instead.
SITE_WORDING = {
    'chris.html': [
        (':description" content="Telecrisis Chris is a turn-based space roguelike: plan your flight, attack the Void Core, harvest energy, and survive the enemy and gravity phases.">',
         ':description" content="Telecrisis Chris is a turn-based space roguelike: plan your flight, attack the Core, harvest energy, and survive the enemy and gravity phases.">'),
    ],
    'gallery.html': [
        ('Void Core"><img src="img/shots/star-yellow-sm.jpg" alt="Yellow Star: lining up on the Void Core" loading="lazy"></a><figcaption>Yellow Star: lining up on the Void',
         'Core"><img src="img/shots/star-yellow-sm.jpg" alt="Yellow Star: lining up on the Core" loading="lazy"></a><figcaption>Yellow Star: lining up on the'),
    ],
    'pilots.html': [
        ('re</strong> — At max lock, fire a free volley at the nearest enemy in your arc before they get a chance! <span class="small">Rank II: Overwatch Fire shoots two volleys.</span></li><li><strong>Pin Down</strong> — At max lock, every enemy in arc loses their turn and does not move. <span class="small">Rank II: Pin Down wors at lock 2, not only when at max.</span></li><li><strong>Recoil Rail</strong> — Every volley that hits shoves you 80px straight back from target.  Turn RECOIL off when you&#x27;d rather stay put. <span class="small">Rank II: The target is shoved 80px the other way too.</span></li><li><strong>Anchor &amp; Launch</strong> — Coast and your ship stops, building lock twice as fast. The next move launches at full throttle and can turn without penalty. <span class="small">Rank II: While anchored, your firing range is doubled',
         'ire</strong> — At max lock, fire a volley at the nearest enemy in your arc during the enemy phase, before they have a chance to respond. <span class="small">Rank II: Shoots two volleys.</span></li><li><strong>Pin Down</strong> — At max lock, every enemy in your arc and range loses its turn entirely. <span class="small">Rank II: Pin Down works from lock at 2.</span></li><li><strong>Lock Leash</strong> — While you hold a lock, the nearest enemy in your arc is dragged 60px toward you each turn. <span class="small">Rank II: The leash drags 120px, and a rock collision deals 4 to both.</span></li><li><strong>Sniper&#x27;s Nest</strong> — A turn spent coasting doubles your firing range and builds lock twice as fast. <span class="small">Rank II: A coasting turn triples your firing range'),
        ('enemies does no self damage and deals 2, 4 or 6 damage based on speed. Fully destroying an enemy this way does not slow you down. <span class="small">Rank II: Ramming deals 3, 6, or 9 damage.</span></li><li><strong>Dogleg</strong> — Your move adds a bend of up to 90° in PLAN and the last 40% of the move turns that direction for 1 stress. <span class="small">Rank II: The bend can be any angle, stress free.</span></li><li><strong>Shockwave Brake</strong> — Losing 150 or more speed in one maneuver blasts everything within 150px for 2. <span class="small">Rank II: The blast deals 4 and reaches 200px.</span></li><li><strong>Grapple Hook</strong> — A hit hooks the enemy or rock (a kill hooks its wreck for 2 turns). In PLAN you can choose REEL IN instead of your move: you fly straight there and ram whatever&#x27;s left for 2, 4 or 6 by your speed, taking no damage. <span class="small">Rank II: A hooked enemy cannot shoot',
         'an enemy costs you no hull and hits it for 2, 4 or 6 based on speed. If that destroys the enemy, you fly on through. <span class="small">Rank II: Ramming hits for 3, 6 or 9.</span></li><li><strong>Slingshot</strong> — After a turn ending inside solution range of your target (Solution 1+), you can turn any amount for free. <span class="small">Rank II: The free turn no longer needs Solution.</span></li><li><strong>Shockwave Brake</strong> — Losing 150 or more speed in one move blasts everything within 150px for 2. <span class="small">Rank II: The blast deals 4 and reaches 200px.</span></li><li><strong>Grapple</strong> — Your hit tethers an enemy: it can&#x27;t move, and while you&#x27;re within 500px you swing around the tethered enemy. <span class="small">Rank II: A tethered enemy can&#x27;t shoot either'),
        ('precision shot hitting everything in a line. <span class="small">Rank II: Everything behind the first target takes 2 additional hits.</span></li><li><strong>Strafe Run</strong> — With Precision active, every rock and enemy you move within 80px takes  a shot with half dice. <span class="small">Rank II: Strafe Run shoots with full dice.</span></li><li><strong>Slipstream</strong> — Precision kills grant a charge. <span class="small">Rank II: Any kill grants a charge, Precision or not.</span></li><li><strong>Pinball</strong> — Rocks and the board edge bounce you off retaining speed and dealing no damage. Precision is retained after a bounce. <span class="small">Rank II: Each rock you bounce off suffers 2 damag',
         'Precision shot that hits passes through everything on its line, dealing its full damange. <span class="small">Rank II: Everything behind the first target takes 2 additional hits.</span></li><li><strong>Strafe Run</strong> — With Precision up, every rock and enemy your move passes within 80px of takes a shot at half your dice. <span class="small">Rank II: Strafe Run shoots with your full dice.</span></li><li><strong>Slipstream</strong> — A Precision kill gives you a charge. <span class="small">Rank II: Any kill gives the charge.</span></li><li><strong>Dead Stick</strong> — Coasting keeps Precision up, and a coasting turn can rotate any amount for free. <span class="small">Rank II: Coasting also gives +2 attack dic'),
        ('consuming all shields: +1 automatic hit per shield consumed this way. <span class="small">Rank II: Each shield dumped is 2 automatic hits.</span></li><li><strong>Corona Diver</strong> — Radiation charges shields instead of draining them. <span class="small">Rank II: Radiation Charges twice as many shields.</span></li><li><strong>Plough</strong> — With shields over half, hittin rocks deals 1 shield damage and destroys the rock. <span class="small">Rank II: Every shield you hold can plough through a rock, not only those above half.</span></li><li><strong>Overflow Burst</strong> — Shield gain past full cause explosions',
         'dumps all your shields into it granting +1 automatic hit per shield. <span class="small">Rank II: Each shield dumped is 2 automatic hits.</span></li><li><strong>Corona Diver</strong> — Radiation charges your shields instead of draining them. <span class="small">Rank II: Radiation charges twice as many shields.</span></li><li><strong>Plough</strong> — While your shields are over half, hitting a rock costs 1 shield and destroys the rock. <span class="small">Rank II: Every shield you hold can plough a rock. </span></li><li><strong>Overflow Burst</strong> — Shields you gain past your max explode'),
        ('With max streak, shots that hit trigger an additional volley at the nearest target. <span class="small">Rank II: The second volley rolls 2 additional dice.</span></li><li><strong>Hot Hand</strong> — With max streak, a shot that hits fires again until missing (max 6). <span class="small">Rank II: Hot Hand starts one below streak max.</span></li><li><strong>Cash Out</strong> — Charged shot spending entire streak with 2 automatic hits per spend. <span class="small">Rank II: Each streak stack is 3 automatic hits.</span></li><li><strong>Insider Trading</strong> — Your next attack roll is shown under your ship before you fly. When you attack, use it or roll fresh. <span class="small">Rank II: The lowest die of the roll shown always becomes a nat',
         'At max streak, a shot that hits fires a second full volley at the nearest target in your arc. <span class="small">Rank II: The second volley rolls 2 extra dice.</span></li><li><strong>Hot Hand</strong> — At max streak, a shot that hits fires repeatedly until a volley misses (up to 6). <span class="small">Rank II: Hot Hand starts one streak below max.</span></li><li><strong>Cash Out</strong> — A charged shot spends your whole streak granting 2 automatic hits per stack. <span class="small">Rank II: Each streak stack is 3 automatic hits.</span></li><li><strong>Insider Trading</strong> — Your next attack roll is made ahead of time and shown under your ship. <span class="small">Rank II: The lowest die of the roll shown always becomes a'),
        ('the first rock or enemy you pass through gives +1 stress instead of collision. <span class="small">Rank II: You pass through the first ttwo obstacles each turn.</span></li><li><strong>Hijack</strong> — An enemy hit from outside your arc is yours next turn (kill it and the nearest other enemy within 300px is). In PLAN, point where it flies or HOLD it. It doesn&#x27;t shoot, and flown into a rock, both take 2. <span class="small">Rank II: You steer it for two turns.</span></li><li><strong>Blink</strong> — A hit from outside arc leaves a blink marker for 2 turns. During PLAN, select BLINK to jump to the marker, then make a move. <span class="small">Rank II: Blinking also sets your evade to 2.</span></li><li><strong>Decoy</strong> — A hit from outside arc drops a decoy that attracts enemies within 320px next turn. <span class="small">Rank II: The decoy draws enemy fire',
         'you pass through the first rock or enemy in your path for +1 stress instead of crashing. <span class="small">Rank II: You pass through the first two obstacles each turn.</span></li><li><strong>Double Agent</strong> — An enemy hit by a shot from outside your arc spends its next turn shooting the nearest other enemy. <span class="small">Rank II: A turned enemy deals double damage.</span></li><li><strong>Blink</strong> — A shot from outside your arc that hits swaps you with the rock you hit, or puts you where a destroyed target was. <span class="small">Rank II: Blinking also sets your evade to 2.</span></li><li><strong>Decoy</strong> — A shot from outside your arc that hits drops a decoy where you are: enemies within 320px of it waste their next turn. <span class="small">Rank II: The decoy draws enemies'),
        ('its a pulse from your ship damaging enemies and rocks within 200px. <span class="small">Rank II: The discharge deals double damage and expands to 300px.</span></li><li><strong>Rock Refinery</strong> — Destroying a rock within 150px rolls 3 harvest dice plus any bonus harvest dice. <span class="small">Rank II: Works out to 300px and rolls 2 more dice.</span></li><li><strong>Probe</strong> — Harvesting leaves behind a probe. Turns without harvest will perform a harvest from the probe. <span class="small">Rank II: The probe harvests every turn, even when you do.</span></li><li><strong>Critical Mass</strong> — Overload spends up to 9 additional energy (never last 10) and deals an additional damage per 3 spen',
         'minates a damaging pulse from your ship, damaging every enemy and rock within 200px. <span class="small">Rank II: The discharge deals double damage and reaches 300px.</span></li><li><strong>Rock Refinery</strong> — Destroying a rock within 150px rolls 3 harvest dice, plus your bonus harvest dice. <span class="small">Rank II: Works out to 300px and rolls 2 more dice.</span></li><li><strong>Probe</strong> — Harvesting leaves a probe behind. On turns you don&#x27;t harvest, it rolls the zone&#x27;s base dice for you. <span class="small">Rank II: The probe harvests every turn, even when you do.</span></li><li><strong>Critical Mass</strong> — Overload spends up to 9 extra energy (never your last 10) and deals 1 damage per 3 spent, ignoring the per-turn limi'),
        ('hit also fires at every other target in arc with a third of your attack dice. <span class="small">Rank II: Full Spread rolls half your dice.</span></li><li><strong>Broadside</strong> — A hit also fires a full volley at the nearest target outside of arc. <span class="small">Rank II: Broadside fires at the two nearest targets outside your arc.</span></li><li><strong>Pivot Fire</strong> — A turn after shooting grants turning any amount the following turn regardless of speed and does not apply stress. <span class="small">Rank II: The free turn no longer needs a shot first.</span></li><li><strong>Wing Drone</strong> — A drone fires half your dice at the nearest enemy out of your arc at the start of the enemy phase. <span class="small">Rank II: The drone fires with',
         'shot that hits also fires at every other target in your arc and range with a third of your attack dice. <span class="small">Rank II: Full Spread rolls half your dice.</span></li><li><strong>Broadside</strong> — A shot that hits also fires a full volley at the nearest target outside your arc. <span class="small">Rank II: Broadside fires at the two nearest targets outside your arc.</span></li><li><strong>Pivot Fire</strong> — The turn after you shoot, you can turn any amount, with no speed limit on turning and no turning stress. <span class="small">Rank II: The free turn no longer needs a shot first.</span></li><li><strong>Wing Drone</strong> — A drone fires half your dice at the nearest enemy outside your arc when the enemy phase starts. <span class="small">Rank II: The drone fires your'),
        ('"og:description" content="The eight pilots of Telecrisis Chris, their ships, signature abilities and keystones.">',
         '"og:description" content="The pilots of Telecrisis Chris and signature abilities/keystones.">'),
        ('free volley at the nearest enemy in your arc when the enemy phase starts, before they act. <span class="small">Rank II: Overwatch Fire shoots two volleys.</span></li><li><strong>Pin Down</strong> — At max lock, every enemy in your arc and range loses its turn: no move, no shot. <span class="small">Rank II: Pin Down works from lock 2, not only at max.</span></li><li><strong>Recoil Rail</strong> — Every volley that hits shoves you 80px straight back from your target. Back away while you shoot, or fire to brake. <span class="small">Rank II: The target is shoved 80px the other way too. Shoved into a rock, both take 2.</span></li><li><strong>Anchor &amp; Launch</strong> — Coast (no thrust) and your ship stops dead and builds lock twice as fast. Your next move launches at full throttle and can turn any amount, with no turning stress. <span class="small">Rank II: While anchored, your firing range is doubled',
         'volley at the nearest enemy in your arc during the enemy phase, before they have a chance to respond. <span class="small">Rank II: Shoots two volleys.</span></li><li><strong>Pin Down</strong> — At max lock, every enemy in your arc and range loses its turn entirely. <span class="small">Rank II: Pin Down works from lock at 2.</span></li><li><strong>Lock Leash</strong> — While you hold a lock, the nearest enemy in your arc is dragged 60px toward you each turn. <span class="small">Rank II: The leash drags 120px, and a rock collision deals 4 to both.</span></li><li><strong>Sniper&#x27;s Nest</strong> — A turn spent coasting doubles your firing range and builds lock twice as fast. <span class="small">Rank II: A coasting turn triples your firing range'),
        ('y your speed. If that destroys it, you fly on through. <span class="small">Rank II: Ramming hits for 3, 6 or 9.</span></li><li><strong>Dogleg</strong> — Your move gets a second leg: set a kink of up to 90° in PLAN and the last 40% of the move turns that way (+1 stress). Bend around a rock or into a ram. <span class="small">Rank II: The kink can be any angle, with no stress.</span></li><li><strong>Shockwave Brake</strong> — Losing 150 or more speed in one move blasts everything within 150px for 2. <span class="small">Rank II: The blast deals 4 and reaches 200px.</span></li><li><strong>Grapple Hook</strong> — A hit hooks the enemy. In PLAN you can choose REEL IN instead of your move: you fly straight to it and ram it for 2, 4 or 6 by your speed, taking no damage. <span class="small">Rank II: A hooked enemy can&#x27;t shoot',
         'ased on speed. If that destroys the enemy, you fly on through. <span class="small">Rank II: Ramming hits for 3, 6 or 9.</span></li><li><strong>Slingshot</strong> — After a turn ending inside solution range of your target (Solution 1+), you can turn any amount for free. <span class="small">Rank II: The free turn no longer needs Solution.</span></li><li><strong>Shockwave Brake</strong> — Losing 150 or more speed in one move blasts everything within 150px for 2. <span class="small">Rank II: The blast deals 4 and reaches 200px.</span></li><li><strong>Grapple</strong> — Your hit tethers an enemy: it can&#x27;t move, and while you&#x27;re within 500px you swing around the tethered enemy. <span class="small">Rank II: A tethered enemy can&#x27;t shoot either'),
        ('hits to each. <span class="small">Rank II: Everything behind the first target takes 2 extra hits.</span></li><li><strong>Strafe Run</strong> — With Precision up, every rock and enemy your move passes within 80px of takes a shot at half your dice. <span class="small">Rank II: Strafe Run shoots with your full dice.</span></li><li><strong>Slipstream</strong> — A Precision kill gives you a charge: move again or fire again. <span class="small">Rank II: Any kill gives the charge, Precision or not.</span></li><li><strong>Pinball</strong> — Rocks and the board edge bounce you off at full speed instead of hurting you. Precision stays up through a bounce. <span class="small">Rank II: Each rock you bounce off takes 2',
         'damange. <span class="small">Rank II: Everything behind the first target takes 2 additional hits.</span></li><li><strong>Strafe Run</strong> — With Precision up, every rock and enemy your move passes within 80px of takes a shot at half your dice. <span class="small">Rank II: Strafe Run shoots with your full dice.</span></li><li><strong>Slipstream</strong> — A Precision kill gives you a charge. <span class="small">Rank II: Any kill gives the charge.</span></li><li><strong>Dead Stick</strong> — Coasting keeps Precision up, and a coasting turn can rotate any amount for free. <span class="small">Rank II: Coasting also gives +2 attack dice'),
        (': +1 automatic hit per shield. <span class="small">Rank II: Each shield dumped is 2 automatic hits.</span></li><li><strong>Corona Diver</strong> — Radiation charges your shields instead of draining them. <span class="small">Rank II: Radiation charges twice as many shields.</span></li><li><strong>Plough</strong> — While your shields are over half, hitting a rock costs 1 shield and destroys the rock. Fissures stay solid. <span class="small">Rank II: Every shield you hold can plough a rock, not only those above half.</span></li><li><strong>Overflow Burst</strong> — Shields you gain past your max explode: 1 damage each',
         ' granting +1 automatic hit per shield. <span class="small">Rank II: Each shield dumped is 2 automatic hits.</span></li><li><strong>Corona Diver</strong> — Radiation charges your shields instead of draining them. <span class="small">Rank II: Radiation charges twice as many shields.</span></li><li><strong>Plough</strong> — While your shields are over half, hitting a rock costs 1 shield and destroys the rock. <span class="small">Rank II: Every shield you hold can plough a rock. </span></li><li><strong>Overflow Burst</strong> — Shields you gain past your max explode dealing 1 damage'),
        ('other target in your arc (the same target if there is none). <span class="small">Rank II: The second volley rolls 2 extra dice.</span></li><li><strong>Hot Hand</strong> — At max streak, a shot that hits fires again, and again, until a volley misses (up to 6). <span class="small">Rank II: Hot Hand starts one streak below max.</span></li><li><strong>Cash Out</strong> — A charged shot spends your whole streak: 2 automatic hits per stack. <span class="small">Rank II: Each streak stack is 3 automatic hits.</span></li><li><strong>Insider Trading</strong> — Your next attack roll is shown under your ship before you fly. When you attack, use it or roll fresh',
         'target in your arc. <span class="small">Rank II: The second volley rolls 2 extra dice.</span></li><li><strong>Hot Hand</strong> — At max streak, a shot that hits fires repeatedly until a volley misses (up to 6). <span class="small">Rank II: Hot Hand starts one streak below max.</span></li><li><strong>Cash Out</strong> — A charged shot spends your whole streak granting 2 automatic hits per stack. <span class="small">Rank II: Each streak stack is 3 automatic hits.</span></li><li><strong>Insider Trading</strong> — Your next attack roll is made ahead of time and shown under your ship'),
        ('Fissures stay solid. <span class="small">Rank II: You pass through the first two obstacles each turn.</span></li><li><strong>Hijack</strong> — An enemy hit from outside your arc is yours next turn: in PLAN, point where it flies. It doesn&#x27;t shoot, and flown into a rock, both take 2. <span class="small">Rank II: You steer it for two turns.</span></li><li><strong>Blink</strong> — A hit from outside your arc leaves a blink marker for 2 turns. In PLAN choose BLINK: you jump to the marker (swapping with a rock), then make your move',
         '<span class="small">Rank II: You pass through the first two obstacles each turn.</span></li><li><strong>Double Agent</strong> — An enemy hit by a shot from outside your arc spends its next turn shooting the nearest other enemy. <span class="small">Rank II: A turned enemy deals double damage.</span></li><li><strong>Blink</strong> — A shot from outside your arc that hits swaps you with the rock you hit, or puts you where a destroyed target was'),
        ('discharges from your ship: its damage to',
         'emminates a damaging pulse from your ship, damaging'),
    ],
    'team.html': [
        ('g:description" content="The people behind the Telecrisis games, plus music, art and sound credits.">',
         'g:description" content="The people behind Telecrisis, plus music, art and sound credits.">'),
    ],
}


def page(fname, title, desc, body, extra="", image="img/shots/star-yellow.jpg"):
    nav = "".join(f'<a href="{h}"{" class=on" if h == fname else ""}>{t}</a>' for h, t in NAV)
    foot_links = "".join(
        f'<a href="{E(u)}" target="_blank" rel="noopener">{E(n)}</a>' for n, u, _ in LINKS if u)
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:image" content="https://awesomesquad.fyi/{image}">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="favicon.png">
<link rel="stylesheet" href="style.css">
</head>
<body>
<div class="stars" aria-hidden="true"></div>
<header class="site-head"><div class="inner">
  <a class="brand" href="index.html"><img src="img/icon.png" alt="">Awesome <span>Squad</span></a>
  <nav>{nav}</nav>
</div></header>
<main>
{body}
</main>
<footer class="site-foot">
  <span>© Awesome Squad · awesomesquad.fyi</span>
  <span class="links">{nav}{foot_links}</span>
</footer>
{extra}
</body>
</html>
"""
    for old, new in SITE_WORDING.get(fname, []):
        doc = doc.replace(old, new)
    open(os.path.join(OUT, fname), "w", encoding="utf-8").write(doc)

# ---------------- index ----------------
page("index.html", "Awesome Squad · The Telecrisis games",
     "Awesome Squad: home of the Telecrisis games: the space roguelike Telecrisis Chris and the arena tactics RPG Telecrisis Revenge.", f"""
<section class="hero">
  <div>
    <div class="kicker">Awesome Squad</div>
    <h1>The <span>Telecrisis</span> games</h1>
    <p class="lead">Tactical space game. Plan your move, commit to it, and live or die by your choices.</p>
    <div class="btns">
      <a class="btn primary" href="chris.html">Meet Telecrisis Chris</a>
      <a class="btn primary" href="revenge.html">Meet Telecrisis Revenge</a>
      <a class="btn" href="gallery.html">See screenshots</a>
    </div>
  </div>
  <a href="gallery.html"><img class="shot" src="img/shots/star-yellow.jpg" alt="Telecrisis Chris: a pilot lines up on the Core around a yellow star"></a>
</section>

<section>
  <h2>The games</h2>
  <div class="grid">
    <a class="card" href="chris.html">
      <span class="tag">In development · v1.0.2</span>
      <h3>Telecrisis Chris</h3>
      <p>A tactical turn-based space roguelike. Selecct a Pilot and neutralize each star's Core to prevent unstable Core's from killing innocent civillians. Core's obstacles, enemies and gravity will challenge you, with increasing difficulty at stars further from the Federation Base.</p>
    </a>
    <a class="card" href="revenge.html">
      <span class="tag">In development · v{RV_VER}</span>
      <h3>Telecrisis Revenge</h3>
      <p>An arena tactics RPG with timed strikes. The Federation's has implemented gladiatorial games to appease the masses, embark on a quest to reach the pinnacle of glory and see what truths will be uncovered.</p>
    </a>
  </div>
</section>

<section>
  <h2>Explore</h2>
  <div class="grid four">
    <a class="card" href="pilots.html"><span class="icon">✦</span><h3>8 pilots, 32 keystones</h3><p>Every pilot flies differently. Each run is unique and reward choices will dictate success.</p></a>
    <a class="card" href="classes.html"><span class="icon">⚔</span><h3>{len(RV["classes"])} gladiator classes</h3><p>Telecrisis Revenge: tanks, brawlers, snipers, medics and more, each with a passive, a signature move and a mastery to win.</p></a>
    <a class="card" href="gallery.html"><span class="icon">▣</span><h3>Screenshots</h3><p>Star fights and side quests from Chris; arenas, timed strikes and the team quarters from Revenge.</p></a>
    <a class="card" href="devlog.html"><span class="icon">✎</span><h3>Devlog</h3><p>What changed lately, build by build.</p></a>
    <a class="card" href="team.html"><span class="icon">☆</span><h3>The team</h3><p>Who makes it, who plays it first, and whose music and art it uses.</p></a>
  </div>
</section>

<section>
  <h2>Follow along</h2>
  <p class="muted">Play builds, wishlist, and catch the streams.</p>
  {link_btns()}
</section>
""")

# ---------------- chris ----------------
page("chris.html", "Telecrisis Chris · Awesome Squad",
     "Telecrisis Chris is a turn-based space roguelike: plan your flight, attack the Core, harvest energy, and survive the enemy and gravity phases.", f"""
<section class="hero">
  <div>
    <div class="kicker">In development · v1.0.2</div>
    <h1>Telecrisis <span>Chris</span></h1>
    <p class="lead">A tactical turn-based space roguelike rewarding skillful piloting and quick reflexes for bettter rewards. Every star has a harvestin Core. Plot your flight, swing through its attack window, and tear it down before the star's field, its defenders and its gravity tear you down first.</p>
    {link_btns()}
  </div>
  <img class="shot" src="img/shots/star-blue.jpg" alt="A Blue Giant star fight with fast flares and a fast asteroid field">
</section>

<section>
  <h2>How a turn works</h2>
  <p class="muted">Every turn runs the same six phases. You commit in PLAN, then watch it play out.</p>
  <ol class="loop">
    <li>PLAN<b>throttle, turn, power</b></li>
    <li>ACTION<b>drain, overload, patch…</b></li>
    <li>ATTACK<b>roll your dice</b></li>
    <li>HARVEST<b>mine energy</b></li>
    <li>ENEMY<b>they shoot back</b></li>
    <li>GRAVITY<b>the star pulls</b></li>
  </ol>
  <div class="grid four">
    <div class="card"><span class="icon">➶</span><h3>Momentum flight</h3><p>Your speed carries. Set throttle, turn and power, then EXECUTE. Turning hard at speed builds stress, and a planned move can't be taken back.</p></div>
    <div class="card"><span class="icon">◈</span><h3>Break the Core</h3><p>The Core orbits the star behind shields. Drain them with energy or shoot them down, then hit its hull from inside the attack window.</p></div>
    <div class="card"><span class="icon">⚡</span><h3>Energy is everything</h3><p>Harvest it from the field and spend it on upgrades, repairs, clearing stress and draining shields. Every spend is a trade.</p></div>
    <div class="card"><span class="icon">★</span><h3>Fly well, get paid</h3><p>Beat par, chain clean turns and hold the sweet spot for bonus rewards. Good piloting pays out.</p></div>
  </div>
</section>

<section>
  <h2>A run across the stars</h2>
  <div class="feature">
    <div>
      <p>Each run is a path across a star map with various stops along the way. A star fight, side quest, or transit stop to upgrade. Clear the path to the final Core.</p>
      <p>Between stars you visit the <strong>Garage</strong> for ship parts and the <strong>Pilot's Lounge</strong> for your pilot's keystone.</p>
      <p class="muted">Clear tiers to unlock new pilots, launch protocols and harder mutators.</p>
    </div>
    <img src="img/shots/star-map.jpg" alt="The star map: choose fleet skirmish, a star, transit or an Ace Hunt">
  </div>
  <table>
    <tr><th>Star</th><th>What to expect</th></tr>
    <tr><td>🌟 Yellow Star</td><td class="muted">Standard conditions. A fair fight.</td></tr>
    <tr><td>🔴 Red Dwarf</td><td class="muted">Dense field, slow flares.</td></tr>
    <tr><td>🔵 Blue Giant</td><td class="muted">Fast flares and a fast-spinning asteroid field.</td></tr>
    <tr><td>💫 Pulsar</td><td class="muted">Rapid flares and brutal gravity.</td></tr>
  </table>
</section>

<section>
  <h2>Side quests</h2>
  <p class="muted">Side quests are encountered as you travel between stars.</p>
  <div class="feature">
    <div><h3>⚔ Fleet Skirmish</h3><p>An ambush! Destroy or be destroyed.</p></div>
    <img src="img/shots/fleet.jpg" alt="Fleet Skirmish">
  </div>
  <div class="feature flip">
    <div><h3>☠ Ace Hunt</h3><p>An enemy ace and its escorts. Take on the challenge and show off superior piloting skills.</p></div>
    <img src="img/shots/ace.jpg" alt="Ace Hunt">
  </div>
  <div class="feature">
    <div><h3>⛟ Escort Convoy</h3><p>Keep a freighter alive until it reaches safety. Raiders want it, and it can only survive if you stay close.</p></div>
    <img src="img/shots/convoy.jpg" alt="Escort Convoy">
  </div>
  <div class="feature flip">
    <div><h3>◎ Wormhole Run</h3><p>A race down a collapsing corridor. Reach the critical point before the gravitaional collapse!</p></div>
    <img src="img/shots/wormhole.jpg" alt="Wormhole Run">
  </div>
</section>

<section>
  <h2>Ways to play</h2>
  <div class="grid">
    <div class="card"><h3>Solo runs</h3><p>The main campaign played alone.</p></div>
    <div class="card"><h3>Co-op</h3><p>The campaign, designed to be played cooperatively or with a bot.</p></div>
    <div class="card"><h3>PvP</h3><p>Pilot against pilot around a single star, with asteroids as cover.</p></div>
  </div>
</section>

<section>
  <h2>Pilots</h2>
  <p class="muted">Eight pilots, each with their own ship, stats and signature ability. <a href="pilots.html">Meet them all →</a></p>
</section>
""")

# ---------------- pilots ----------------
cards = []
for pid, name, col, role, ab, abtxt, hull, sh, dice, unlock in PILOTS:
    ks = "".join(f'<li><strong>{E(k["name"])}</strong> — {E(k["desc"])} <span class="small">Rank II: {E(k["r2"])}</span></li>'
                 for k in keystones[pid])
    un = f'<span class="unlock">{E(unlock)}</span>' if unlock else '<span class="unlock">Starter</span>'
    cards.append(f"""
  <article class="card pilot" style="--pc:{col}" id="{pid}">
    <div class="pilot-head"><img src="img/ships/{pid}.png" alt="{E(name)}'s ship"><div><h3>{E(name)}</h3><div class="role">{E(role)}</div></div>{un}</div>
    <ul class="stats"><li>Hull <b>{hull}</b></li><li>Shields <b>{sh}</b></li><li>Attack dice <b>{dice}</b></li></ul>
    <div class="ability"><strong>{E(ab)}:</strong> {E(abtxt)}</div>
    <div class="ks-title">Keystones · pick one per run</div>
    <ul class="ks">{ks}</ul>
  </article>""")
page("pilots.html", "Pilots · Telecrisis Chris",
     "The pilots of Telecrisis Chris and signature abilities/keystones.", f"""
<section>
  <div class="kicker">Telecrisis Chris</div>
  <h1>The <span>pilots</span></h1>
  <p class="lead">Four pilots are ready from the start. More join as you clear tiers. Each has a signature ability to leverage, four keystones/rule-bending upgrades, one per run, offered in the Pilot's Lounge. Rank II upgrades it, or take a second for fun.</p>
</section>
<section class="grid" style="grid-template-columns:repeat(auto-fit,minmax(min(100%,440px),1fr))">
{''.join(cards)}
</section>
<p class="ph">Keystones are new and still being balanced, so names and numbers may change.</p>
""")

# ---------------- revenge ----------------
RV_LINKS = [("Play in browser", ""), ("itch.io", "")]   # set a url to switch a button on

def rv_btns():
    out = ['<a class="btn primary" href="classes.html">Meet the classes</a>', '<a class="btn" href="gallery.html#revenge">Screenshots</a>']
    for name, url in RV_LINKS:
        if url:
            out.append(f'<a class="btn" href="{E(url)}" target="_blank" rel="noopener">{E(name)}</a>')
        else:
            out.append(f'<span class="btn off" title="Coming soon">{E(name)} <span class="soon">soon</span></span>')
    return '<div class="btns">' + "".join(out) + "</div>"

story = "".join(f'<div class="card"><h3>{E(c["title"])}</h3>' + "".join(f"<p>{E(t)}</p>" for t in c["text"] if t != "First, decide who each of them will be.") + "</div>"
                for c in RV["intro"])
circuits = "".join(f'<tr><td><strong>{E(a["name"])}</strong><br><span class="small muted">Outpost: {E(a["outpost"])}</span></td>'
                   f'<td class="muted">{E(a["desc"])}</td><td>{a["lo"]}–{a["hi"]}</td></tr>' for a in RV["areas"])
inputs = "".join(f'<li>{E(st["name"])}<b>{E(st["help"].split(".")[0])}</b></li>' for st in RV["styles"])
C = RV["counts"]
gear_total = C["weapons"] + C["armor"] + C["accessories"]

page("revenge.html", "Telecrisis Revenge · Awesome Squad",
     "Telecrisis Revenge is an arena tactics RPG with timed strikes: fight through the Federation's gladiatorial Games, circuit by circuit, to reach its leaders.", f"""
<section class="hero">
  <div>
    <div class="kicker">In development · v{RV_VER}</div>
    <h1>Telecrisis <span>Revenge</span></h1>
    <p class="lead">An arena tactics RPG where every hit is timed. The Federation keeps its people quiet with gladiatorial Games. The children of the pilots it locked away enter them, win their way up four circuits, and get close enough to the leaders to bring them down.</p>
    {rv_btns()}
  </div>
  <img class="shot" src="img/shots/rv-attack.jpg" alt="Savage lines up a Sweep Bar strike on a Federation Trooper">
</section>

<section>
  <h2>The story</h2>
  <div class="grid">{story}</div>
</section>

<section>
  <h2>How a match plays</h2>
  <p class="muted">Turn-based on a grid, in speed order. Positioning sets up the hit; your timing decides how hard it lands.</p>
  <ol class="loop">
    <li>PLACE<b>set your formation</b></li>
    <li>MOVE<b>height, flanks, cover</b></li>
    <li>STRIKE<b>time the input</b></li>
    <li>GUARD<b>parry their blows</b></li>
    <li>WIN<b>XP, gear, the crowd</b></li>
  </ol>
  <div class="grid four">
    <div class="card"><span class="icon">⏱</span><h3>Timed strikes</h3><p>Every weapon has its own input: sweep bars, chains, combos, lock-ons and more. Land a Critical for big damage; the timing is the same for every fighter, so skill matters, not stats.</p></div>
    <div class="card"><span class="icon">⛨</span><h3>Guard and parry</h3><p>On the enemy's turn you guard with your own timing. A perfect parry toward the attacker blocks it and counters. Officers feint, so wait for the real swing.</p></div>
    <div class="card"><span class="icon">⬢</span><h3>Position matters</h3><p>Side hits do +15%, back hits +30%. High ground helps. Fighters next to each other square up face to face, and walking away gives your opponent a parting strike.</p></div>
    <div class="card"><span class="icon">☄</span><h3>Arena rules</h3><p>Hold the zone, survive the rounds, take down the champion, win fast, or fight with no supplies. Shock plates, falling debris, oil fires, cover and overwatch change every map.</p></div>
  </div>
</section>

<section>
  <div class="feature">
    <div>
      <h2>Beat the <span>odds</span></h2>
      <p>Quick fighters can dodge a hit, but never a Critical. Land one on an enemy that was about to slip away and you get <strong>DODGE DENIED!</strong> as it's dragged back into the hit.</p>
      <p>The crowd is on the underdog's side. Fall behind and their cheers top up your team; pull ahead and they pay you in credits instead of making the fight easier.</p>
    </div>
    <img src="img/shots/rv-crit.jpg" alt="A Critical on the Sweep Bar">
  </div>
  <div class="feature flip">
    <div>
      <h3>Read the board before you commit</h3>
      <p>Orange outlines show what your chosen attack can reach, from where you stand or from any tile you hover. Click an enemy to see the damage preview, then click again to strike; you can still back out at the risk choice.</p>
      <p class="muted">Angled view shows the heights; press V for a flat, top-down board.</p>
    </div>
    <img src="img/shots/rv-battle.jpg" alt="An engaged pair, range outlines and the attack preview">
  </div>
  <div class="feature">
    <div>
      <h3>Guarding is a skill too</h3>
      <p>Every enemy strike runs its own meter. Guard to take less, parry toward the attacker to take nothing and hit back.</p>
    </div>
    <img src="img/shots/rv-guard.jpg" alt="Guarding an Officer's strike, with the parry direction shown">
  </div>
</section>

<section>
  <h2>The road to the Games</h2>
  <div class="feature">
    <div>
      <p>Four circuits stand between the team and the Federation's leaders. Each is a ladder of proving-ground bouts, cup matches and a story match, with two class trials that unlock a mastery for every fighter of that class.</p>
      <p>The circuit final is gated: clear the ladder first. The ladder alone leaves you a few levels short, so the circuit's Exhibition and the Open Arena are there to grind, and their wins can drop gear and arena-only rare finds.</p>
      <p class="muted">Finish the story and every circuit stays open, along with the Open Arena.</p>
    </div>
    <img src="img/shots/rv-map.jpg" alt="The sector map with the four circuits">
  </div>
  <table>
    <tr><th>Circuit</th><th>What it is</th><th>Enemy levels</th></tr>
    {circuits}
  </table>
</section>

<section>
  <h2>The team quarters</h2>
  <div class="feature flip">
    <div>
      <p>Between matches you run the team: hire recruits, spend training points, learn perks, and pick the party and the formation.</p>
      <p>The store sells <strong>{gear_total} pieces of gear</strong> across four Mk tiers that open circuit by circuit, plus {C["supplies"]} kinds of supplies. Mk gear arrives already upgraded, the store shows who each piece would improve, and spare gear sells back.</p>
      <p class="muted">{C["rares"]} rare finds, each with a catch, come from story matches, class trials and side bouts.</p>
    </div>
    <img src="img/shots/rv-store.jpg" alt="The store, with gear comparisons for the team">
  </div>
</section>

<section>
  <h2>{len(RV["styles"])} timed inputs</h2>
  <p class="muted">Each weapon and technique uses one. Practise any of them, with nothing at stake, in the Training Grounds.</p>
  <ol class="loop">{inputs}</ol>
  <div class="feature">
    <div>
      <h3>Training Grounds</h3>
      <p>Pick a drill, pick a risk (bigger window or bigger payoff), and keep a tally of your Criticals and best streak.</p>
    </div>
    <img src="img/shots/rv-training.jpg" alt="The Training Grounds: the Lock-On drill">
  </div>
</section>

<section>
  <h2>Your game, your way</h2>
  <div class="grid">
    <div class="card"><h3>Story / Standard / Hard</h3><p>Enemy strength you can switch at any time. Standard is tuned so an average player loses now and then.</p></div>
    <div class="card"><h3>Relaxed timing</h3><p>Bigger zones and more time on every input, for anyone who wants the tactics without the pressure.</p></div>
    <div class="card"><h3>Open Arena</h3><p>Free-play bouts against opponents at your level. Pick the arena, the odds and the team size.</p></div>
  </div>
</section>

<section>
  <h2>Classes</h2>
  <p class="muted">{len(RV["classes"])} classes, each with a weight, a passive, a signature technique and a mastery. <a href="classes.html">Meet them all →</a></p>
</section>
""", image="img/shots/rv-attack.jpg")

# ---------------- classes ----------------
WEIGHT_COL = {"heavy": "#ff4d5e", "medium": "#f2c14e", "light": "#3fd6ff"}
ccards = []
for c in RV["classes"]:
    col = WEIGHT_COL.get(c["weight"], "#b46cff")
    weapons = ", ".join(w.capitalize() for w in c["weapons"])
    dodge = f'{round(c["dodge"] * 100)}%' if c["dodge"] else "none"
    ccards.append(f"""
  <article class="card pilot" style="--pc:{col}" id="{c["id"]}">
    <div class="pilot-head"><div><h3>{E(c["name"])}</h3><div class="role">{E(c["role"])} · {E(c["weight"].capitalize())}</div></div><span class="unlock">{E(weapons)}</span></div>
    <p>{E(c["desc"])}</p>
    <ul class="stats"><li>HP <b>{c["hp"]}</b></li><li>Attack <b>{c["atk"]}</b></li><li>Defense <b>{c["def"]}</b></li><li>Speed <b>{c["spd"]}</b></li><li>Move <b>{c["move"]}</b></li><li>Dodge <b>{dodge}</b></li></ul>
    <div class="ability"><strong>{E(c["passive_name"])}:</strong> {E(c["passive_desc"])}</div>
    <div class="ks-title">Signature · {c["signature_cost"]} energy</div>
    <ul class="ks"><li><strong>{E(c["signature"])}</strong> — {E(c["signature_desc"].rstrip("."))}.</li></ul>
    <div class="ks-title" style="margin-top:12px">Mastery</div>
    <ul class="ks"><li><strong>{E(c["mastery"])}</strong> — {E(c["mastery_desc"].rstrip("."))}. <span class="small">Won in {E(c["trial"])}.</span></li></ul>
  </article>""")
page("classes.html", "Classes · Telecrisis Revenge",
     "The gladiator classes of Telecrisis Revenge: stats, passives, signature techniques and masteries.", f"""
<section>
  <div class="kicker">Telecrisis Revenge</div>
  <h1>The <span>classes</span></h1>
  <p class="lead">Build a team of up to six. Weight sets armor, speed and matchups: heavy beats medium, medium beats light, light beats heavy. Each class has a passive, a signature technique and a mastery won in its class trial that upgrades every fighter of that class.</p>
</section>
<section class="grid" style="grid-template-columns:repeat(auto-fit,minmax(min(100%,440px),1fr))">
{''.join(ccards)}
</section>
<p class="ph">Telecrisis Revenge is in development, so classes and numbers may change. Stats shown are at level 1, before training and gear.</p>
""", image="img/shots/rv-quarters.jpg")

# ---------------- gallery ----------------
SHOTS = [("star-yellow", "Yellow Star: lining up on the Void Core"),
         ("star-blue", "Blue Giant: fast flares, fast field"),
         ("star-map", "The star map: pick your path"),
         ("fleet", "Fleet Skirmish"),
         ("ace", "Ace Hunt"),
         ("convoy", "Escort Convoy"),
         ("wormhole", "Wormhole Run")]
RV_SHOTS = [("rv-attack", "Lining up a Sweep Bar strike"),
            ("rv-crit", "A Critical lands"),
            ("rv-guard", "Guarding an Officer's strike: parry toward the attacker"),
            ("rv-battle", "Squared up: range outlines and the attack preview"),
            ("rv-placement", "Placing the team before a cup match"),
            ("rv-flat", "Flat view on the Refinery Floor"),
            ("rv-map", "The sector map: four circuits"),
            ("rv-quarters", "Team quarters: classes, training and gear"),
            ("rv-store", "The store, with gear comparisons"),
            ("rv-briefing", "Match briefing: rules, rewards and the line-up"),
            ("rv-training", "Training Grounds: the Lock-On drill"),
            ("rv-title", "Title screen")]
def figs_of(shots):
    return "".join(f'<figure><a href="img/shots/{s}.jpg" data-cap="{E(c)}"><img src="img/shots/{s}-sm.jpg" alt="{E(c)}" loading="lazy"></a><figcaption>{E(c)}</figcaption></figure>' for s, c in shots)
figs = figs_of(SHOTS)
rv_figs = figs_of(RV_SHOTS)
lb = """<div class="lightbox" id="lb" role="dialog" aria-modal="true"><button aria-label="Close">✕</button><img alt=""><p></p></div>
<script>
const lb=document.getElementById('lb'),li=lb.querySelector('img'),lp=lb.querySelector('p');
const items=[...document.querySelectorAll('.gallery a')];let cur=0;
function show(i){cur=(i+items.length)%items.length;li.src=items[cur].href;lp.textContent=items[cur].dataset.cap;lb.classList.add('open');}
items.forEach((a,i)=>a.addEventListener('click',e=>{e.preventDefault();show(i);}));
lb.addEventListener('click',e=>{if(e.target!==li)lb.classList.remove('open');});
document.addEventListener('keydown',e=>{if(!lb.classList.contains('open'))return;
 if(e.key==='Escape')lb.classList.remove('open');if(e.key==='ArrowRight')show(cur+1);if(e.key==='ArrowLeft')show(cur-1);});
</script>"""
page("gallery.html", "Screenshots · Awesome Squad",
     "Screenshots of the Telecrisis games: Telecrisis Chris star fights and side quests, Telecrisis Revenge arena matches and the team quarters.", f"""
<section>
  <div class="kicker">Awesome Squad</div>
  <h1><span>Screenshots</span></h1>
  <p class="lead">From the current development builds. Click a shot to see it full size.</p>
  <div class="btns"><a class="btn" href="#chris">Telecrisis Chris</a><a class="btn" href="#revenge">Telecrisis Revenge</a></div>
</section>
<section id="chris">
  <h2>Telecrisis <span>Chris</span></h2>
  <div class="gallery">{figs}</div>
</section>
<section id="revenge">
  <h2>Telecrisis <span>Revenge</span> <span class="small muted">v{RV_VER}</span></h2>
  <div class="gallery">{rv_figs}</div>
</section>
""", lb)

# ---------------- devlog ----------------
page("devlog.html", "Devlog · Awesome Squad",
     "What's new in Telecrisis Chris and Telecrisis Revenge, build by build.", """
<section>
  <div class="kicker">Awesome Squad</div>
  <h1><span>Devlog</span></h1>
  <p class="lead">What changed lately, newest first.</p>
  <div class="btns"><a class="btn" href="#revenge">Telecrisis Revenge</a><a class="btn" href="#chris">Telecrisis Chris</a></div>
</section>

<section id="revenge">
  <h2>Telecrisis <span>Revenge</span></h2>

  <article class="card post">
    <div class="date">November 24, 2026 · v0.16.1</div>
    <h3>Know what you're being asked</h3>
    <ul>
      <li><strong>Meet your rival:</strong> before the first match, Kass Vantor of the Vantor Academy turns up at the dock to size up your team. He spars with you so you can learn the attack bar and the guard (with parries) at your own pace, then promises to be waiting in every circuit.</li>
      <li><strong>Every new bar is explained:</strong> the first time an input comes up in a match (a new attack style, a feint, a delayed strike, a combo), the game pauses to show what it's asking and how each result is earned. You can try it as many times as you like, and the match only carries on when you press Continue. The aim is understanding, not twitch reflexes. You can turn this off in Options.</li>
      <li><strong>Always know where to go:</strong> an Up Next bar on the ship and the map shows the next match, where it is, and your circuit progress. The next planet is marked on the map, the victory screen offers a Next Match button, and winning a match moves you on instead of leaving you on the one you just won.</li>
    </ul>
  </article>

  <article class="card post">
    <div class="date">November 21, 2026 · v0.16.0</div>
    <h3>Into the black</h3>
    <ul>
      <li><strong>Space first:</strong> the coliseum is now the Crown Ring, an orbital arena station with broadcast screens and camera drones. Fights take place on deck plating among cargo crates, and the menus share Telecrisis Chris's colours, riveted panels and cockpit glass.</li>
      <li><strong>New look for the team:</strong> your fighters are frontier spacers in mismatched salvaged armour, some in visored helmets and some bare-faced. The Federation guard wear matching polished armour.</li>
      <li><strong>Hype replaces the crowd:</strong> every match is broadcast and viewers root for the underdog. Sponsors drop Medi-Gel when Hype fills, and two commentators call the action in the battle log.</li>
      <li><strong>The Long Shot:</strong> your team lives aboard its own ship. The first trip to each new circuit is a voyage with two stops (a drifting freighter, a distress beacon, a Federation checkpoint and more), and every choice spells out exactly what it costs and gives.</li>
      <li><strong>Recovered flight logs:</strong> dig the pilots' buried recordings out of the Federation's archives as you climb, and piece together what they found past the edge of the charts.</li>
      <li><strong>Station hazards:</strong> airlock blasts push rows of fighters sideways, hull breaches drag people toward holes in the deck, and solar flares punish anyone caught in the open. Every hazard is marked a round ahead.</li>
      <li><strong>Fixes:</strong> visible scroll bars, even-sized stat buttons, a clearer skill points label, and a shock plate legend.</li>
    </ul>
  </article>

  <article class="card post">
    <div class="date">November 20, 2026 · v0.15.0</div>
    <h3>Real training, and a Federation that learns</h3>
    <ul>
      <li><strong>New stats:</strong> Melee and Ranged Power, Melee and Ranged Defense, Instinct, Ferocity, Guard and Showmanship. Each unlocks perks at 6, 12 and 18 points, so stacking one stat means falling behind in others.</li>
      <li><strong>Your inputs decide the outcome:</strong> no stat, perk or item changes a timing bar or rolls dice over your result. Instinct now builds a Hot Streak from Criticals in a row, and defensive bonuses make your guards stronger instead of adding dodge chance.</li>
      <li><strong>Level cap 50:</strong> each circuit takes your team about 10 levels. Every 5 levels pick a feat (like Reckless or Pack Tactics) or a stat boost, at level 10 choose one of two specializations for your class, and at 30 it turns Elite. A new row of the skill tree opens each circuit.</li>
      <li><strong>New moves:</strong> charges, vaults, harpoon pulls, position swaps, line, cone and burst attacks, and crowd plays like Showboat and the Grand Finale.</li>
      <li><strong>Federation drills:</strong> as the circuits go on, enemies learn combos, delayed strikes and plated armor, and their squads start focusing fire, escorting and pincering. Every one is shown on the enemy's card and is the same every time, so you can learn it. No hidden difficulty boosts: later circuits ask more of your timing and tactics.</li>
      <li><strong>Steadier pacing:</strong> the four circuits take about the same time, the early walls are smoothed out, and a team left short by an entry rule faces fewer opponents.</li>
    </ul>
  </article>

  <article class="card post">
    <div class="date">November 19, 2026 · v0.14.0</div>
    <h3>Star maps, skill trees and eight new ways to hit</h3>
    <ul>
      <li><strong>A map of the circuits:</strong> each circuit is now a star system you travel around. Arena worlds hold the ladder, the seat of power holds the story match and final, and there are trial grounds, the pits for side bouts, Vantor Academy's outpost, and your home station. Each place has its own shop stock, local recruits, a veteran for hire, and conditions like low gravity, dust storms or a roaring crowd.</li>
      <li><strong>Off the map:</strong> every circuit hides a location you have to earn your way into, with contraband gear and a class you can't get anywhere else. Four in all.</li>
      <li><strong>Skill trees:</strong> fighters earn a skill point every level and spend it in their class's tree: three branches of new attacks and passives, each ending in a capstone, and a fighter can only take one. Two fighters of the same class can play nothing alike. Retrain at the home station.</li>
      <li><strong>Eight new attack inputs:</strong> Feint, Push Your Luck, Pendulum, Lead the Target, Dual Wield, Cook the Fuse, Tug of War and Path Trace, all in the Training Grounds.</li>
      <li><strong>Fairer counters:</strong> a perfect parry only hits back if your weapon can reach the attacker (or you've learned Deflect), and duo follow-ups need the partner in reach of the target.</li>
      <li><strong>A bigger board</strong> (16 by 10), so fights open with a bit of maneuvering instead of instant contact.</li>
      <li><strong>Fits your screen:</strong> 16:10 screens like the Steam Deck and ultrawide monitors now use the whole display, small text is bigger, and there's a Text size option. A <strong>Next match</strong> button jumps straight to your next fight.</li>
      <li><strong>38 achievements</strong> now, including finding the hidden places.</li>
    </ul>
  </article>

  <article class="card post">
    <div class="date">November 18, 2026 · v0.13.0</div>
    <h3>No two matches alike</h3>
    <ul>
      <li><strong>Choose your path:</strong> each circuit now opens three matches at a time and one more with every win. The final needs the story match and most of the ladder, not every bout.</li>
      <li><strong>Start patterns:</strong> head-on, switched ends, corner to corner, pincer, split team, broadside, and crossfire for the story fights. Every attempt rolls a new one, and the briefing map shows it.</li>
      <li><strong>Entry rules:</strong> lightweights only, no guns, one of each class, bring a tank and more, on optional matches and side bouts. Your whole roster and your gear choices matter now.</li>
      <li><strong>A side-bout board</strong> of three generated bouts per circuit, from 1v1 duels to full squads, redrawn after every match.</li>
      <li><strong>Smarter Federation:</strong> four difficulties. On Standard and Hard, enemies flank, gang up on the wounded, go for knockouts and fall back when hurt.</li>
      <li><strong>Bonus objectives and medals</strong> (win fast, nobody knocked out, no supplies and more), <strong>injuries</strong> that sit knocked-out fighters out for a match, and <strong>challenge modifiers</strong> that make every match harder for more credits and XP.</li>
      <li><strong>Vantor Academy,</strong> the Federation's own gladiator school, turns up twice a circuit with named fighters, a grudge and trophies to win.</li>
      <li><strong>35 achievements,</strong> ready for Steam.</li>
    </ul>
  </article>

  <article class="card post">
    <div class="date">November 17, 2026 · v0.12.0</div>
    <h3>The Games go pocket-sized</h3>
    <ul>
      <li><strong>Play on your phone:</strong> open the game in your phone's browser, turn it sideways, and it switches to a phone layout with bigger buttons and text. Add it to your home screen and it opens full screen like an app, updating itself when a new build is out.</li>
      <li><strong>Touch controls for every timed input:</strong> an on-screen pad appears only when a meter needs it: a direction pad, a big Tap / Hold / Mash button, and left and right buttons for Alternating Mash. Lock-On works like a trackpad: drag anywhere and the crosshair follows, so your finger never covers the target.</li>
      <li><strong>Timing that keeps up:</strong> every press is now judged at the moment your finger landed, not when the game got round to it. A new <strong>Timing check</strong> in Options has you tap along to a beat and adjusts for your screen's delay.</li>
      <li><strong>Battle on a small screen:</strong> Fighter / Info / Log tabs, tap any unit to inspect it, tap a tile twice to move, and tap any attack or supply to see what it does (and, if it's locked, why).</li>
      <li><strong>Finger scrolling</strong> for every list, the Team, Store and Records tabs as swipe strips, and option rows that grow to fit their text.</li>
    </ul>
  </article>

  <article class="card post">
    <div class="date">November 16, 2026 · v0.11.0</div>
    <h3>Engagement, dodging and a harder Federation</h3>
    <ul>
      <li><strong>Squaring up:</strong> fighters next to each other face off. An engaged fighter keeps facing its opponent, so its allies can be flanked, and walking away gives the opponent a parting strike. Light fighters slip away free.</li>
      <li><strong>Dodging by class:</strong> quick fighters dodge some hits, but never a Critical. Land one on a dodge and it's <strong>DODGE DENIED!</strong></li>
      <li><strong>Story / Standard / Hard</strong> enemy strength, a tougher baseline, and harder circuit finals and story matches, tuned with a campaign simulator.</li>
      <li><strong>Side bouts that matter:</strong> the ladder leaves you a few levels short of each final. Exhibitions and the Open Arena pay full XP and can drop gear and four new arena-only rare finds.</li>
      <li><strong>Gear:</strong> a Mk tier of gear for every circuit (77 pieces in all), rare finds from story matches and trials, selling, gear comparison in the store, and three new supplies.</li>
      <li><strong>No more misclicks:</strong> place your fighters before each match, see every attack's range, and confirm both the target and the risk choice. You can back out and get your energy back.</li>
      <li><strong>Defense rework:</strong> Defense now scales with the attacker's level, so armor and training matter all the way to level 80.</li>
    </ul>
  </article>

  <article class="card post">
    <div class="date">November 15, 2026 · v0.10.0</div>
    <h3>The Games open</h3>
    <ul>
      <li><strong>The campaign:</strong> four circuits of proving grounds, cup matches, story matches and class trials, each ending in a gated final. The level cap is 99.</li>
      <li><strong>Sixteen timed inputs</strong>, from Sweep Bars to Lock-Ons, and the Training Grounds to practise them.</li>
      <li><strong>Match rules and hazards:</strong> hold the zone, survive, champions, blitz and iron rules; shock plates, debris, oil fires, cover and overwatch.</li>
      <li><strong>A crowd that backs the underdog.</strong></li>
      <li><strong>The space-coliseum look:</strong> gladiator figures, an angled board that shows height, and a new arena backdrop.</li>
    </ul>
  </article>
</section>

<section id="chris">
  <h2>Telecrisis <span>Chris</span></h2>

  <article class="card post">
    <div class="date">November 2026 · in progress</div>
    <h3>Keystones, round boards and a convoy with teeth</h3>
    <ul>
      <li><strong>Pilot keystones:</strong> every pilot has four rule-bending keystones. Pick one per run in the Pilot's Lounge, and a status line shows when it's ready or has just fired.</li>
      <li><strong>Round boards everywhere:</strong> every star and side quest (except the Wormhole corridor) now plays on a circular board with a bigger edge.</li>
      <li><strong>Escort Convoy</strong> got sharper: raiders now go for the freighter, and it needs you close to survive.</li>
      <li><strong>Ace Hunt</strong> pays double, and the ace's escorts give you a turn to react before they open fire.</li>
      <li><strong>Salvo</strong> flies faster with a bigger blast, and the arming point is marked on the warning line.</li>
      <li><strong>One console layout</strong> across star fights, side quests and PvP, with a mission card for each side quest.</li>
      <li>Side-quest energy is now banked for your next stop. Turrets can't spawn right on top of you.</li>
    </ul>
  </article>

  <article class="card post">
    <div class="date">November 2, 2026 · v1.0.2</div>
    <h3>Lounge abilities and a cleaner cockpit</h3>
    <ul>
      <li><strong>40 new Lounge abilities</strong> mixed into the normal draw.</li>
      <li><strong>Core momentum</strong> is visible, with x2, x3 and x4 damage multipliers.</li>
      <li><strong>Star recap</strong> shows the Core, your bounty and which abilities fired.</li>
      <li><strong>Run variety:</strong> a smaller Garage with rarity, and a launch protocol to pick each run.</li>
      <li><strong>Menus and console:</strong> one layout in every mode, no scrolling menus, and a controller pass.</li>
      <li><strong>Salvo</strong> flies faster and checks its whole flight path for hits.</li>
    </ul>
  </article>

  <article class="card post">
    <div class="date">October 26, 2026 · v1.0.1</div>
    <h3>A real first run</h3>
    <ul>
      <li><strong>New onboarding:</strong> tier 0 is a guided hunt (beacon, first shot, unlock banners, payoff), and you can skip it.</li>
      <li><strong>Progression:</strong> new pilots join as you clear tiers, and the run-end screen shows what unlocks next.</li>
      <li><strong>The Core:</strong> shots now chip its shields too, while DRAIN stays the fast way through.</li>
      <li><strong>Readability:</strong> text scales with your screen (Steam Deck included), and the console and side panels were reworked.</li>
    </ul>
  </article>
</section>
""")

# ---------------- team ----------------
page("team.html", "Team · Awesome Squad",
     "The people behind Telecrisis, plus music, art and sound credits.", """
<section>
  <div class="kicker">Awesome Squad</div>
  <h1>The <span>team</span></h1>
  <p class="lead">Friends and family who have supported my endeavors.</p>
  <div class="grid credits">
    <div class="card">
      <h3>Design &amp; direction</h3>
      <ul>
        <li>Ted Savage<span>Design, direction, and character concepts</span></li>
        <li>Steve L<span>Design contributions</span></li>
      </ul>
    </div>
    <div class="card">
      <h3>Music</h3>
      <ul>
        <li>Peter S<span>Menu theme</span></li>
        <li>Kevin MacLeod (<a href="https://incompetech.com" target="_blank" rel="noopener">incompetech.com</a>)<span>Star, side-quest, shop and credits themes. Licensed under <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener">CC BY 4.0</a>.</span></li>
      </ul>
    </div>
    <div class="card">
      <h3>Art</h3>
      <ul>
        <li>Artist to be announced<span>Character &amp; key art</span></li>
        <li>Kenney (<a href="https://kenney.nl" target="_blank" rel="noopener">kenney.nl</a>)<span>Placeholder ship, enemy, space, effect and UI sprites (CC0)</span></li>
      </ul>
    </div>
    <div class="card">
      <h3>Sound effects</h3>
      <ul>
        <li>From <a href="https://pixabay.com" target="_blank" rel="noopener">Pixabay</a><span>DRAGON-STUDIO, Joe_Bou_Khalil, SoundReality, Leszek_Szary, BenVibrant</span></li>
      </ul>
    </div>
    <div class="card">
      <h3>Code</h3>
      <ul>
        <li>Claude (Anthropic)<span>Code implementation, under Ted Savage's design and direction</span></li>
      </ul>
    </div>
    <div class="card">
      <h3>Playtesters</h3>
      <ul>
        <li>Steve L</li><li>Kevin L</li><li>Stephanie W</li><li>Peter S</li><li>Will S</li>
        <li>Anthony F</li>
      </ul>
    </div>
    <div class="card">
      <h3>Telecrisis Revenge</h3>
      <ul>
        <li>Ted Savage<span>Game design, story and direction</span></li>
        <li>Claude (Anthropic)<span>Code, under Ted Savage's design and direction</span></li>
        <li>Art and audio<span>Gladiator figures and arenas are drawn in code for now; sound effects are generated placeholders</span></li>
      </ul>
    </div>
    <div class="card">
      <h3>Built with</h3>
      <ul>
        <li><a href="https://godotengine.org" target="_blank" rel="noopener">Godot Engine 4.6</a><span>MIT License</span></li>
        <li>Noto fonts (Google)<span>SIL Open Font License 1.1</span></li>
      </ul>
    </div>
  </div>
</section>
""")
print("ok", {k: len(v) for k, v in keystones.items()})

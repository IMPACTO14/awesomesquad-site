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
     "Firing Solution", "+1 attack die per turn within 240px of your target. At +2 or more, Evade refills to the solution minus 1.", 8, 3, 3, None),
    ("peter", "SpooderMoon", "#FF8811", "Precision alignment and speed.",
     "Precision Lock", "With velocity and facing within 30° of each other, attacks hit on 8+.", 10, 4, 2, None),
    ("cara", "LSP", "#E050E0", "Slow and steady. Surplus shields become harvest power.",
     "Harvest Conversion", "Each shield above max is +1 harvest die. Overload costs 2 energy.", 14, 7, 1, None),
    ("steven", "Axemodeus", "#1AD9D9", "Cool and calculated.",
     "Calculated Strike", "Hitting on consecutive turns from the same arc zone grants +1 die (max 3). Resets when you switch arcs.", 10, 5, 2, "Unlocks with progress"),
    ("covert", "Cobra", "#F2BF1A", "Gutsy and tricky.",
     "Rule Bender", "May fire outside the attack arc once per turn; misses deal 1 self damage.", 9, 4, 3, "Unlocks with progress"),
    ("kevin", "BlueJello", "#80E64D", "Methodical researcher. Gets more efficient the longer the fight runs.",
     "Prior Research", "+1 harvest die on turn 5, +2 on turn 10, +3 on turn 15. Overload gets cheaper as the star goes on.", 11, 6, 2, "Unlocks with progress"),
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
    open(os.path.join(OUT, fname), "w", encoding="utf-8").write(doc)

# ---------------- index ----------------
page("index.html", "Awesome Squad · The Telecrisis games",
     "Awesome Squad: home of the Telecrisis games: the space roguelike Telecrisis Chris and the arena tactics RPG Telecrisis Revenge.", f"""
<section class="hero">
  <div>
    <div class="kicker">Awesome Squad</div>
    <h1>The <span>Telecrisis</span> games</h1>
    <p class="lead">Tactical space games built by Ted and friends. Plan your move, commit to it, and live with what the void throws back.</p>
    <div class="btns">
      <a class="btn primary" href="chris.html">Meet Telecrisis Chris</a>
      <a class="btn primary" href="revenge.html">Meet Telecrisis Revenge</a>
      <a class="btn" href="gallery.html">See screenshots</a>
    </div>
  </div>
  <a href="gallery.html"><img class="shot" src="img/shots/star-yellow.jpg" alt="Telecrisis Chris: a pilot lines up on the Void Core around a yellow star"></a>
</section>

<section>
  <h2>The games</h2>
  <div class="grid">
    <a class="card" href="chris.html">
      <span class="tag">In development · v1.0.2</span>
      <h3>Telecrisis Chris</h3>
      <p>A turn-based space roguelike. Pick a pilot, chart a run across the stars, and break each star's Void Core while asteroids, sentinels and gravity work against you.</p>
    </a>
    <a class="card" href="revenge.html">
      <span class="tag">In development · v{RV_VER}</span>
      <h3>Telecrisis Revenge</h3>
      <p>An arena tactics RPG with timed strikes. The children of the Federation's imprisoned pilots fight their way through its gladiatorial Games to reach the four leaders, and bring them down.</p>
    </a>
  </div>
</section>

<section>
  <h2>Explore</h2>
  <div class="grid four">
    <a class="card" href="pilots.html"><span class="icon">✦</span><h3>8 pilots, 32 keystones</h3><p>Every pilot flies differently. Each run you can pick one keystone that bends the rules around their style.</p></a>
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
     "Telecrisis Chris is a turn-based space roguelike: plan your flight, attack the Void Core, harvest energy, and survive the enemy and gravity phases.", f"""
<section class="hero">
  <div>
    <div class="kicker">In development · v1.0.2</div>
    <h1>Telecrisis <span>Chris</span></h1>
    <p class="lead">A turn-based space roguelike about momentum. Every star hides a Void Core. Plot your flight, swing through its attack window, and tear it down before the star's field, its defenders and its gravity tear you down first.</p>
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
    <div class="card"><span class="icon">◈</span><h3>Break the Void Core</h3><p>The Core orbits the star behind shields. Drain them with energy or shoot them down, then hit its hull from inside the attack window.</p></div>
    <div class="card"><span class="icon">⚡</span><h3>Energy is everything</h3><p>Harvest it from the field and spend it on upgrades, repairs, clearing stress and draining shields. Every spend is a trade.</p></div>
    <div class="card"><span class="icon">★</span><h3>Fly well, get paid</h3><p>Beat par, chain clean turns and hold the sweet spot for bonus rewards. Good piloting pays out.</p></div>
  </div>
</section>

<section>
  <h2>A run across the stars</h2>
  <div class="feature">
    <div>
      <p>Each run is a path across a star map. Pick your next node: a star fight, a side quest, or a transit stop to upgrade. Clear the path to the final Core.</p>
      <p>Between stars you visit the <strong>Garage</strong> for ship parts and the <strong>Pilot's Lounge</strong> for new abilities and your pilot's keystone.</p>
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
  <p class="muted">Not every node is a Core fight.</p>
  <div class="feature">
    <div><h3>⚔ Fleet Skirmish</h3><p>A squad of sentinels and nothing else. Destroy every ship.</p></div>
    <img src="img/shots/fleet.jpg" alt="Fleet Skirmish">
  </div>
  <div class="feature flip">
    <div><h3>☠ Ace Hunt</h3><p>An enemy ace and its escorts. Bring the ace down. Volatile rocks near it can blast it too.</p></div>
    <img src="img/shots/ace.jpg" alt="Ace Hunt">
  </div>
  <div class="feature">
    <div><h3>⛟ Escort Convoy</h3><p>Keep a freighter alive until it reaches safety. Raiders want it, and it can only survive if you stay close.</p></div>
    <img src="img/shots/convoy.jpg" alt="Escort Convoy">
  </div>
  <div class="feature flip">
    <div><h3>◎ Wormhole Run</h3><p>A race down a collapsing corridor. Reach the finish line before the wall behind you catches up.</p></div>
    <img src="img/shots/wormhole.jpg" alt="Wormhole Run">
  </div>
</section>

<section>
  <h2>Ways to play</h2>
  <div class="grid">
    <div class="card"><h3>Solo runs</h3><p>The full roguelike: one pilot, one ship, one run across the stars.</p></div>
    <div class="card"><h3>Co-op</h3><p>Two pilots, one run.</p></div>
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
     "The eight pilots of Telecrisis Chris, their ships, signature abilities and keystones.", f"""
<section>
  <div class="kicker">Telecrisis Chris</div>
  <h1>The <span>pilots</span></h1>
  <p class="lead">Four pilots are ready from the start. Four more join as you clear tiers. Each has a signature ability, and four keystones: rule-bending upgrades, one per run, offered in the Pilot's Lounge. Rank II upgrades it.</p>
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
     "The people behind the Telecrisis games, plus music, art and sound credits.", """
<section>
  <div class="kicker">Awesome Squad</div>
  <h1>The <span>team</span></h1>
  <p class="lead">A small crew of friends and family making the games we want to play.</p>
  <div class="grid credits">
    <div class="card">
      <h3>Design &amp; direction</h3>
      <ul>
        <li>Ted Savage<span>Game design, creative direction, pilot character concepts</span></li>
        <li>Steven LaBarge<span>Design contributions</span></li>
      </ul>
    </div>
    <div class="card">
      <h3>Music</h3>
      <ul>
        <li>Peter Savage<span>Menu theme</span></li>
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
        <li>Steven LaBarge</li><li>Kevin Larsen</li><li>Stephanie Weber</li><li>Peter Savage</li><li>Will Savage</li>
        <li>Anthony Fontana<span>Came up with onboarding through gameplay progression</span></li>
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

from flask import Flask, request, redirect, session, make_response
import sqlite3
import urllib.parse

app = Flask(__name__)
app.secret_key = "weaksecret"

TITLE = "0xDay CTF"
SUBTITLE = "Web Exploitation CTF Round"
S1_FLAG = "IEEE{5t4g3_01_4u7h_Byp455}"
S2_FLAG = "IEEE{5t4g3_02_4cc355_C0n7r0l}"
S3_FLAG = "IEEE{5t4g3_03_5QL1_Ch41n}"
S4_FLAG = "IEEE{5t4g3_04_H34d3r_C00k13_4bu53}"
S5_FLAG = "IEEE{Ph453_01_C0mpl373d_M4573r}"

# =============================
# DB INIT
# =============================

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)")
    c.execute("DELETE FROM users")
    c.execute("INSERT INTO users (username,password,role) VALUES ('admin','S3cr3t!','admin')")
    c.execute("INSERT INTO users (username,password,role) VALUES ('guest','guest123','user')")
    conn.commit(); conn.close()

# =============================
# UI COMPONENTS
# =============================

GLOBAL_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&family=VT323&display=swap');

  :root {
    --bg:        #050a05;
    --bg2:       #0a120a;
    --bg3:       #0f1a0f;
    --border:    #1aff6a33;
    --border2:   #1aff6a88;
    --green:     #1aff6a;
    --green-dim: #0d8c3a;
    --green-glow:#1aff6a44;
    --amber:     #ffb800;
    --red:       #ff3c3c;
    --blue:      #00d4ff;
    --text:      #a8ffb8;
    --text-dim:  #4a7a5a;
    --text-mute: #2a4a35;
    --flag:      #ffb800;
  }

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Share Tech Mono', monospace;
    min-height: 100vh;
    overflow-x: hidden;
    position: relative;
  }

  /* Scanline overlay */
  body::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(0,0,0,0.08) 2px,
      rgba(0,0,0,0.08) 4px
    );
    pointer-events: none;
    z-index: 9999;
  }

  /* Matrix rain bg effect via CSS */
  body::after {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background:
      radial-gradient(ellipse at 20% 50%, #0d3d1a22 0%, transparent 50%),
      radial-gradient(ellipse at 80% 20%, #0a2d1522 0%, transparent 40%);
    pointer-events: none;
    z-index: 0;
  }

  /* ---- HEADER ---- */
  .site-header {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    position: relative;
    z-index: 10;
    border-bottom: 1px solid var(--border);
  }

  .site-header .logo {
    font-family: 'Orbitron', monospace;
    font-weight: 900;
    font-size: clamp(2rem, 6vw, 3.8rem);
    color: var(--green);
    letter-spacing: 0.12em;
    text-shadow: 0 0 30px var(--green-glow), 0 0 60px var(--green-glow);
    animation: flicker 8s infinite;
  }

  .site-header .logo span { color: var(--amber); }

  .site-header .subtitle {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.85rem;
    color: var(--text-dim);
    letter-spacing: 0.3em;
    text-transform: uppercase;
    margin-top: 0.4rem;
  }

  .site-header .tagline {
    font-size: 0.7rem;
    color: var(--text-mute);
    margin-top: 0.6rem;
    letter-spacing: 0.2em;
  }

  /* ---- NAV ---- */
  .top-nav {
    display: flex;
    justify-content: center;
    gap: 2rem;
    padding: 0.8rem 1rem;
    border-bottom: 1px solid var(--border);
    background: var(--bg2);
    position: relative;
    z-index: 10;
  }

  .top-nav a {
    color: var(--text-dim);
    text-decoration: none;
    font-size: 0.75rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    transition: color 0.2s;
    padding: 0.3rem 0.6rem;
    border: 1px solid transparent;
  }

  .top-nav a:hover {
    color: var(--green);
    border-color: var(--green-dim);
  }

  /* ---- MAIN LAYOUT ---- */
  .wrapper {
    max-width: 780px;
    margin: 0 auto;
    padding: 2.5rem 1.5rem;
    position: relative;
    z-index: 10;
  }

  /* ---- STAGE CARD ---- */
  .card {
    background: var(--bg2);
    border: 1px solid var(--border2);
    border-radius: 2px;
    padding: 2rem 2.5rem;
    position: relative;
    overflow: hidden;
  }

  .card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 3px;
    background: linear-gradient(90deg, transparent, var(--green), transparent);
  }

  .card-corner {
    position: absolute;
    width: 12px; height: 12px;
    border-color: var(--green);
    border-style: solid;
  }
  .card-corner.tl { top: 8px; left: 8px; border-width: 2px 0 0 2px; }
  .card-corner.tr { top: 8px; right: 8px; border-width: 2px 2px 0 0; }
  .card-corner.bl { bottom: 8px; left: 8px; border-width: 0 0 2px 2px; }
  .card-corner.br { bottom: 8px; right: 8px; border-width: 0 2px 2px 0; }

  /* ---- STAGE BADGE ---- */
  .stage-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: var(--bg3);
    border: 1px solid var(--green-dim);
    padding: 0.3rem 0.8rem;
    font-size: 0.7rem;
    letter-spacing: 0.3em;
    color: var(--green-dim);
    text-transform: uppercase;
    margin-bottom: 1.2rem;
  }

  .stage-badge .dot {
    width: 6px; height: 6px;
    background: var(--green);
    border-radius: 50%;
    animation: pulse 2s infinite;
  }

  /* ---- HEADINGS ---- */
  .card-title {
    font-family: 'Orbitron', monospace;
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--green);
    letter-spacing: 0.08em;
    margin-bottom: 0.5rem;
  }

  .card-desc {
    color: var(--text-dim);
    font-size: 0.82rem;
    line-height: 1.7;
    margin-bottom: 1.5rem;
    border-left: 2px solid var(--green-dim);
    padding-left: 0.8rem;
  }

  /* ---- FORM ELEMENTS ---- */
  .field-group {
    margin-bottom: 1rem;
  }

  .field-label {
    display: block;
    font-size: 0.7rem;
    color: var(--text-dim);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
  }

  input[type="text"],
  input[type="password"],
  input[type="search"] {
    width: 100%;
    background: var(--bg3);
    border: 1px solid var(--green-dim);
    color: var(--text);
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.95rem;
    padding: 0.65rem 0.9rem;
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
    border-radius: 1px;
  }

  input[type="text"]:focus,
  input[type="password"]:focus,
  input[type="search"]:focus {
    border-color: var(--green);
    box-shadow: 0 0 12px var(--green-glow);
  }

  /* ---- BUTTONS ---- */
  .btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: transparent;
    border: 1px solid var(--green);
    color: var(--green);
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.85rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    padding: 0.6rem 1.4rem;
    cursor: pointer;
    transition: background 0.2s, box-shadow 0.2s, color 0.2s;
    text-decoration: none;
    border-radius: 1px;
  }

  .btn:hover {
    background: var(--green-glow);
    box-shadow: 0 0 16px var(--green-glow);
    color: #fff;
  }

  .btn-amber {
    border-color: var(--amber);
    color: var(--amber);
  }
  .btn-amber:hover { background: #ffb80022; box-shadow: 0 0 16px #ffb80044; color: #fff; }

  .btn-ghost {
    border-color: var(--text-mute);
    color: var(--text-dim);
    font-size: 0.75rem;
    padding: 0.4rem 0.9rem;
  }
  .btn-ghost:hover { background: #ffffff08; }

  /* ---- HINT PANEL ---- */
  .hint-panel {
    margin-top: 1.4rem;
    background: var(--bg3);
    border: 1px solid #ffb80033;
    border-left: 3px solid var(--amber);
    border-radius: 1px;
    overflow: hidden;
  }

  .hint-panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.55rem 1rem;
    border-bottom: 1px solid #ffb80022;
  }

  .hint-panel-label {
    font-size: 0.68rem;
    letter-spacing: 0.28em;
    color: var(--amber);
    text-transform: uppercase;
  }

  .hint-lvl-btns { display: flex; gap: 0.4rem; }

  .hint-lvl-btn {
    background: transparent;
    border: 1px solid #ffb80055;
    color: var(--text-mute);
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.1em;
    padding: 0.25rem 0.6rem;
    cursor: pointer;
    transition: all 0.18s;
    border-radius: 1px;
  }

  .hint-lvl-btn:hover { border-color: var(--amber); color: var(--amber); }
  .hint-lvl-btn.hint-btn-active { background: #ffb80022; border-color: var(--amber); color: var(--amber); }

  .hint-row {
    display: none;
    align-items: flex-start;
    gap: 0.9rem;
    padding: 0.7rem 1rem;
    border-top: 1px solid #ffb80011;
  }

  .hint-level-badge {
    flex-shrink: 0;
    font-size: 0.62rem;
    letter-spacing: 0.15em;
    color: var(--amber);
    text-transform: uppercase;
    white-space: nowrap;
    padding-top: 0.1rem;
    min-width: 110px;
  }

  .hint-text {
    font-size: 0.8rem;
    color: var(--text-dim);
    line-height: 1.65;
  }

  /* ---- FLAG DISPLAY ---- */
  .flag-box {
    background: var(--bg3);
    border: 1px solid var(--flag);
    padding: 1rem 1.4rem;
    margin: 1.2rem 0;
    border-radius: 1px;
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
  }

  .flag-label {
    font-size: 0.65rem;
    letter-spacing: 0.3em;
    color: var(--flag);
    text-transform: uppercase;
    white-space: nowrap;
  }

  .flag-value {
    font-family: 'VT323', monospace;
    font-size: 1.3rem;
    color: #fff;
    letter-spacing: 0.05em;
    word-break: break-all;
  }

  /* ---- STATUS / ALERT BOXES ---- */
  .alert {
    padding: 0.75rem 1rem;
    border-radius: 1px;
    font-size: 0.83rem;
    margin-bottom: 1rem;
  }
  .alert-error { background: #ff3c3c11; border: 1px solid #ff3c3c44; color: #ff7070; }
  .alert-success { background: #1aff6a11; border: 1px solid var(--border2); color: var(--text); }

  /* ---- TERMINAL OUTPUT ---- */
  .terminal {
    background: #000;
    border: 1px solid var(--green-dim);
    padding: 1rem;
    font-size: 0.82rem;
    color: var(--green);
    max-height: 200px;
    overflow-y: auto;
    margin: 1rem 0;
    border-radius: 1px;
  }

  /* ---- ACTION ROW ---- */
  .action-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
    margin-top: 1.5rem;
  }

  /* ---- NEXT LEVEL BANNER ---- */
  .next-banner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--bg3);
    border: 1px solid var(--green-dim);
    padding: 1rem 1.4rem;
    margin-top: 1.5rem;
    flex-wrap: wrap;
    gap: 1rem;
  }

  .next-banner-text {
    font-size: 0.78rem;
    color: var(--text-dim);
  }

  .next-banner-text strong { color: var(--green); }

  /* ---- DIVIDER ---- */
  .divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.5rem 0;
  }

  /* ---- CODE INLINE ---- */
  code {
    background: var(--bg3);
    border: 1px solid var(--border);
    padding: 0.15rem 0.4rem;
    color: var(--blue);
    font-size: 0.85em;
    border-radius: 1px;
  }

  /* ---- RULES PAGE ---- */
  .rules-section { margin-bottom: 1.8rem; }
  .rules-section h3 {
    font-family: 'Orbitron', monospace;
    font-size: 0.85rem;
    color: var(--green);
    letter-spacing: 0.15em;
    margin-bottom: 0.8rem;
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.4rem;
  }
  .rules-list { list-style: none; padding: 0; }
  .rules-list li {
    font-size: 0.82rem;
    color: var(--text-dim);
    padding: 0.3rem 0;
    padding-left: 1.5rem;
    position: relative;
    line-height: 1.6;
  }
  .rules-list li::before { content: '//'; position: absolute; left: 0; color: var(--green-dim); }

  .flag-format-demo {
    background: var(--bg3);
    border: 1px solid var(--border2);
    padding: 0.8rem 1.2rem;
    margin: 1rem 0;
    font-family: 'VT323', monospace;
    font-size: 1.4rem;
    color: var(--flag);
    letter-spacing: 0.05em;
  }

  .stage-map {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 0.8rem;
    margin-top: 1rem;
  }

  .stage-map-item {
    background: var(--bg3);
    border: 1px solid var(--border);
    padding: 0.8rem;
    text-align: center;
    border-radius: 1px;
  }

  .stage-map-item .sn {
    font-family: 'Orbitron', monospace;
    font-size: 1rem;
    color: var(--green);
    font-weight: 700;
  }

  .stage-map-item .st {
    font-size: 0.65rem;
    color: var(--text-mute);
    margin-top: 0.3rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
  }

  /* ---- FOOTER ---- */
  .site-footer {
    text-align: center;
    padding: 1.5rem;
    border-top: 1px solid var(--border);
    margin-top: 3rem;
    font-size: 0.7rem;
    color: var(--text-mute);
    letter-spacing: 0.2em;
    position: relative;
    z-index: 10;
  }

  /* ---- ANIMATIONS ---- */
  @keyframes flicker {
    0%, 95%, 100% { opacity: 1; }
    96% { opacity: 0.85; }
    97% { opacity: 1; }
    98% { opacity: 0.9; }
    99% { opacity: 1; }
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.7); }
  }

  @keyframes blink { 0%,49% { opacity: 1; } 50%,100% { opacity: 0; } }

  .cursor::after {
    content: '_';
    animation: blink 1s step-end infinite;
    color: var(--green);
  }

  /* ---- LINKS ---- */
  a { color: var(--green); text-decoration: none; }
  a:hover { text-decoration: underline; }
</style>
"""

HINT_JS = """
<script>
function revealHint(stageId, level) {
  for (var i = 1; i <= level; i++) {
    var el = document.getElementById(stageId + '-h' + i);
    if (el) el.style.display = 'flex';
  }
  for (var j = 1; j <= 3; j++) {
    var btn = document.getElementById(stageId + '-btn' + j);
    if (btn) btn.classList.remove('hint-btn-active');
  }
  var active = document.getElementById(stageId + '-btn' + level);
  if (active) active.classList.add('hint-btn-active');
}
</script>
"""

def hint_block(hints, block_id="hint-panel"):
    """hints: list of exactly 3 strings — Lvl1 concept, Lvl2 direction, Lvl3 nudge (NO answers/payloads)."""
    rows = ""
    icons = ["&#9650;", "&#9654;&#9654;", "&#9888;"]
    labels = ["Lvl 1 — Concept", "Lvl 2 — Direction", "Lvl 3 — Nudge"]
    for i, (hint, icon, label) in enumerate(zip(hints, icons, labels), 1):
        rows += f"""
        <div id="{block_id}-h{i}" class="hint-row" style="display:none;">
          <span class="hint-level-badge">{label}</span>
          <span class="hint-text">{hint}</span>
        </div>"""
    btns = "".join(
        f'<button id="{block_id}-btn{i}" type="button" class="hint-lvl-btn" onclick="revealHint(\'{block_id}\',{i})">H{i}</button>'
        for i in range(1, 4)
    )
    return f"""
    <div class="hint-panel">
      <div class="hint-panel-header">
        <span class="hint-panel-label">// hint system</span>
        <div class="hint-lvl-btns">{btns}</div>
      </div>
      {rows}
    </div>
    """

def flag_display(flag):
    return f"""
    <div class="flag-box">
      <span class="flag-label">&#9873; Flag Captured</span>
      <span class="flag-value">{flag}</span>
    </div>
    """

def next_level_btn(href, label="Proceed to Next Stage"):
    return f"""
    <div class="next-banner">
      <div class="next-banner-text"><strong>Stage Complete.</strong> Continue to the next challenge.</div>
      <a href="{href}" class="btn btn-amber">&#187; {label}</a>
    </div>
    """

def page(stage_label, body, show_nav=True):
    nav = ""
    if show_nav:
        nav = """
        <nav class="top-nav">
          <a href="/">Home</a>
          <a href="/rules">Rules</a>
          <a href="/login">Stage 01</a>
          <a href="/level2?ref=shadow_gate_v2">Stage 02</a>
          <a href="/level3">Stage 03</a>
          <a href="/hidden_area">Stage 04</a>
          <a href="/level5">Stage 05</a>
        </nav>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{TITLE} — {SUBTITLE}</title>
{GLOBAL_CSS}
{HINT_JS}
</head>
<body>
<header class="site-header">
  <div class="logo"><span>0x</span>Day CTF</div>
  <div class="subtitle">{SUBTITLE}</div>
  <div class="tagline">// capture the flag — web exploitation track //</div>
</header>
{nav}
<main class="wrapper">
  <div class="card">
    <span class="card-corner tl"></span>
    <span class="card-corner tr"></span>
    <span class="card-corner bl"></span>
    <span class="card-corner br"></span>
    {body}
  </div>
</main>
<footer class="site-footer">
  0xDay CTF &nbsp;|&nbsp; Web Exploitation Round &nbsp;|&nbsp; Flag format: IEEE{{...}}
</footer>
</body>
</html>"""


# =============================
# HOME
# =============================

@app.route('/')
def index():
    body = f"""
    <div class="stage-badge"><span class="dot"></span> System Initialized</div>
    <h1 class="card-title cursor">Entry Point</h1>
    <p class="card-desc">
      Welcome to the <strong>0xDay Web Exploitation CTF</strong>. Five stages await. Each stage exploits a real-world web vulnerability. Capture all flags to complete Phase 01.
    </p>

    <hr class="divider">

    <div class="stage-map">
      <div class="stage-map-item"><div class="sn">01</div><div class="st">Auth Bypass</div></div>
      <div class="stage-map-item"><div class="sn">02</div><div class="st">Access Control</div></div>
      <div class="stage-map-item"><div class="sn">03</div><div class="st">SQL Injection</div></div>
      <div class="stage-map-item"><div class="sn">04</div><div class="st">Header / Cookie</div></div>
      <div class="stage-map-item"><div class="sn">05</div><div class="st">Config Leak</div></div>
    </div>

    <hr class="divider">

    <div class="action-row">
      <a href="/login" class="btn">&#187; Begin Challenge</a>
      <a href="/rules" class="btn btn-ghost">Read Rules</a>
    </div>
    """
    return page("Entry", body)


# =============================
# RULES PAGE
# =============================

@app.route('/rules')
def rules():
    body = f"""
    <div class="stage-badge"><span class="dot"></span> Briefing</div>
    <h1 class="card-title">Rules &amp; Format</h1>

    <div class="rules-section">
      <h3>// Flag Format</h3>
      <p style="font-size:0.82rem; color:var(--text-dim); margin-bottom:0.6rem;">All flags follow this exact format. Submit exactly as shown.</p>
      <div class="flag-format-demo">IEEE{{5t4g3_3x4mpl3_Fl4g}}</div>
      <p style="font-size:0.78rem; color:var(--text-mute);">Flags are case-sensitive. Do not add spaces or modify characters.</p>
    </div>

    <div class="rules-section">
      <h3>// Challenge Rules</h3>
      <ul class="rules-list">
        <li>You are permitted to use browser DevTools, curl, Burp Suite, and similar tools.</li>
        <li>Do not brute-force the server or launch DoS attacks.</li>
        <li>Do not share flags or solutions with other participants during the event.</li>
        <li>Flags are hidden in the application logic — read the source hints carefully.</li>
        <li>If you get stuck, use the hint system available on each stage page.</li>
      </ul>
    </div>

    <div class="rules-section">
      <h3>// Vulnerability Categories</h3>
      <ul class="rules-list">
        <li><strong>Stage 01</strong> — Authentication bypass via encoding / SQL injection</li>
        <li><strong>Stage 02</strong> — Access control via hidden endpoints &amp; custom headers</li>
        <li><strong>Stage 03</strong> — Second-order SQL injection / LIKE clause injection</li>
        <li><strong>Stage 04</strong> — Header &amp; cookie manipulation</li>
        <li><strong>Stage 05</strong> — Source inspection / information disclosure via exposed debug endpoint</li>
      </ul>
    </div>

    <div class="rules-section">
      <h3>// Code of Conduct</h3>
      <ul class="rules-list">
        <li>Play fair. This is a learning environment.</li>
        <li>Any attempts to disrupt infrastructure will result in disqualification.</li>
        <li>All findings outside the defined scope must be reported, not exploited.</li>
      </ul>
    </div>

    <div class="action-row">
      <a href="/login" class="btn">&#187; Start Stage 01</a>
    </div>
    """
    return page("Rules", body)


# =============================
# STAGE 1
# =============================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username', '')
        p = request.form.get('password', '')

        if "'" in u or "'" in p:
            body = f"""
            <div class="stage-badge"><span class="dot"></span> Stage 01 — Auth Bypass</div>
            <h1 class="card-title">Authentication</h1>
            <div class="alert alert-error">&#9888; Input blocked. Quote characters are filtered at surface level.</div>
            <p style="font-size:0.82rem; color:var(--text-dim); margin-bottom:1.2rem;">Not all encodings are equal. Try another approach.</p>
            <a href="/login" class="btn btn-ghost">&#8592; Try Again</a>
            """
            return page("Stage 01", body)

        u = urllib.parse.unquote(u)
        p = urllib.parse.unquote(p)

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        query = f"SELECT id FROM users WHERE username='{u}' AND password='{p}'"

        try:
            res = c.execute(query).fetchone()
        except:
            res = None

        if res:
            session['user'] = u
            body = f"""
            <div class="stage-badge"><span class="dot"></span> Stage 01 — Complete</div>
            <h1 class="card-title">Access Granted</h1>
            <div class="alert alert-success">Authentication anomaly detected. Bypass successful.</div>
            {flag_display(S1_FLAG)}
            {next_level_btn('/level2?ref=shadow_gate_v2', 'Proceed to Stage 02')}
            """
            return page("Stage 01 — Solved", body)
        else:
            body = f"""
            <div class="stage-badge"><span class="dot"></span> Stage 01 — Auth Bypass</div>
            <h1 class="card-title">Authentication</h1>
            <div class="alert alert-error">&#10006; Access Denied. Credentials rejected.</div>
            <form method="POST">
              <div class="field-group">
                <label class="field-label">Username</label>
                <input type="text" name="username" placeholder="enter username{{user}}" autocomplete="off">
              </div>
              <div class="field-group">
                <label class="field-label">Password</label>
                <input type="password" name="password" placeholder="enter password">
              </div>
              <div class="action-row">
                <button type="submit" class="btn">&#187; Authenticate</button>
              </div>
            </form>
            {hint_block([
                "Input validation that runs before transformation is not the same as sanitization. The check and the use happen at different stages.",
                "Characters that get blocked in raw form may have alternate representations in different encoding schemes.",
                "SQL queries built by joining strings together can be restructured if you can control where quotes appear — think about how SQL parses string boundaries."
            ], "hint1a")}
            """
            return page("Stage 01", body)

    body = f"""
    <div class="stage-badge"><span class="dot"></span> Stage 01 — Auth Bypass</div>
    <h1 class="card-title">Authentication</h1>
    <p class="card-desc">
      A login form stands between you and the flag. The server filters some characters — but filtering isn't sanitization. Find a way in. Login as user
    </p>
    <form method="POST">
      <div class="field-group">
        <label class="field-label">Username</label>
        <input type="text" name="username" placeholder="enter username" autocomplete="off">
      </div>
      <div class="field-group">
        <label class="field-label">Password</label>
        <input type="password" name="password" placeholder="enter password">
      </div>
      <div class="action-row">
        <button type="submit" class="btn">&#187; Authenticate</button>
      </div>
    </form>
    {hint_block([
        "Authentication systems check credentials against a database. If the query structure itself can be manipulated, the check becomes meaningless.",
        "Certain special characters have meaning inside SQL. If user input is placed directly into a query string, those characters don't stay as data.",
        "The filter inspects the raw value before the server transforms it. Encoding the same data differently may let it pass the check while still reaching the query unchanged."
    ], "hint1b")}
    """
    return page("Stage 01", body)


# =============================
# STAGE 2
# =============================

@app.route('/level2')
def level2():
    ref = request.args.get('ref', '')

    if urllib.parse.quote(ref) == 'shadow_gate_v2':
        body = f"""
        <div class="stage-badge"><span class="dot"></span> Stage 02 — Access Control</div>
        <h1 class="card-title">Checkpoint Reached</h1>
        <p class="card-desc">
          You passed the gate. But the real access panel is hidden. Machines leave breadcrumbs — check what robots know. Then speak the right language to the server.
        </p>
        <hr class="divider">
        <p style="font-size:0.82rem; color:var(--text-dim);">Next target: find a hidden admin endpoint and send the correct identity header.</p>
        {hint_block([
            "Web servers sometimes publish a file that tells crawlers which paths are off-limits. This file is a standard part of how the web works — and it's publicly readable.",
            "Restricted paths listed in that file are meant to be hidden, but listing them makes them discoverable. Check what paths the server is trying to hide.",
            "Servers can make decisions based on data in the request that isn't the URL or body. Some endpoints trust certain request metadata to determine who you are."
        ], "hint2")}
        """
        return page("Stage 02", body)

    body = f"""
    <div class="stage-badge"><span class="dot"></span> Stage 02 — Access Control</div>
    <h1 class="card-title">Invalid Entry</h1>
    <div class="alert alert-error">&#9888; Access reference is invalid or improperly encoded.</div>
    <p style="font-size:0.82rem; color:var(--text-dim);">Encoding direction matters. The gate checks an encoded value.</p>
    <a href="/login" class="btn btn-ghost">&#8592; Back to Stage 01</a>
    """
    return page("Stage 02", body)


@app.route('/robots.txt')
def robots():
    return """User-agent: *\nDisallow: /admin_v5\n# try custom header"""


@app.route('/admin_v5')
def admin_v5():
    if request.headers.get('X-Role') == 'admin':
        body = f"""
        <div class="stage-badge"><span class="dot"></span> Stage 02 — Complete</div>
        <h1 class="card-title">Privileged Access Granted</h1>
        <div class="alert alert-success">Identity accepted via header injection. You became what you sent.</div>
        {flag_display(S2_FLAG)}
        {next_level_btn('/level3', 'Proceed to Stage 03')}
        """
        return page("Stage 02 — Solved", body)

    body = f"""
    <div class="stage-badge"><span class="dot"></span> Stage 02 — Admin Panel</div>
    <h1 class="card-title">Forbidden</h1>
    <div class="alert alert-error">&#10006; Access denied. Your identity header is missing or incorrect.</div>
    <p style="font-size:0.82rem; color:var(--text-dim); margin-top:0.8rem;">Headers define identity. Send the right one.</p>
    {hint_block([
        "HTTP requests carry more than just a URL and a body. Headers are key-value pairs sent alongside the request — servers can read and act on any of them.",
        "Some applications trust custom headers to determine a user's role or permission level without verifying them server-side. Think about what role would unlock this panel.",
        "Tools like curl, Burp Suite, or browser extensions let you craft requests with any headers you choose — browsers alone won't let you set arbitrary headers normally."
    ], "hint-admin")}
    """
    return page("Stage 02", body)


# =============================
# STAGE 3
# =============================

@app.route('/level3', methods=['GET', 'POST'])
def level3():
    output_html = ""

    if request.method == 'POST':
        k = request.form.get('keyword', '')

        if not k.strip():
            output_html = '<div class="alert alert-error">Empty input not allowed.</div>'
        elif "admin" in k.lower():
            output_html = '<div class="alert alert-error">&#9888; Keyword "admin" is blocked.</div>'
        else:
            conn = sqlite3.connect("database.db")
            c = conn.cursor()
            query = f"SELECT username FROM users WHERE username LIKE '%{k}%'"
            data = c.execute(query).fetchall()
            result_text = str(data)
            output_html = f'<div class="terminal">{result_text}</div>'

            if any('admin' in str(x) for x in data):
                output_html += flag_display(S3_FLAG)
                output_html += next_level_btn('/hidden_area', 'Proceed to Stage 04')

    body = f"""
    <div class="stage-badge"><span class="dot"></span> Stage 03 — SQL Injection</div>
    <h1 class="card-title">User Search</h1>
    <p class="card-desc">
      A search field queries the database using a LIKE clause. The word "admin" is blocked client-side — but can you retrieve admin records without using that word directly?
    </p>
    <form method="POST">
      <div class="field-group">
        <label class="field-label">Search Keyword</label>
        <input type="search" name="keyword" placeholder="search users..." autocomplete="off">
      </div>
      <div class="action-row">
        <button type="submit" class="btn">&#187; Execute Search</button>
      </div>
    </form>
    {output_html}
    {hint_block([
        "The search runs a SQL LIKE query. LIKE uses wildcard characters to match patterns — but what if SQL itself is restructured rather than using the pattern-matching alone?",
        "The keyword filter blocks a specific string in your input, not in the database results. The server checks if <em>your input</em> contains that string — not the query output.",
        "SQL supports combining two separate SELECT statements with a keyword that merges their result sets. If you can inject that structure, you control what data comes back."
    ], "hint3")}
    """
    return page("Stage 03", body)


# =============================
# STAGE 4
# =============================

@app.route('/hidden_area')
def hidden_area():
    token = request.headers.get('X-Access', '') or request.cookies.get('access', '')

    if token == 'granted':
        body = f"""
        <div class="stage-badge"><span class="dot"></span> Stage 04 — Complete</div>
        <h1 class="card-title">Hidden Area Unlocked</h1>
        <div class="alert alert-success">Token accepted. Cookie / header value verified.</div>
        {flag_display(S4_FLAG)}
        <hr class="divider">
        <p style="font-size:0.82rem; color:var(--text-dim);">
          Stage 05 is the final challenge. Developers sometimes leave sensitive endpoints exposed — especially when debug mode is on. The path to the last flag is hidden somewhere in this page.
        </p>
        <!-- developer note: debug endpoint still live at /debug_config — remove before prod -->
        {next_level_btn('/level5', 'Proceed to Stage 05')}
        """
        return page("Stage 04 — Solved", body)

    resp = make_response(page("Stage 04", f"""
    <div class="stage-badge"><span class="dot"></span> Stage 04 — Header / Cookie Abuse</div>
    <h1 class="card-title">Hidden Area</h1>
    <div class="alert alert-error">&#10006; Access denied. Your token value is incorrect.</div>
    <p style="font-size:0.82rem; color:var(--text-dim); margin-bottom:1.2rem;">
      The server checks either an <code>X-Access</code> header <em>or</em> an <code>access</code> cookie.
      It has already set a cookie on your browser — but is the value right?
    </p>
    {hint_block([
        "Browsers store small pieces of data sent by servers called cookies. The server can set a cookie, but the client stores it — and can modify it.",
        "When a server sets a cookie, it's not locked. The stored value lives in your browser and can be inspected or changed using browser developer tools.",
        "The server also accepts an alternative: a custom request header. Requests sent via tools outside the browser can carry headers that a normal page visit would never include."
    ], "hint4")}
    """))
    resp.set_cookie('access', 'denied')
    return resp


# =============================
# STAGE 5
# =============================

@app.route('/level5')
def level5():
    body = f"""
    <div class="stage-badge"><span class="dot"></span> Stage 05 — Information Disclosure</div>
    <h1 class="card-title">Final Stage</h1>
    <p class="card-desc">
      Developers build applications with debug tools that should never reach production. These endpoints expose secrets — configuration, keys, flags. Your job: find the one left open on this server.
    </p>
    <hr class="divider">
    <div class="terminal">
      &gt; target: this web application<br>
      &gt; objective: locate exposed debug endpoint<br>
      &gt; method: source inspection / path discovery<br>
      &gt; status: <span style="color:var(--amber)">searching...</span>
    </div>
    {hint_block([
        "Web pages are more than what you see rendered. Browsers receive full HTML source — developers sometimes leave notes in that source that are invisible on screen but readable in the code.",
        "Every page you have visited so far has source code. Check the HTML of the page that sent you here — developers often leave comments about things they forgot to clean up.",
        "Debug and configuration endpoints are often named with words like 'debug', 'config', 'test', or 'admin'. The note left in the previous page's source points directly to the path."
    ], "hint5")}
    """
    return page("Stage 05", body)


@app.route('/debug_config')
def debug_config():
    body = f"""
    <div class="stage-badge"><span class="dot"></span> Stage 05 — Complete</div>
    <h1 class="card-title">Debug Config Exposed</h1>
    <div class="alert alert-success">Information disclosure vulnerability triggered. Debug endpoint left live in production.</div>
    <div class="terminal">
      &gt; /debug_config accessed<br>
      &gt; SECRET_KEY = {app.secret_key}<br>
      &gt; ENVIRONMENT = production<br>
      &gt; DEBUG = True<br>
      &gt; <span style="color:var(--red)">WARNING: this endpoint should be disabled in production</span>
    </div>
    {flag_display(S5_FLAG)}
    <div class="next-banner">
      <div class="next-banner-text"><strong>Phase 01 Complete.</strong> All five flags captured. Well done, operator.</div>
      <a href="/" class="btn btn-amber">&#187; Return to Entry</a>
    </div>
    """
    return page("Stage 05 — Final", body)


# =============================
# MAIN
# =============================

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
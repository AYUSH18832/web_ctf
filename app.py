from flask import Flask, request, redirect, session, make_response
import sqlite3
import urllib.parse

app = Flask(__name__)
app.secret_key = "weaksecret"

TITLE = "TEST RUN FOR CTF PHASE 1"
S5_FINAL = "SUVFRXtQaDQ1M18wMV9DMG1wbDM3M2RfTTQ1NzNyfQ=="

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
# UI
# =============================

def page(title, body):
    return f"""
    <html>
    <head>
        <title>{TITLE}</title>
        <style>
            body {{ background:#0b0f0c; color:#9cff9c; font-family: monospace; }}
            .box {{ border:1px solid #1aff1a; padding:20px; margin:40px auto; width:60%; box-shadow:0 0 15px #00ff88; }}
            a {{ color:#00ffaa; }}
            input,button {{ background:#001a00; color:#9cff9c; border:1px solid #00ff88; padding:8px; margin:4px; }}
            .hint {{ color:#2aff2a; opacity:0.25; font-size:11px; }}
        </style>
    </head>
    <body>
        <div class='box'>
            <h1>{TITLE}</h1>
            <h3>[ {title} ]</h3>
            {body}
        </div>
    </body>
    </html>
    """

# =============================
# HOME
# =============================

@app.route('/')
def index():
    return page("ENTRY", """
    <p>System initialized.</p>
    <a href='/login'>Authenticate</a>
    <p class='hint'>Input may be transformed before it is trusted.</p>
    """)

# =============================
# STAGE 1 
# =============================

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username','')
        p = request.form.get('password','')

        # weak filter (blocks quotes but can be bypassed via encoding)
        if "'" in u or "'" in p:
            return page("AUTH", "<p>Blocked input</p><p class='hint'>Not all encodings are equal.</p>")

        # decode once (bypass via double encoding)
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
            return page("AUTH", """
            <p>Access anomaly.</p>
            <p>Welcome Guest!</p>
            <!-- next_ref=shadow_gate_v2 -->
            <p class='hint'>Layers of decoding reveal truth.</p>
            <p>FLAG:SUVFRXs1dDRnM18wMV80dTdoX0J5cDQ1NX0= [Can't read flag,Look for hint look into code.]<!--Do you know base64?--></p>
            <a href='/level2?ref=shadow_gate_v2'>continue</a>
            """)
        else:
            return page("AUTH", "<p>Denied</p>")

    return page("AUTH", """
    <p class='hint'>Can you login as guest?</p>
    <form method='POST'>
        <input placeholder="Enter your name" name='username'>
        <input placeholder="Enter your password" name='password'>
        <button>enter</button>
    </form>
    <p class='hint'>Sometimes one decode isn’t enough.</p>
    """)

# =============================
# STAGE 2 
# =============================

@app.route('/level2')
def level2():
    ref = request.args.get('ref','')

    # encoded check (must send encoded value)
    if urllib.parse.quote(ref) == 'shadow_gate_v2':
        return page("LEVEL 2", """
        <p>Checkpoint reached.</p>
        <p class='hint'>Robots speak, but headers whisper louder.</p>
        """)

    return page("LEVEL 2", "<p>Invalid</p><p class='hint'>Encoding direction matters.</p>")

@app.route('/robots.txt')
def robots():
    return """
User-agent: *
Disallow: /admin_v5
# try custom header"""

@app.route('/admin_v5')
def admin_v5():
    # require special header instead of direct access
    if request.headers.get('X-Role') == 'admin':
        return page("ADMIN", """
        <p>Privileged access granted.</p>
        <p class='hint'>You became what you sent.</p>
        <p>FLAG:SUVFRXs1dDRnM18wM181UUwxX0NoNDFufQ==</p>
        <a href='/level3'>next</a>
        """)

    return page("ADMIN", "<p>Forbidden</p><p class='hint'>Headers define identity.</p>")

# =============================
# STAGE 3 
# =============================

@app.route('/level3', methods=['GET','POST'])
def level3():
    output = ""
    if request.method == 'POST':
        k = request.form.get('keyword','')
        if "admin" in k.lower():
            output = "Blocked"
        else:
            conn = sqlite3.connect("database.db")
            c = conn.cursor()
            query = f"SELECT username FROM users WHERE username LIKE '%{k}%'"
            data = c.execute(query).fetchall()
            output = str(data)
            if any('admin' in str(x) for x in data):
                output += "<br>FLAG:SUVFRXs1dDRnM18wNF9IMzRkM3JfQzAwazEzXzRidTUzfQ== → got to /hidden_area"

    return page("LEVEL 3", f"<form method='POST'><input name='keyword'><button>search</button></form><div>{output}<p>Hint: Can you find the database.?</p></div>")

# =============================
# STAGE 4 
# =============================

@app.route('/hidden_area')
def hidden_area():
    token = request.headers.get('X-Access','') or request.cookies.get('access','')
    if token == 'granted':
        return page("HIDDEN", "<p>FLAG:SUVFRXs1dDRnM18wNF9IMzRkM3JfQzAwazEzXzRidTUzfQ==</p><p>Hint: Look for the hidden configuration file for final flag</p> <!-- Look for /debug_config  Its easy.-->")
    resp = make_response(page("HIDDEN", "Denied"))
    resp.set_cookie('access','denied')
    return resp

# =============================
# STAGE 5 
# =============================

@app.route('/debug_config')
def debug_config():
    return page("DEBUG", f"<pre>SECRET={app.secret_key}</pre><p>FINAL FLAG:{S5_FINAL}</p>")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)

import streamlit as st, json, os, hashlib, base64, datetime as dt
import plotly.express as px
from hijri_converter import Gregorian

st.set_page_config(page_title="Zakhira", page_icon="🪙", layout="wide")
DB = "db.json"
TYPES = {"Cash": 1, "Bank balance": 1, "Gold (grams)": 0, "Silver (grams)": 0,
         "Shares / funds": 1, "Business inventory": 1, "Money owed to you": 1, "Debt you owe": 1}

# ---------- storage (demo: JSON file. Move to Supabase for production) ----------
def load(): return json.load(open(DB)) if os.path.exists(DB) else {}
def save(d): json.dump(d, open(DB, "w"))
def hp(p, s): return hashlib.pbkdf2_hmac("sha256", p.encode(), s.encode(), 100000).hex()
db = load()

# ---------- look and feel ----------
st.markdown("""<style>
.hero{background:linear-gradient(120deg,#063f2e,#0b8a63 55%,#e2b653);border-radius:24px;padding:30px;color:#fff;display:flex;gap:20px;align-items:center;flex-wrap:wrap}
.hero h1{margin:0;font-size:2.4rem;color:#fff}.hero p{margin:6px 0 0;opacity:.92;font-size:1.05rem}
.tile{border-radius:20px;padding:18px;color:#fff;margin-bottom:10px}
.g{background:linear-gradient(135deg,#8a6d2f,#f3d37a)}.s{background:linear-gradient(135deg,#5d6f78,#dfe6ea);color:#10231c}
.e{background:linear-gradient(135deg,#064a37,#2bb585)}.r{background:linear-gradient(135deg,#7a2b3a,#e27d60)}
.tile b{font-size:1.7rem;display:block}.rem{border-left:6px solid #0b8a63;background:rgba(11,138,99,.08);padding:10px 14px;border-radius:10px;margin:6px 0}
.rem.late{border-color:#c0392b;background:rgba(192,57,43,.1)}.rem.soon{border-color:#e2b653;background:rgba(226,182,83,.15)}
.av{width:90px;height:90px;border-radius:50%;object-fit:cover;border:4px solid #e2b653}
</style>""", unsafe_allow_html=True)

ART = """<svg width="260" height="110" viewBox="0 0 260 110"><defs>
<linearGradient id="a" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff2b0"/><stop offset="1" stop-color="#c8921f"/></linearGradient>
<linearGradient id="b" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#9aa7ae"/></linearGradient></defs>
<polygon points="10,95 30,55 120,55 140,95" fill="url(#a)" stroke="#8a6d2f"/><text x="75" y="82" font-size="14" text-anchor="middle" fill="#6b4e12" font-weight="700">GOLD</text>
<circle cx="185" cy="55" r="34" fill="url(#b)" stroke="#6b7a82" stroke-width="3"/><text x="185" y="62" font-size="18" text-anchor="middle" fill="#445" font-weight="700">AG</text>
<rect x="190" y="18" width="62" height="34" rx="5" fill="#2e8b57" stroke="#fff" transform="rotate(12 220 35)"/><text x="221" y="42" font-size="13" fill="#fff" text-anchor="middle" font-weight="700" transform="rotate(12 220 35)">Rs 5000</text></svg>"""

def hero(sub):
    st.markdown(f'<div class="hero"><div>{ART}</div><div><h1>🪙 Zakhira</h1><p>{sub}</p></div></div>', unsafe_allow_html=True)

# ---------- auth ----------
if "me" not in st.session_state: st.session_state.me = None
if not st.session_state.me:
    hero("Apna zakat hisaab, sona chandi aur paisa, sab ek jagah. Asaan, halal, bharosemand.")
    st.write("")
    t1, t2 = st.tabs(["Log in", "Create account"])
    with t1:
        e = st.text_input("Email", key="le").strip().lower(); p = st.text_input("Password", type="password", key="lp")
        if st.button("Log in", type="primary"):
            u = db.get(e)
            if u and u["pw"] == hp(p, u["salt"]): st.session_state.me = e; st.rerun()
            else: st.error("Email or password is incorrect.")
    with t2:
        n = st.text_input("Full name"); e2 = st.text_input("Email", key="re").strip().lower()
        p2 = st.text_input("Password (6+ characters)", type="password", key="rp")
        c1, c2 = st.columns(2)
        fiqh = c1.selectbox("Fiqh", ["Hanafi", "Shafi", "Maliki", "Hanbali", "Jafari"])
        zd = c2.date_input("Your zakat date", dt.date.today())
        if st.button("Create account", type="primary"):
            if not n or "@" not in e2 or len(p2) < 6: st.error("Enter your name, a valid email and a 6+ character password.")
            elif e2 in db: st.error("This email is already registered.")
            else:
                s = os.urandom(8).hex()
                db[e2] = {"name": n, "pw": hp(p2, s), "salt": s, "fiqh": fiqh, "zdate": str(zd), "photo": "",
                          "assets": [], "txs": [], "rem": [], "rates": {"gold": 30000, "silver": 350}}
                save(db); st.session_state.me = e2; st.rerun()
    st.stop()

me = st.session_state.me; u = db[me]
def val(a): return a["amt"] * (u["rates"]["gold"] if a["type"].startswith("Gold") else u["rates"]["silver"] if a["type"].startswith("Silver") else 1)
pos = sum(val(a) for a in u["assets"] if a["type"] != "Debt you owe")
debt = sum(val(a) for a in u["assets"] if a["type"] == "Debt you owe")
net = pos - debt; nisab = 612.36 * u["rates"]["silver"]; due = net * 0.025 if net >= nisab else 0
fmt = lambda x: f"Rs {x:,.0f}"

def next_zakat():
    d = dt.date.fromisoformat(u["zdate"])
    while d < dt.date.today(): d += dt.timedelta(days=354)   # one Hijri year
    return d

with st.sidebar:
    if u["photo"]: st.markdown(f'<img class="av" src="data:image/png;base64,{u["photo"]}">', unsafe_allow_html=True)
    st.subheader(f"Assalamualaikum, {u['name'].split()[0]}")
    page = st.radio("Menu", ["🏠 Home", "💰 Assets", "🧮 Zakat", "🤲 Giving", "⏰ Reminders", "⚙️ Profile"], label_visibility="collapsed")
    q = st.text_input("🔎 Search (gold, BC, nisab...)").lower()
    if q:
        hits = {"gold": "Assets / Zakat", "nisab": "Zakat", "bc": "Add as 'Money owed to you' in Assets", "committee": "Add as 'Money owed to you' in Assets",
                "sadaqah": "Giving", "reminder": "Reminders", "photo": "Profile", "debt": "Assets"}
        for k, v in hits.items():
            if q in k: st.info(f"{k.title()} → {v}")
    st.caption("Dark / light: use the ⋮ menu (top right) → Settings → Theme.")
    if st.button("Log out"): st.session_state.me = None; st.rerun()

# ---------- pages ----------
if page == "🏠 Home":
    nz = next_zakat(); days = (nz - dt.date.today()).days
    h = Gregorian(nz.year, nz.month, nz.day).to_hijri()
    hero(f"Your next zakat date is in {days} days ({h.day} {h.month_name()} {h.year} AH).")
    st.write("")
    a, b, c, d = st.columns(4)
    a.markdown(f'<div class="tile e">Net worth<b>{fmt(net)}</b></div>', unsafe_allow_html=True)
    b.markdown(f'<div class="tile g">Zakat due<b>{fmt(due)}</b></div>', unsafe_allow_html=True)
    c.markdown(f'<div class="tile s">Gold + silver<b>{fmt(sum(val(x) for x in u["assets"] if x["type"][:4] in ("Gold","Silv")))}</b></div>', unsafe_allow_html=True)
    d.markdown(f'<div class="tile r">Given so far<b>{fmt(sum(t["amt"] for t in u["txs"] if t["kind"]=="Zakat"))}</b></div>', unsafe_allow_html=True)
    rows = [(a["type"], val(a)) for a in u["assets"] if a["type"] != "Debt you owe"]
    if rows:
        fig = px.pie(names=[r[0] for r in rows], values=[r[1] for r in rows], hole=.5,
                     color_discrete_sequence=["#0b8a63", "#e2b653", "#7fb99f", "#c8921f", "#5d6f78", "#e27d60"])
        st.plotly_chart(fig, use_container_width=True)
    else: st.info("Add your first asset in the Assets page to see your chart.")

elif page == "💰 Assets":
    st.header("Assets and debts")
    c1, c2, c3 = st.columns([2, 2, 3])
    t = c1.selectbox("Type", list(TYPES)); amt = c2.number_input("Amount (Rs, or grams)", min_value=0.0, step=100.0); note = c3.text_input("Note")
    if st.button("Add", type="primary") and amt > 0:
        u["assets"].append({"type": t, "amt": amt, "note": note}); save(db); st.rerun()
    for i, a in enumerate(u["assets"]):
        x, y = st.columns([6, 1]); x.write(f"**{a['type']}** {a['note']} — {fmt(val(a))}")
        if y.button("Remove", key=f"d{i}"): u["assets"].pop(i); save(db); st.rerun()

elif page == "🧮 Zakat":
    st.header("Zakat calculator")
    c1, c2 = st.columns(2)
    g = c1.number_input("Gold rate per gram (Rs)", value=float(u["rates"]["gold"])); s = c2.number_input("Silver rate per gram (Rs)", value=float(u["rates"]["silver"]))
    if st.button("Update rates"): u["rates"] = {"gold": g, "silver": s}; save(db); st.rerun()
    a, b, c = st.columns(3); a.metric("Assets", fmt(pos)); b.metric("Debts", fmt(debt)); c.metric("Nisab (silver)", fmt(nisab))
    if net >= nisab: st.success(f"Zakat is due: {fmt(due)} (2.5% of {fmt(net)})")
    else: st.warning("Your net wealth is below nisab. No zakat due.")
    st.caption("This is a guide, not a fatwa. Please confirm with your scholar.")

elif page == "🤲 Giving":
    st.header("Giving record")
    c1, c2, c3 = st.columns(3)
    k = c1.selectbox("Type", ["Zakat", "Sadaqah", "Fidya", "Kaffara"]); amt = c2.number_input("Amount (Rs)", min_value=0.0, step=500.0); to = c3.text_input("Given to")
    if st.button("Save record", type="primary") and amt > 0:
        u["txs"].append({"kind": k, "amt": amt, "to": to or "-", "date": str(dt.date.today())}); save(db); st.rerun()
    if u["txs"]:
        import pandas as pd
        df = pd.DataFrame(u["txs"]); f = st.multiselect("Filter", df.kind.unique(), default=list(df.kind.unique()))
        df = df[df.kind.isin(f)]; st.dataframe(df, use_container_width=True); st.metric("Total", fmt(df.amt.sum()))
        st.download_button("Export CSV", df.to_csv(index=False), "giving.csv")

elif page == "⏰ Reminders":
    st.header("Reminders")
    nz = next_zakat(); st.markdown(f'<div class="rem soon">🪙 <b>Zakat due date</b> — {nz} ({(nz-dt.date.today()).days} days left)</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([3, 2]); title = c1.text_input("New reminder (e.g. Pay Fitrana, Qurbani saving)"); d = c2.date_input("Date", dt.date.today())
    if st.button("Add reminder", type="primary") and title:
        u["rem"].append({"t": title, "d": str(d)}); save(db); st.rerun()
    for i, r in sorted(enumerate(u["rem"]), key=lambda x: x[1]["d"]):
        left = (dt.date.fromisoformat(r["d"]) - dt.date.today()).days
        cls = "late" if left < 0 else "soon" if left <= 7 else ""
        x, y = st.columns([6, 1])
        x.markdown(f'<div class="rem {cls}"><b>{r["t"]}</b> — {r["d"]} ({"overdue" if left<0 else f"{left} days left"})</div>', unsafe_allow_html=True)
        if y.button("Done", key=f"r{i}"): u["rem"].pop(i); save(db); st.rerun()

else:
    st.header("Profile")
    if u["photo"]: st.markdown(f'<img class="av" src="data:image/png;base64,{u["photo"]}">', unsafe_allow_html=True)
    up = st.file_uploader("Profile photo", type=["png", "jpg", "jpeg"])
    n = st.text_input("Name", u["name"]); zd = st.date_input("Zakat date", dt.date.fromisoformat(u["zdate"]))
    if st.button("Save profile", type="primary"):
        u["name"] = n; u["zdate"] = str(zd)
        if up: u["photo"] = base64.b64encode(up.getvalue()).decode()
        save(db); st.rerun()

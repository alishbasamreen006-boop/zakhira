import streamlit as st, json, os, hashlib, base64, datetime as dt, random
import pandas as pd, plotly.express as px, plotly.graph_objects as go
from hijri_converter import Gregorian

st.set_page_config(page_title="Zakhira", page_icon="🪙", layout="wide")
DB = "db.json"; TODAY = dt.date.today()
PAL = ["#0b8a63", "#e2b653", "#7fb99f", "#e27d60", "#5d6f78", "#c8921f", "#8e6bbf", "#4aa3c7"]
ASSET_TYPES = ["Cash", "Bank balance", "Gold (grams)", "Silver (grams)", "Shares / funds", "Business inventory", "Property for trade"]
EXP_CATS = ["Food", "Rent", "Bills", "Transport", "Education", "Health", "Family", "Fun", "Other"]
fmt = lambda x: f"Rs {x:,.0f}"

# ---------------- storage (demo JSON file; use Supabase for production) ----------------
def load(): return json.load(open(DB)) if os.path.exists(DB) else {}
def save(): json.dump(db, open(DB, "w"))
def hp(p, s): return hashlib.pbkdf2_hmac("sha256", p.encode(), s.encode(), 100000).hex()
db = load()

# ---------------- look and feel ----------------
st.markdown("""<style>
.hero{background:linear-gradient(120deg,#063f2e,#0b8a63 55%,#e2b653);border-radius:26px;padding:26px 30px;color:#fff;display:flex;gap:22px;align-items:center;flex-wrap:wrap;margin-bottom:14px}
.hero h1{margin:0;font-size:2.2rem;color:#fff}.hero p{margin:6px 0 0;opacity:.93;font-size:1.05rem}
.tile{border-radius:22px;padding:16px 18px;color:#fff;margin-bottom:10px;box-shadow:0 6px 16px rgba(0,0,0,.12)}
.tile small{opacity:.9;font-size:.9rem}.tile b{font-size:1.5rem;display:block}
.g{background:linear-gradient(135deg,#8a6d2f,#d9b24c)}.s{background:linear-gradient(135deg,#5d6f78,#9fb0b9)}
.e{background:linear-gradient(135deg,#064a37,#2bb585)}.r{background:linear-gradient(135deg,#7a2b3a,#e27d60)}.b{background:linear-gradient(135deg,#1f5f7a,#6cc3e0)}
.card{background:rgba(11,138,99,.07);border:1px solid rgba(11,138,99,.18);border-radius:20px;padding:14px 18px;margin:6px 0}
.tip{background:linear-gradient(120deg,rgba(226,182,83,.28),rgba(226,182,83,.08));border-radius:20px;padding:16px 20px;margin-top:10px}
.rem{border-left:6px solid #0b8a63;background:rgba(11,138,99,.08);padding:9px 14px;border-radius:10px;margin:5px 0}
.rem.late{border-color:#c0392b;background:rgba(192,57,43,.1)}.rem.soon{border-color:#e2b653;background:rgba(226,182,83,.17)}
.av{width:86px;height:86px;border-radius:50%;object-fit:cover;border:4px solid #e2b653}
</style>""", unsafe_allow_html=True)

ART = """<svg width="250" height="105" viewBox="0 0 260 110"><defs>
<linearGradient id="a" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff2b0"/><stop offset="1" stop-color="#c8921f"/></linearGradient>
<linearGradient id="b" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#9aa7ae"/></linearGradient></defs>
<polygon points="10,95 30,55 120,55 140,95" fill="url(#a)" stroke="#8a6d2f"/><text x="75" y="82" font-size="14" text-anchor="middle" fill="#6b4e12" font-weight="700">GOLD</text>
<circle cx="185" cy="55" r="34" fill="url(#b)" stroke="#6b7a82" stroke-width="3"/><text x="185" y="62" font-size="18" text-anchor="middle" fill="#445" font-weight="700">AG</text>
<rect x="190" y="18" width="62" height="34" rx="5" fill="#2e8b57" stroke="#fff" transform="rotate(12 220 35)"/><text x="221" y="42" font-size="13" fill="#fff" text-anchor="middle" font-weight="700" transform="rotate(12 220 35)">Rs 5000</text></svg>"""
def hero(sub, title="🪙 Zakhira"):
    st.markdown(f'<div class="hero"><div>{ART}</div><div><h1>{title}</h1><p>{sub}</p></div></div>', unsafe_allow_html=True)
def tile(label, value, cls, icon=""):
    return f'<div class="tile {cls}"><small>{icon} {label}</small><b>{value}</b></div>'
def style(fig, h=300):
    fig.update_layout(height=h, margin=dict(l=10, r=10, t=45, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", colorway=PAL)
    st.plotly_chart(fig, width="stretch")

# ---------------- auth ----------------
if "me" not in st.session_state: st.session_state.me = None
if not st.session_state.me:
    hero("Your all-in-one halal money companion: wealth, zakat, budgeting, goals, investing and giving.")
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
        fiqh = c1.selectbox("Fiqh", ["Hanafi", "Shafi", "Maliki", "Hanbali", "Jafari"]); zd = c2.date_input("Your zakat date", TODAY)
        if st.button("Create account", type="primary"):
            if not n or "@" not in e2 or len(p2) < 6: st.error("Enter your name, a valid email and a 6+ character password.")
            elif e2 in db: st.error("This email is already registered.")
            else:
                s = os.urandom(8).hex(); db[e2] = {"name": n, "pw": hp(p2, s), "salt": s, "fiqh": fiqh, "zdate": str(zd), "photo": ""}
                save(); st.session_state.me = e2; st.rerun()
    st.stop()

me = st.session_state.me; u = db[me]
for k, v in {"assets": [], "txs": [], "rem": [], "flow": [], "goals": [], "qarz": [], "hist": [], "rates": {"gold": 30000, "silver": 350}}.items(): u.setdefault(k, v)

def val(a): return a["amt"] * (u["rates"]["gold"] if a["type"].startswith("Gold") else u["rates"]["silver"] if a["type"].startswith("Silver") else 1)
def calc():
    pos = sum(val(a) for a in u["assets"]) + sum(q["amt"] for q in u["qarz"] if q["dir"] == "Owed to me" and not q["done"])
    debt = sum(q["amt"] for q in u["qarz"] if q["dir"] == "I owe" and not q["done"])
    nisab = 612.36 * u["rates"]["silver"]; net = pos - debt
    return pos, debt, net, nisab, (net * 0.025 if net >= nisab else 0)
pos, debt, net, nisab, due = calc()
if not u["hist"] or u["hist"][-1]["d"] != str(TODAY):
    u["hist"].append({"d": str(TODAY), "v": net}); save()
def next_zakat():
    d = dt.date.fromisoformat(u["zdate"])
    while d < TODAY: d += dt.timedelta(days=354)
    return d
def paid(): return sum(t["amt"] for t in u["txs"] if t["kind"] == "Zakat")
def month_df():
    if not u["flow"]: return pd.DataFrame(columns=["date", "kind", "cat", "amt", "m"])
    df = pd.DataFrame(u["flow"]); df["m"] = df["date"].str[:7]; return df
def barakah_score():
    df = month_df(); inc = df[df.kind == "Income"].amt.sum(); exp = df[df.kind == "Expense"].amt.sum()
    sv = max(0, min(1, (inc - exp) / inc)) * 40 if inc else 0
    gv = 30 if due == 0 else min(1, paid() / due) * 30
    gl = (sum(min(1, g["saved"] / g["target"]) for g in u["goals"]) / len(u["goals"]) * 30) if u["goals"] else 0
    return round(sv + gv + gl)

def demo_data():
    r = random.Random(7)
    u["assets"] = [{"type": "Cash", "amt": 250000, "note": "Home"}, {"type": "Bank balance", "amt": 900000, "note": "Islamic savings"},
                   {"type": "Gold (grams)", "amt": 45, "note": "Jewellery"}, {"type": "Silver (grams)", "amt": 300, "note": ""}, {"type": "Shares / funds", "amt": 600000, "note": "Halal fund"}]
    u["flow"] = []
    for i in range(6):
        ds = str(TODAY.replace(day=1) - dt.timedelta(days=30 * i))
        u["flow"].append({"kind": "Income", "cat": "Salary", "amt": 180000, "date": ds})
        for c, a in zip(EXP_CATS, [30000, 45000, 15000, 12000, 10000, 6000, 14000, 8000, 5000]): u["flow"].append({"kind": "Expense", "cat": c, "amt": a + r.randint(-3000, 5000), "date": ds})
    u["goals"] = [{"name": "Hajj", "icon": "🕋", "target": 1400000, "saved": 520000}, {"name": "Qurbani", "icon": "🐐", "target": 150000, "saved": 90000}, {"name": "Emergency fund", "icon": "🛟", "target": 600000, "saved": 310000}]
    u["qarz"] = [{"who": "Ali (friend)", "dir": "Owed to me", "amt": 50000, "due": str(TODAY + dt.timedelta(days=20)), "done": False}, {"who": "Shop supplier", "dir": "I owe", "amt": 30000, "due": str(TODAY + dt.timedelta(days=5)), "done": False}]
    u["txs"] = [{"kind": "Zakat", "amt": 20000, "to": "Charity A", "date": str(TODAY)}, {"kind": "Sadaqah", "amt": 5000, "to": "Local masjid", "date": str(TODAY)}, {"kind": "Sadaqah", "amt": 3000, "to": "Orphanage", "date": str(TODAY)}]
    u["rem"] = [{"t": "Pay electricity bill", "d": str(TODAY + dt.timedelta(days=3))}, {"t": "Qurbani saving transfer", "d": str(TODAY + dt.timedelta(days=12))}]
    u["hist"] = [{"d": str(TODAY - dt.timedelta(days=30 * (5 - i))), "v": 1450000 + i * 160000 + r.randint(-40000, 40000)} for i in range(6)]
    save()

PAGES = ["🏠 Dashboard", "💰 Assets", "🧮 Zakat", "💸 Income & Expenses", "🎯 Goals", "🤝 Qarz (Loans)", "📈 Invest", "🤲 Giving", "🌙 Seasonal", "⚖️ Inheritance", "⏰ Reminders", "📚 Learn", "📄 Reports", "⚙️ Profile"]
KEYS = {"gold": 1, "silver": 1, "nisab": 2, "zakat": 2, "budget": 3, "expense": 3, "income": 3, "hajj": 4, "umrah": 4, "goal": 4, "saving": 4, "loan": 5, "qarz": 5, "bc": 5, "committee": 5, "debt": 5, "sip": 6, "invest": 6, "halal": 6,
        "sadaqah": 7, "charity": 7, "fitrana": 8, "qurbani": 8, "ramadan": 8, "inherit": 9, "faraid": 9, "will": 9, "remind": 10, "learn": 11, "riba": 11, "report": 12, "photo": 13, "profile": 13}
with st.sidebar:
    if u["photo"]: st.markdown(f'<img class="av" src="data:image/png;base64,{u["photo"]}">', unsafe_allow_html=True)
    st.subheader(f"Assalamualaikum, {u['name'].split()[0]}")
    page = st.radio("Menu", PAGES, label_visibility="collapsed")
    q = st.text_input("🔎 Search (gold, hajj, bc, sip...)").lower().strip()
    for k, i in KEYS.items():
        if q and q in k: st.info(f"Try → {PAGES[i]}"); break
    st.caption("Dark / light: ⋮ menu (top right) → Settings → Theme.")
    if st.button("Log out"): st.session_state.me = None; st.rerun()

# ---------------- pages ----------------
def dashboard():
    nz = next_zakat(); days = (nz - TODAY).days; h = Gregorian(nz.year, nz.month, nz.day).to_hijri()
    hero(f"Next zakat date in {days} days ({h.day} {h.month_name()} {h.year} AH). Here is how your money is doing.", f"Welcome back, {u['name'].split()[0]} ✨")
    if not u["assets"] and not u["flow"]:
        st.info("Your dashboard is empty. Add your own data, or load sample data to see how it looks.")
        if st.button("✨ Load sample data", type="primary"): demo_data(); st.rerun()
    df = month_df(); inc = df[df.kind == "Income"].amt.sum(); exp = df[df.kind == "Expense"].amt.sum()
    metal = sum(val(a) for a in u["assets"] if a["type"][:4] in ("Gold", "Silv"))
    for col, args in zip(st.columns(5), [("Net worth", fmt(net), "e", "💰"), ("Zakat due", fmt(due), "g", "🕌"), ("Gold + silver", fmt(metal), "s", "🪙"), ("Saved (all time)", fmt(inc - exp), "b", "🐷"), ("Given", fmt(sum(t["amt"] for t in u["txs"])), "r", "🤲")]):
        col.markdown(tile(*args), unsafe_allow_html=True)
    a, b, c3 = st.columns([1, 1.1, 1.4])
    with a:
        f = go.Figure(go.Indicator(mode="gauge+number", value=barakah_score(), title={"text": "Barakah score ✨"}, gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#0b8a63"},
            "steps": [{"range": [0, 40], "color": "#f3d6cf"}, {"range": [40, 70], "color": "#f7e8b8"}, {"range": [70, 100], "color": "#cdeedd"}]})); style(f, 280)
        st.caption("Mixes savings rate, zakat paid and goal progress.")
    with b:
        rows = [(a_["type"], val(a_)) for a_ in u["assets"]]
        if rows: style(px.pie(pd.DataFrame(rows, columns=["t", "v"]).groupby("t").sum().reset_index(), names="t", values="v", hole=.55, title="Where your wealth sits"), 280)
    with c3:
        if len(u["hist"]) > 1:
            f = px.area(pd.DataFrame(u["hist"]), x="d", y="v", title="Net worth over time"); f.update_traces(line_color="#0b8a63", fillcolor="rgba(11,138,99,.25)"); style(f, 280)
    a, b = st.columns(2)
    with a:
        if len(df): style(px.bar(df.groupby(["m", "kind"]).amt.sum().reset_index(), x="m", y="amt", color="kind", barmode="group", title="Income vs expenses", color_discrete_map={"Income": "#0b8a63", "Expense": "#e27d60"}))
    with b:
        e = df[df.kind == "Expense"]
        if len(e): style(px.treemap(e.groupby("cat").amt.sum().reset_index(), path=["cat"], values="amt", title="Where your money goes"))
    a, b, c3 = st.columns(3)
    with a:
        st.markdown("##### 🎯 Goals")
        for g in u["goals"]: st.write(f"{g['icon']} **{g['name']}**: {fmt(g['saved'])} / {fmt(g['target'])}"); st.progress(min(1.0, g["saved"] / g["target"]))
        if not u["goals"]: st.caption("No goals yet.")
    with b:
        st.markdown("##### ⏰ Coming up")
        items = [("🪙 Zakat due", str(nz))] + [(r["t"], r["d"]) for r in u["rem"]] + [(f"🤝 {x['who']}", x["due"]) for x in u["qarz"] if not x["done"]]
        for t, d in sorted(items, key=lambda x: x[1])[:5]:
            left = (dt.date.fromisoformat(d) - TODAY).days; st.markdown(f'<div class="rem {"late" if left < 0 else "soon" if left <= 7 else ""}"><b>{t}</b><br>{d} · {left} days</div>', unsafe_allow_html=True)
    with c3:
        if u["txs"]: style(px.bar(pd.DataFrame(u["txs"]).groupby("kind").amt.sum().reset_index(), x="kind", y="amt", color="kind", title="Your giving"), 260)
    tips = ["Pay zakat as soon as it is due. Do not delay without reason.", "Save first, spend second: move savings out on payday.", "Avoid riba: choose Islamic savings and halal-screened funds.", "A small regular sadaqah beats a big occasional one.", "Write down every loan. It protects friendships."]
    st.markdown(f'<div class="tip">💡 <b>Tip of the day:</b> {tips[TODAY.toordinal() % len(tips)]}</div>', unsafe_allow_html=True)

def assets():
    st.header("💰 Assets"); c1, c2, c3 = st.columns([2, 2, 3])
    t = c1.selectbox("Type", ASSET_TYPES); amt = c2.number_input("Amount (Rs, or grams)", min_value=0.0, step=100.0); note = c3.text_input("Note")
    if st.button("Add asset", type="primary") and amt > 0: u["assets"].append({"type": t, "amt": amt, "note": note}); save(); st.rerun()
    for i, a in enumerate(u["assets"]):
        x, y = st.columns([6, 1]); x.markdown(f'<div class="card"><b>{a["type"]}</b> {a["note"]}: {fmt(val(a))}</div>', unsafe_allow_html=True)
        if y.button("Remove", key=f"a{i}"): u["assets"].pop(i); save(); st.rerun()

def zakat():
    st.header("🧮 Zakat"); c1, c2 = st.columns(2)
    g = c1.number_input("Gold rate per gram (Rs)", value=float(u["rates"]["gold"])); s = c2.number_input("Silver rate per gram (Rs)", value=float(u["rates"]["silver"]))
    if st.button("Update rates"): u["rates"] = {"gold": g, "silver": s}; save(); st.rerun()
    a, b, c = st.columns(3); a.metric("Assets + loans owed to you", fmt(pos)); b.metric("Debts", fmt(debt)); c.metric("Nisab (silver)", fmt(nisab))
    style(go.Figure(go.Waterfall(x=["Assets", "Debts", "Net", "Zakat 2.5%"], y=[pos, -debt, 0, due], measure=["relative", "relative", "total", "relative"])), 280)
    if net >= nisab: st.success(f"Zakat due: {fmt(due)}. Paid so far: {fmt(paid())}. Remaining: {fmt(max(0, due - paid()))}")
    else: st.warning("Your net wealth is below nisab, so no zakat is due.")
    st.caption("A calculation guide, not a fatwa. Confirm with your scholar.")

def flow():
    st.header("💸 Income & Expenses"); c1, c2, c3, c4 = st.columns(4)
    k = c1.selectbox("Kind", ["Income", "Expense"]); cat = c2.selectbox("Category", ["Salary", "Business", "Other income"] if k == "Income" else EXP_CATS)
    amt = c3.number_input("Amount (Rs)", min_value=0.0, step=500.0); d = c4.date_input("Date", TODAY)
    if st.button("Add entry", type="primary") and amt > 0: u["flow"].append({"kind": k, "cat": cat, "amt": amt, "date": str(d)}); save(); st.rerun()
    df = month_df()
    if len(df):
        m = df[df.m == df.m.max()]; inc = m[m.kind == "Income"].amt.sum(); exp = m[m.kind == "Expense"].amt.sum()
        a, b, c = st.columns(3); a.metric("Income (latest month)", fmt(inc)); b.metric("Expenses", fmt(exp)); c.metric("Saved", fmt(inc - exp))
        if inc:
            needs = m[(m.kind == "Expense") & m.cat.isin(["Food", "Rent", "Bills", "Transport", "Education", "Health"])].amt.sum()
            style(px.pie(names=["Needs", "Wants", "Savings + giving"], values=[needs, exp - needs, max(0, inc - exp)], hole=.5, title="Latest month: needs / wants / savings"), 260)
        st.dataframe(df.drop(columns="m").sort_values("date", ascending=False), width="stretch")

def goals():
    st.header("🎯 Goals"); c1, c2, c3, c4 = st.columns(4)
    pre = c1.selectbox("Preset", ["Hajj", "Umrah", "Qurbani", "Emergency fund", "House", "Education", "Custom"]); name = c2.text_input("Name", pre)
    tg = c3.number_input("Target (Rs)", min_value=0.0, step=10000.0); sv = c4.number_input("Saved so far", min_value=0.0, step=5000.0)
    icon = {"Hajj": "🕋", "Umrah": "🕌", "Qurbani": "🐐", "Emergency fund": "🛟", "House": "🏠", "Education": "🎓"}.get(pre, "⭐")
    if st.button("Add goal", type="primary") and tg > 0: u["goals"].append({"name": name, "icon": icon, "target": tg, "saved": sv}); save(); st.rerun()
    for i, g in enumerate(u["goals"]):
        p = min(1.0, g["saved"] / g["target"]); st.markdown(f"### {g['icon']} {g['name']}"); st.progress(p, text=f"{p:.0%}: {fmt(g['saved'])} of {fmt(g['target'])}")
        a, b, c = st.columns([2, 1, 1]); add = a.number_input("Add savings", min_value=0.0, step=1000.0, key=f"ga{i}")
        if b.button("Save", key=f"gs{i}"): g["saved"] += add; save(); st.rerun()
        if c.button("Delete", key=f"gd{i}"): u["goals"].pop(i); save(); st.rerun()
        mo = st.slider("Months to reach it", 1, 120, 24, key=f"gm{i}"); st.caption(f"Save about {fmt(max(0, g['target'] - g['saved']) / mo)} per month.")

def qarz():
    st.header("🤝 Qarz (Loans)"); st.caption("Loans owed to you count as assets for zakat, and debts you owe are deducted.")
    c1, c2, c3, c4 = st.columns(4); who = c1.text_input("Person"); dr = c2.selectbox("Direction", ["Owed to me", "I owe"]); amt = c3.number_input("Amount (Rs)", min_value=0.0, step=1000.0); dd = c4.date_input("Due date", TODAY + dt.timedelta(days=30))
    if st.button("Add loan", type="primary") and amt > 0 and who: u["qarz"].append({"who": who, "dir": dr, "amt": amt, "due": str(dd), "done": False}); save(); st.rerun()
    for i, x in enumerate(u["qarz"]):
        c, y = st.columns([6, 1]); c.markdown(f'<div class="card">{"🟢" if x["dir"] == "Owed to me" else "🔴"} <b>{x["who"]}</b> · {x["dir"]} · {fmt(x["amt"])} · due {x["due"]} {"✅ settled" if x["done"] else ""}</div>', unsafe_allow_html=True)
        if y.button("Reopen" if x["done"] else "Settle", key=f"q{i}"): x["done"] = not x["done"]; save(); st.rerun()

def invest():
    st.header("📈 Invest"); st.caption("Education only. Not a recommendation to buy or sell anything.")
    t1, t2, t3 = st.tabs(["Growth calculator", "Compare options", "Halal screen"])
    with t1:
        a, b, c, d = st.columns(4); m = a.number_input("Monthly amount (Rs)", 1000.0, value=20000.0, step=1000.0); yrs = b.slider("Years", 1, 40, 15)
        r = c.slider("Expected yearly return %", 0.0, 30.0, 12.0); inf = d.slider("Inflation %", 0.0, 30.0, 8.0); rows = []; bal = 0.0
        for y in range(1, yrs + 1):
            for _ in range(12): bal = (bal + m) * (1 + r / 1200)
            rows.append({"Year": y, "Invested": m * 12 * y, "Nominal value": bal, "Today's money": bal / (1 + inf / 100) ** y})
        df = pd.DataFrame(rows); style(px.line(df, x="Year", y=["Invested", "Nominal value", "Today's money"], title="What your monthly savings could become"), 340)
        real = df.iloc[-1]["Today's money"]; st.success(f"After {yrs} years: {fmt(bal)} (about {fmt(real)} in today's money)")
    with t2:
        inf = st.slider("Inflation %", 0.0, 30.0, 8.0, key="i2"); base = {"Gold": 10.0, "Islamic savings": 9.0, "Islamic fund": 14.0, "Property": 12.0}
        rr = {k: st.slider(f"{k}: assumed yearly return %", -10.0, 30.0, v, key=k) for k, v in base.items()}
        df = pd.DataFrame({"Option": list(rr), "Assumed return": list(rr.values()), "Real return": [v - inf for v in rr.values()]})
        style(px.bar(df, x="Option", y=["Assumed return", "Real return"], barmode="group", title="Return vs real return (%)"), 300)
        st.dataframe(pd.DataFrame({"Option": list(rr), "Risk": ["Medium", "Low", "Medium-High", "Medium"], "Liquidity": ["High", "High", "Medium", "Low"], "Check": ["Physical or Shariah-compliant", "Profit-sharing, no riba", "Shariah board approved", "Halal financing only"]}), width="stretch")
    with t3:
        st.write("Quick screen for a company. This is a rough guide; confirm with the official Shariah-compliant index or your fund's Shariah board.")
        c1, c2, c3 = st.columns(3); dr = c1.number_input("Interest-bearing debt / market cap %", 0.0, 100.0, 20.0); ir = c2.number_input("Non-halal income %", 0.0, 100.0, 2.0); act = c3.selectbox("Core business halal?", ["Yes", "No"])
        ok = [act == "Yes", dr < 37, ir < 5]; st.progress(sum(ok) / 3)
        (st.success if all(ok) else st.error)("Passes the quick screen" if all(ok) else "Does not pass the quick screen")

def giving():
    st.header("🤲 Giving"); c1, c2, c3 = st.columns(3); k = c1.selectbox("Type", ["Zakat", "Sadaqah", "Fidya", "Kaffara", "Fitrana"]); amt = c2.number_input("Amount (Rs)", min_value=0.0, step=500.0); to = c3.text_input("Given to")
    if st.button("Save record", type="primary") and amt > 0: u["txs"].append({"kind": k, "amt": amt, "to": to or "-", "date": str(TODAY)}); save(); st.rerun()
    if u["txs"]:
        df = pd.DataFrame(u["txs"]); a, b = st.columns(2)
        with a: style(px.pie(df.groupby("kind").amt.sum().reset_index(), names="kind", values="amt", hole=.5, title="By type"), 280)
        with b: style(px.bar(df.groupby("to").amt.sum().reset_index(), x="to", y="amt", title="By recipient"), 280)
        st.dataframe(df, width="stretch"); st.download_button("Export CSV", df.to_csv(index=False), "giving.csv")

def seasonal():
    st.header("🌙 Seasonal"); t1, t2 = st.tabs(["Fitrana", "Qurbani saving"])
    with t1:
        a, b = st.columns(2); n = a.number_input("People in your family", 1, 50, 5); r = b.number_input("Fitrana per person (Rs, use this year's announced rate)", 0.0, value=300.0)
        st.metric("Total fitrana", fmt(n * r))
    with t2:
        a, b = st.columns(2); price = a.number_input("Animal price (Rs)", 0.0, value=120000.0, step=5000.0); sh = b.selectbox("Type", ["Goat / sheep (1 share)", "Cow / camel (1 of 7 shares)"])
        cost = price if sh.startswith("Goat") else price / 7; mo = st.slider("Months until Eid ul Adha", 1, 12, 6); st.metric("Your cost", fmt(cost)); st.metric("Save per month", fmt(cost / mo))

def inherit():
    st.header("⚖️ Inheritance (simplified)"); st.warning("Covers only spouse, parents and children. Real cases can be more complex. Always confirm with a scholar or darul-ifta.")
    c1, c2 = st.columns(2); estate = c1.number_input("Net estate after debts and funeral (Rs)", 0.0, value=10000000.0, step=100000.0); who = c2.selectbox("The deceased was", ["Male (wife may inherit)", "Female (husband may inherit)"])
    a, b, c, d, e = st.columns(5); sp = a.checkbox("Spouse alive"); fa = b.checkbox("Father alive"); mo = c.checkbox("Mother alive"); sons = d.number_input("Sons", 0, 20); dau = e.number_input("Daughters", 0, 20)
    kids = sons + dau > 0; sh = {}
    if sp: sh["Spouse"] = (1 / 8 if kids else 1 / 4) if who.startswith("Male") else (1 / 4 if kids else 1 / 2)
    if mo: sh["Mother"] = 1 / 6 if kids else 1 / 3
    if fa and kids: sh["Father"] = 1 / 6
    if dau and not sons: sh["Daughters"] = 1 / 2 if dau == 1 else 2 / 3
    fixed = sum(sh.values())
    if fixed > 1: sh = {k: v / fixed for k, v in sh.items()}; fixed = 1
    rest = 1 - fixed
    if sons: sh["Sons and daughters (2:1)"] = rest
    elif fa and not kids: sh["Father"] = rest
    elif fa and dau: sh["Father"] = sh.get("Father", 0) + rest
    if not sh: st.info("Select at least one heir."); return
    if sum(sh.values()) < 0.999: st.caption("A remainder exists that goes to other relatives, which this tool does not cover.")
    st.dataframe(pd.DataFrame({"Heir": list(sh), "Share": [f"{v:.3f}" for v in sh.values()], "Amount": [fmt(v * estate) for v in sh.values()]}), width="stretch")
    style(px.pie(names=list(sh), values=list(sh.values()), hole=.5), 280)

def reminders():
    st.header("⏰ Reminders"); nz = next_zakat(); st.markdown(f'<div class="rem soon">🪙 <b>Zakat due</b>: {nz} ({(nz - TODAY).days} days)</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([3, 2]); t = c1.text_input("New reminder (bill, fitrana, loan...)"); d = c2.date_input("Date", TODAY)
    if st.button("Add reminder", type="primary") and t: u["rem"].append({"t": t, "d": str(d)}); save(); st.rerun()
    for i, r in sorted(enumerate(u["rem"]), key=lambda x: x[1]["d"]):
        left = (dt.date.fromisoformat(r["d"]) - TODAY).days; x, y = st.columns([6, 1])
        x.markdown(f'<div class="rem {"late" if left < 0 else "soon" if left <= 7 else ""}"><b>{r["t"]}</b>: {r["d"]} ({"overdue" if left < 0 else f"{left} days left"})</div>', unsafe_allow_html=True)
        if y.button("Done", key=f"r{i}"): u["rem"].pop(i); save(); st.rerun()

def learn():
    st.header("📚 Learn")
    for t, b in {"What is nisab?": "Nisab is the minimum wealth after which zakat becomes due. Many scholars use the silver nisab (612.36 g) for cash and mixed wealth. Zakat is generally 2.5% of net zakatable wealth held for one lunar year.",
                 "What is riba?": "Riba is interest, or any guaranteed extra on a loan. Islamic finance uses trade, leasing and profit-sharing instead. Look for products approved by a Shariah board.",
                 "Is a committee (BC) zakatable?": "Scholars discuss this in detail. In general, money you have received or are owed counts as wealth. Ask your scholar about your exact case.",
                 "Budgeting the halal way": "Plan needs first, keep a regular share for savings, and set aside sadaqah. Avoid waste and unnecessary debt.",
                 "Why write down loans?": "The Quran advises writing down debts (Surah Al-Baqarah 2:282). The Qarz module helps you do this."}.items():
        with st.expander(t): st.write(b)

def reports():
    st.header("📄 Reports"); nz = next_zakat()
    md = f"# Zakhira report for {u['name']} ({TODAY})\n\n- Net worth: {fmt(net)}\n- Assets: {fmt(pos)}\n- Debts: {fmt(debt)}\n- Nisab: {fmt(nisab)}\n- Zakat due: {fmt(due)}\n- Zakat paid: {fmt(paid())}\n- Next zakat date: {nz}\n\n## Assets\n" + "".join(f"- {a['type']} {a['note']}: {fmt(val(a))}\n" for a in u["assets"]) + "\n*A guide, not a fatwa.*\n"
    st.markdown(md); st.download_button("Download report (Markdown)", md, "zakhira-report.md")
    if u["flow"]: st.download_button("Download income and expenses (CSV)", pd.DataFrame(u["flow"]).to_csv(index=False), "flow.csv")

def profile():
    st.header("⚙️ Profile")
    if u["photo"]: st.markdown(f'<img class="av" src="data:image/png;base64,{u["photo"]}">', unsafe_allow_html=True)
    up = st.file_uploader("Profile photo", type=["png", "jpg", "jpeg"]); n = st.text_input("Name", u["name"]); zd = st.date_input("Zakat date", dt.date.fromisoformat(u["zdate"]))
    if st.button("Save profile", type="primary"):
        u["name"] = n; u["zdate"] = str(zd)
        if up: u["photo"] = base64.b64encode(up.getvalue()).decode()
        save(); st.rerun()
    st.divider()
    if st.button("✨ Load sample data (replaces your data)"): demo_data(); st.rerun()

dict(zip(PAGES, [dashboard, assets, zakat, flow, goals, qarz, invest, giving, seasonal, inherit, reminders, learn, reports, profile]))[page]()

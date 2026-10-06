import sqlite3, random, datetime as dt
import pandas as pd
import streamlit as st
from pathlib import Path

LOGO = Path(__file__).parent / "assets" / "logo.png"

def show_logo():
    for p in (LOGO, Path(__file__).parent / "logo.png", Path(__file__).parent / "Oromia_bank.png"):
        if p.exists():
            st.image(str(p)); return
    st.markdown("## 🏦 Oromia Bank")

GREEN, BLUE = "#8DC63F", "#5557A8"
DB = str(Path(__file__).parent / "pension.db")
st.set_page_config(page_title="Oromia Bank Pension System", page_icon="🏦", layout="wide")

# ---------------- Translations ----------------
T = {
 "English": {"home": "My Summary", "pay": "My Payments", "pol": "Proof of Life", "loc": "Branch & Agent Locator",
             "sup": "Support", "prof": "My Profile", "hello": "Welcome", "next": "Next payment"},
 "Afaan Oromo": {"home": "Cuunfaa Koo", "pay": "Kaffaltii Koo", "pol": "Mirkaneessa Jiraachuu", "loc": "Damee fi Ejensii Barbaadi",
             "sup": "Deeggarsa", "prof": "Piroofaayilii Koo", "hello": "Baga nagaan dhufte", "next": "Kaffaltii itti aanu"},
 "አማርኛ": {"home": "ማጠቃለያ", "pay": "ክፍያዎቼ", "pol": "ሕይወት ማረጋገጫ", "loc": "ቅርንጫፍና ወኪል ፈልግ",
             "sup": "ድጋፍ", "prof": "መገለጫዬ", "hello": "እንኳን ደህና መጡ", "next": "ቀጣይ ክፍያ"},
}
STAFF = {"officer": ("Branch Officer", "1234"), "maker": ("Payroll Officer (Maker)", "1234"),
         "checker": ("Payroll Approver (Checker)", "1234"), "fraud": ("Fraud Analyst", "1234"),
         "admin": ("System Admin", "1234")}
BRANCHES = ["Finfinne Main", "Adama", "Jimma", "Bishoftu", "Nekemte", "Shashamane", "Ambo", "Asella"]

# ---------------- Database ----------------
def con():
    return sqlite3.connect(DB, check_same_thread=False)

def init_db():
    c = con()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS pensioners(id TEXT PRIMARY KEY,name TEXT,nid TEXT,phone TEXT,gender TEXT,dob TEXT,
      branch TEXT,amount REAL,status TEXT,channel TEXT,account TEXT,last_pol TEXT,lang TEXT);
    CREATE TABLE IF NOT EXISTS batches(id INTEGER PRIMARY KEY AUTOINCREMENT,month TEXT,eligible INT,excluded INT,
      total REAL,status TEXT,maker TEXT,checker TEXT,created TEXT);
    CREATE TABLE IF NOT EXISTS payments(id INTEGER PRIMARY KEY AUTOINCREMENT,batch INT,pid TEXT,amount REAL,status TEXT,date TEXT);
    CREATE TABLE IF NOT EXISTS tickets(id INTEGER PRIMARY KEY AUTOINCREMENT,pid TEXT,type TEXT,msg TEXT,status TEXT,created TEXT);
    CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY AUTOINCREMENT,ts TEXT,user TEXT,action TEXT);
    """)
    if c.execute("SELECT COUNT(*) FROM pensioners").fetchone()[0] == 0:
        random.seed(7)
        first = ["Abebe", "Chaltu", "Dida", "Gemechu", "Hawi", "Jaalala", "Kadir", "Lensa", "Mulu", "Nuuraa", "Obsaa", "Tolasa", "Ukkee", "Bekele", "Tigist"]
        last = ["Tadesse", "Bulti", "Gudina", "Kebede", "Lemma", "Fufa", "Wakjira", "Dinsa", "Negasa", "Hirpa"]
        today = dt.date.today()
        rows = []
        for i in range(1, 61):
            st_ = random.choices(["Active", "Suspended", "Deceased"], [80, 12, 8])[0]
            pol = today - dt.timedelta(days=random.randint(10, 500))
            rows.append((f"P{i:04d}", f"{random.choice(first)} {random.choice(last)}", f"ID{random.randint(10**9, 10**10-1)}",
                         f"09{random.randint(10000000, 99999999)}", random.choice(["M", "F"]), str(dt.date(random.randint(1938, 1964), random.randint(1, 12), random.randint(1, 28))),
                         random.choice(BRANCHES), random.randint(1500, 9500), st_, random.choice(["Bank Account", "Agent Cash-out", "Wallet"]),
                         f"1000{random.randint(10**8, 10**9-1)}", str(pol), random.choice(["Afaan Oromo", "አማርኛ", "English"])))
        c.executemany("INSERT INTO pensioners VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
        c.execute("UPDATE pensioners SET phone=(SELECT phone FROM pensioners WHERE id='P0001') WHERE id='P0002'")  # seeded fraud example
        c.commit()
    c.close()

def q(sql, p=()):
    c = con(); df = pd.read_sql_query(sql, c, params=p); c.close(); return df

def run(sql, p=()):
    c = con(); c.execute(sql, p); c.commit(); c.close()

def log(action):
    run("INSERT INTO audit(ts,user,action) VALUES(?,?,?)", (dt.datetime.now().strftime("%Y-%m-%d %H:%M"), st.session_state.get("user", "-"), action))

def pol_due(d):
    return (dt.date.today() - dt.date.fromisoformat(d)).days > 365

# ---------------- Styling ----------------
def style(large=False):
    fs = "1.35rem" if large else "1rem"
    st.markdown(f"""<style>
    html, body, [class*="css"] {{ font-size:{fs}; }}
    .hdr {{background:linear-gradient(90deg,{GREEN},{BLUE});padding:14px 20px;border-radius:12px;color:white;margin-bottom:14px}}
    .hdr h2 {{margin:0;color:white}}
    .card {{background:#F1F7E6;border-left:6px solid {GREEN};padding:14px;border-radius:10px;margin-bottom:10px}}
    div.stButton>button {{background:{BLUE};color:white;border-radius:8px;border:0}}
    div.stButton>button:hover {{background:{GREEN};color:#222}}
    </style>""", unsafe_allow_html=True)

def header(title, sub=""):
    st.markdown(f'<div class="hdr"><h2>{title}</h2><span>{sub}</span></div>', unsafe_allow_html=True)

# ---------------- Login ----------------
def login():
    style()
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        show_logo()
        st.markdown("### Pension Payment System · Sirna Kaffaltii Fayyadaa")
        role = st.radio("Sign in as", ["Pensioner", "Bank Staff"], horizontal=True)
        if role == "Pensioner":
            pid = st.text_input("Pension ID (e.g. P0001)")
            pin = st.text_input("PIN (demo: 1234)", type="password")
            if st.button("Sign in", use_container_width=True):
                r = q("SELECT * FROM pensioners WHERE id=?", (pid.strip().upper(),))
                if len(r) and pin == "1234":
                    st.session_state.update(role="pensioner", user=r.iloc[0]["id"]); st.rerun()
                else:
                    st.error("Invalid ID or PIN")
        else:
            u = st.selectbox("Staff user", list(STAFF))
            pin = st.text_input("Password (demo: 1234)", type="password")
            if st.button("Sign in", use_container_width=True):
                if pin == STAFF[u][1]:
                    st.session_state.update(role="staff", user=u); log("Login"); st.rerun()
                else:
                    st.error("Wrong password")
        st.caption("Demo system with sample data only. Try pensioner P0001 / 1234.")

# ---------------- Pensioner portal ----------------
def pensioner_portal():
    p = q("SELECT * FROM pensioners WHERE id=?", (st.session_state.user,)).iloc[0]
    with st.sidebar:
        show_logo()
        lang = st.selectbox("Language / Afaan / ቋንቋ", list(T), index=list(T).index(p["lang"]))
        large = st.toggle("Large text", value=True)
        t = T[lang]
        page = st.radio("Menu", [t[k] for k in ["home", "pay", "pol", "loc", "sup", "prof"]])
        if st.button("Sign out"): st.session_state.clear(); st.rerun()
    style(large)
    header(f"{t['hello']}, {p['name']}", f"Pension ID {p['id']} · {p['branch']} branch")
    if page == t["home"]:
        c1, c2, c3 = st.columns(3)
        c1.metric("Monthly pension (ETB)", f"{p['amount']:,.0f}")
        c2.metric("Status", p["status"])
        c3.metric(t["next"], (dt.date.today().replace(day=28)).strftime("%d %b %Y"))
        if pol_due(p["last_pol"]):
            st.warning("⚠️ Your proof of life is overdue. Visit a branch or agent to avoid suspension.")
        else:
            st.success("✅ Proof of life is up to date.")
        st.info("Never share your PIN. Bank staff and agents never ask for fees to process pensions.")
    elif page == t["pay"]:
        df = q("SELECT date,amount,status,batch FROM payments WHERE pid=? ORDER BY id DESC", (p["id"],))
        if df.empty: st.info("No payments yet. Payments appear after the monthly payroll is approved.")
        else:
            st.dataframe(df, use_container_width=True)
            st.download_button("Download statement (CSV)", df.to_csv(index=False), "statement.csv")
        if st.button("Report wrong or missing payment"):
            run("INSERT INTO tickets(pid,type,msg,status,created) VALUES(?,?,?,?,?)", (p["id"], "Missing payment", "Reported from payments page", "Open", str(dt.date.today())))
            st.success("Ticket opened. You will receive an SMS update.")
    elif page == t["pol"]:
        st.markdown(f'<div class="card">Last verified: <b>{p["last_pol"]}</b><br>Due before: <b>{dt.date.fromisoformat(p["last_pol"]) + dt.timedelta(days=365)}</b></div>', unsafe_allow_html=True)
        m = st.radio("Verification method", ["Branch / agent (fingerprint)", "Selfie with liveness check", "Home visit (bedridden)", "Trusted witness"])
        if m.startswith("Selfie"):
            img = st.camera_input("Take a clear selfie")
            if img and st.button("Submit selfie"):
                run("UPDATE pensioners SET last_pol=? WHERE id=?", (str(dt.date.today()), p["id"])); st.success("Proof of life recorded. Thank you!"); st.rerun()
        elif st.button("Request this method"):
            run("INSERT INTO tickets(pid,type,msg,status,created) VALUES(?,?,?,?,?)", (p["id"], "PoL request", m, "Open", str(dt.date.today())))
            st.success("Request sent. A bank officer will contact you.")
    elif page == t["loc"]:
        town = st.selectbox("Town", BRANCHES)
        st.markdown(f'<div class="card"><b>Oromia Bank – {town} Branch</b><br>Mon–Fri 8:30–17:00 · Services: PoL, cash-out, onboarding</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card"><b>Agent – {town} Kebele 02</b><br>Cash available · Services: cash-out, PoL</div>', unsafe_allow_html=True)
    elif page == t["sup"]:
        with st.form("tk"):
            typ = st.selectbox("Issue", ["Missing payment", "Wrong amount", "PoL issue", "Profile change", "Survivor claim", "Fraud report"])
            msg = st.text_area("Describe the problem")
            if st.form_submit_button("Submit"):
                run("INSERT INTO tickets(pid,type,msg,status,created) VALUES(?,?,?,?,?)", (p["id"], typ, msg, "Open", str(dt.date.today()))); st.success("Ticket created")
        st.dataframe(q("SELECT id,type,status,created FROM tickets WHERE pid=?", (p["id"],)), use_container_width=True)
    else:
        st.write({"Name": p["name"], "National ID": p["nid"], "Phone": p["phone"], "Payout channel": p["channel"], "Account": p["account"]})
        ch = st.selectbox("Request payout channel change", ["Bank Account", "Agent Cash-out", "Wallet"])
        if st.button("Submit for approval"):
            run("INSERT INTO tickets(pid,type,msg,status,created) VALUES(?,?,?,?,?)", (p["id"], "Profile change", f"Channel -> {ch}", "Pending approval", str(dt.date.today()))); st.success("Sent for maker-checker approval")

# ---------------- Staff console ----------------
def staff_console():
    u = st.session_state.user; role = STAFF[u][0]
    with st.sidebar:
        show_logo(); st.caption(f"👤 {role}")
        page = st.radio("Menu", ["Dashboard", "Pensioner Admin", "Payroll", "Proof of Life", "Fraud & Risk", "Support Console", "Reports", "Audit Log"])
        if st.button("Sign out"): st.session_state.clear(); st.rerun()
    style(); header(page, role)
    P = q("SELECT * FROM pensioners")
    if page == "Dashboard":
        P["due"] = P["last_pol"].apply(pol_due)
        c = st.columns(4)
        c[0].metric("Pensioners", len(P)); c[1].metric("Active", int((P.status == "Active").sum()))
        c[2].metric("PoL overdue", int(P.due.sum())); c[3].metric("Monthly liability (ETB)", f"{P[P.status=='Active'].amount.sum():,.0f}")
        a, b = st.columns(2)
        a.subheader("By branch"); a.bar_chart(P.groupby("branch").size())
        b.subheader("By status"); b.bar_chart(P.groupby("status").size())
    elif page == "Pensioner Admin":
        s = st.text_input("Search name / ID / phone / national ID")
        d = P[P.apply(lambda r: s.lower() in " ".join(map(str, r.values)).lower(), axis=1)] if s else P
        st.dataframe(d, use_container_width=True, height=300)
        with st.expander("➕ Register new pensioner"):
            with st.form("reg"):
                n = st.text_input("Full name"); nid = st.text_input("National ID"); ph = st.text_input("Phone")
                g = st.selectbox("Gender", ["M", "F"]); dob = st.date_input("Date of birth", dt.date(1955, 1, 1), min_value=dt.date(1920, 1, 1))
                br = st.selectbox("Branch", BRANCHES); am = st.number_input("Monthly pension (ETB)", 500, 50000, 3000)
                ch = st.selectbox("Channel", ["Bank Account", "Agent Cash-out", "Wallet"]); lg = st.selectbox("Language", list(T))
                if st.form_submit_button("Register"):
                    if (P.nid == nid).any() or (P.phone == ph).any(): st.error("Duplicate National ID or phone detected")
                    elif not n or not nid: st.error("Name and National ID required")
                    else:
                        pid = f"P{len(P)+1:04d}"
                        run("INSERT INTO pensioners VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", (pid, n, nid, ph, g, str(dob), br, am, "Active", ch, f"1000{random.randint(10**8,10**9-1)}", str(dt.date.today()), lg))
                        log(f"Registered {pid}"); st.success(f"Registered {pid}"); st.rerun()
        c1, c2, c3 = st.columns(3)
        pid = c1.selectbox("Change status of", P.id); ns = c2.selectbox("New status", ["Active", "Suspended", "Deceased", "Closed"])
        if c3.button("Apply"): run("UPDATE pensioners SET status=? WHERE id=?", (ns, pid)); log(f"{pid} -> {ns}"); st.rerun()
    elif page == "Payroll":
        st.caption("Maker prepares the batch; a different user (checker) approves. No one can approve their own batch.")
        month = st.text_input("Payroll month", dt.date.today().strftime("%B %Y"))
        if u == "maker" and st.button("Prepare payroll batch"):
            el = P[(P.status == "Active") & (~P.last_pol.apply(pol_due))]
            run("INSERT INTO batches(month,eligible,excluded,total,status,maker,created) VALUES(?,?,?,?,?,?,?)", (month, len(el), len(P) - len(el), float(el.amount.sum()), "Pending approval", u, str(dt.date.today())))
            log(f"Prepared batch {month}"); st.rerun()
        elif u != "maker": st.info("Log in as 'maker' to prepare batches and 'checker' to approve.")
        B = q("SELECT * FROM batches ORDER BY id DESC"); st.dataframe(B, use_container_width=True)
        pend = B[B.status == "Pending approval"]
        if u == "checker" and len(pend):
            bid = st.selectbox("Batch to review", pend.id)
            if st.button("✅ Approve & credit"):
                el = P[(P.status == "Active") & (~P.last_pol.apply(pol_due))]
                for _, r in el.iterrows():
                    run("INSERT INTO payments(batch,pid,amount,status,date) VALUES(?,?,?,?,?)", (int(bid), r.id, r.amount, random.choices(["Credited", "Failed"], [96, 4])[0], str(dt.date.today())))
                run("UPDATE batches SET status='Approved',checker=? WHERE id=?", (u, int(bid))); log(f"Approved batch {bid}"); st.success("Batch approved and payments credited"); st.rerun()
        st.subheader("Exclusions preview")
        ex = P[(P.status != "Active") | (P.last_pol.apply(pol_due))].copy()
        ex["reason"] = ex.apply(lambda r: r.status if r.status != "Active" else "PoL overdue", axis=1)
        st.dataframe(ex[["id", "name", "branch", "reason"]], use_container_width=True)
    elif page == "Proof of Life":
        P["due"] = P.last_pol.apply(pol_due); od = P[(P.due) & (P.status == "Active")]
        st.metric("Overdue (active)", len(od)); st.dataframe(od[["id", "name", "phone", "branch", "last_pol"]], use_container_width=True)
        pid = st.selectbox("Record PoL for", P.id); m = st.selectbox("Method", ["Fingerprint", "Face", "Trusted witness", "Home visit"])
        if st.button("Record verification"): run("UPDATE pensioners SET last_pol=? WHERE id=?", (str(dt.date.today()), pid)); log(f"PoL {pid} via {m}"); st.rerun()
    elif page == "Fraud & Risk":
        pay = q("SELECT pid FROM payments"); al = []
        for ph, g in P.groupby("phone"):
            if len(g) > 1: al.append(("High", "Same phone on multiple pensioners", ", ".join(g.id)))
        for acc, g in P.groupby("account"):
            if len(g) > 1: al.append(("High", "Shared account", ", ".join(g.id)))
        for i in P[(P.status == "Deceased") & P.id.isin(pay.pid)].id: al.append(("Critical", "Payment to deceased pensioner", i))
        for i in P[(P.status == "Active") & P.last_pol.apply(pol_due)].id[:10]: al.append(("Medium", "Active with expired PoL", i))
        st.dataframe(pd.DataFrame(al, columns=["Severity", "Rule", "Pensioner(s)"]), use_container_width=True)
    elif page == "Support Console":
        T_ = q("SELECT * FROM tickets ORDER BY id DESC"); st.dataframe(T_, use_container_width=True)
        if len(T_):
            tid = st.selectbox("Ticket", T_.id); ns = st.selectbox("Set status", ["In progress", "Resolved", "Escalated"])
            if st.button("Update ticket"): run("UPDATE tickets SET status=? WHERE id=?", (ns, int(tid))); log(f"Ticket {tid} {ns}"); st.rerun()
    elif page == "Reports":
        pay = q("SELECT status,COUNT(*) n,SUM(amount) total FROM payments GROUP BY status"); st.subheader("Payment reconciliation"); st.dataframe(pay)
        for name, df in [("pensioners", P), ("payments", q("SELECT * FROM payments"))]:
            st.download_button(f"Export {name} (CSV)", df.to_csv(index=False), f"{name}.csv")
    else:
        st.dataframe(q("SELECT * FROM audit ORDER BY id DESC"), use_container_width=True)

# ---------------- Router ----------------
init_db()
r = st.session_state.get("role")
if r == "pensioner": pensioner_portal()
elif r == "staff": staff_console()
else: login()

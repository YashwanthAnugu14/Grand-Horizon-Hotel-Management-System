import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
from datetime import datetime, date, timedelta
import time

st.set_page_config(page_title="Grand Horizon Hotel", layout="wide", initial_sidebar_state="collapsed")

STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
* { font-family: 'Inter', sans-serif !important; box-sizing: border-box; margin: 0; padding: 0; }
html, body, .stApp { background: #0a0a0f !important; color: #f0f0f5 !important; }
.stApp { background: #0a0a0f !important; }
section[data-testid="stSidebar"] { display: none !important; }
header[data-testid="stHeader"] { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
.main > div { padding: 0 !important; }
button[data-testid="baseButton-secondary"], button[data-testid="baseButton-primary"] {
    background: #7c3aed !important; color: #fff !important; border: none !important;
    border-radius: 12px !important; font-weight: 600 !important; font-size: 14px !important;
    padding: 10px 20px !important; cursor: pointer !important; transition: all 0.2s !important;
}
button[data-testid="baseButton-secondary"]:hover, button[data-testid="baseButton-primary"]:hover {
    background: #6d28d9 !important; transform: translateY(-1px) !important;
}
.stTextInput > div > div > input, .stSelectbox > div > div, .stDateInput > div > div > input,
.stNumberInput > div > div > input, .stTextArea textarea {
    background: #16161f !important; border: 1px solid #2a2a3a !important;
    color: #f0f0f5 !important; border-radius: 10px !important; font-size: 14px !important;
}
.stSelectbox > div > div { background: #16161f !important; border: 1px solid #2a2a3a !important; color: #f0f0f5 !important; border-radius: 10px !important; }
.stSelectbox svg { fill: #a0a0b0 !important; }
[data-baseweb="select"] > div { background: #16161f !important; border-color: #2a2a3a !important; }
[data-baseweb="select"] span { color: #f0f0f5 !important; }
[data-baseweb="popover"] { background: #16161f !important; }
[role="listbox"] { background: #16161f !important; }
[role="option"] { color: #f0f0f5 !important; }
[role="option"]:hover { background: #2a2a3a !important; }
.stDataFrame, [data-testid="stDataFrame"] { background: #16161f !important; border-radius: 12px !important; }
.stDataFrame table { color: #f0f0f5 !important; }
.stDataFrame thead tr th { background: #1e1e2e !important; color: #a78bfa !important; }
.stDataFrame tbody tr:nth-child(even) { background: #13131c !important; }
label { color: #a0a0b0 !important; font-size: 13px !important; font-weight: 500 !important; }
.stAlert { border-radius: 12px !important; }
[data-testid="stMetric"] { background: #16161f !important; border-radius: 14px !important; padding: 16px !important; border: 1px solid #2a2a3a !important; }
[data-testid="stMetricLabel"] { color: #a0a0b0 !important; font-size: 13px !important; }
[data-testid="stMetricValue"] { color: #a78bfa !important; font-size: 28px !important; font-weight: 700 !important; }
[data-testid="stMetricDelta"] { color: #34d399 !important; }
.stTabs [data-baseweb="tab-list"] { background: #13131c !important; border-radius: 14px !important; padding: 4px !important; gap: 4px !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #a0a0b0 !important; border-radius: 10px !important; font-weight: 500 !important; font-size: 14px !important; }
.stTabs [aria-selected="true"] { background: #7c3aed !important; color: #fff !important; }
.stTabs [data-baseweb="tab-panel"] { background: transparent !important; padding-top: 20px !important; }
.stCheckbox label { color: #f0f0f5 !important; font-size: 14px !important; }
hr { border-color: #2a2a3a !important; }
.stMarkdown p { color: #c0c0d0 !important; }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #13131c; }
::-webkit-scrollbar-thumb { background: #3a3a5a; border-radius: 3px; }
</style>
"""

def card(content, padding="24px", bg="#16161f", border="1px solid #2a2a3a", radius="16px", extra=""):
    return f'<div style="background:{bg};border:{border};border-radius:{radius};padding:{padding};{extra}">{content}</div>'

def badge(text, color="#7c3aed", bg="rgba(124,58,237,0.15)"):
    return f'<span style="background:{bg};color:{color};border-radius:20px;padding:4px 12px;font-size:12px;font-weight:600;">{text}</span>'

def stat_mini(label, value, color="#a78bfa"):
    return f'<div style="text-align:center"><div style="font-size:22px;font-weight:800;color:{color}">{value}</div><div style="font-size:11px;color:#606070;margin-top:2px">{label}</div></div>'

DB = "hotel_system.db"

def get_conn():
    conn = sqlite3.connect(DB, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        status TEXT DEFAULT 'active',
        created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_number TEXT UNIQUE NOT NULL,
        room_type TEXT NOT NULL,
        floor INTEGER NOT NULL,
        rate REAL NOT NULL,
        status TEXT DEFAULT 'Available',
        capacity INTEGER DEFAULT 2,
        amenities TEXT DEFAULT '',
        description TEXT DEFAULT ''
    );
    CREATE TABLE IF NOT EXISTS guests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT,
        id_type TEXT,
        id_number TEXT,
        address TEXT,
        nationality TEXT DEFAULT 'Domestic',
        registered_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guest_id INTEGER NOT NULL,
        room_id INTEGER NOT NULL,
        check_in TEXT NOT NULL,
        check_out TEXT NOT NULL,
        nights INTEGER NOT NULL,
        total_amount REAL NOT NULL,
        status TEXT DEFAULT 'Confirmed',
        payment_mode TEXT DEFAULT 'Cash',
        payment_status TEXT DEFAULT 'Pending',
        special_requests TEXT DEFAULT '',
        created_by INTEGER,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY(guest_id) REFERENCES guests(id),
        FOREIGN KEY(room_id) REFERENCES rooms(id)
    );
    CREATE TABLE IF NOT EXISTS housekeeping (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_id INTEGER NOT NULL,
        status TEXT DEFAULT 'Pending',
        assigned_to TEXT DEFAULT '',
        notes TEXT DEFAULT '',
        updated_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY(room_id) REFERENCES rooms(id)
    );
    CREATE TABLE IF NOT EXISTS maintenance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_id INTEGER NOT NULL,
        issue TEXT NOT NULL,
        priority TEXT DEFAULT 'Normal',
        status TEXT DEFAULT 'Open',
        assigned_to TEXT DEFAULT '',
        notes TEXT DEFAULT '',
        reported_at TEXT DEFAULT (datetime('now')),
        resolved_at TEXT,
        FOREIGN KEY(room_id) REFERENCES rooms(id)
    );
    CREATE TABLE IF NOT EXISTS activity_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT NOT NULL,
        details TEXT DEFAULT '',
        timestamp TEXT DEFAULT (datetime('now'))
    );
    """)
    conn.commit()
    if not c.execute("SELECT id FROM users WHERE username='admin'").fetchone():
        roles = [
            ("admin","Admin","System Administrator","admin"),
            ("frontdesk","Front Desk","Front Desk Staff","staff"),
            ("manager","Manager","Hotel Manager","manager"),
            ("housekeeping","Housekeeping","Housekeeping Staff","housekeeping"),
            ("maintenance","Maintenance","Maintenance Staff","maintenance"),
        ]
        for u,pw,fn,role in roles:
            c.execute("INSERT INTO users (username,password,full_name,role) VALUES (?,?,?,?)",
                      (u, hash_pw(pw), fn, role))
        room_types = [
            ("Standard", 2500, 1),("Standard", 2500, 1),("Standard", 2500, 1),
            ("Deluxe", 4500, 2),("Deluxe", 4500, 2),("Deluxe", 4500, 2),
            ("Suite", 8500, 3),("Suite", 8500, 3),
            ("Presidential", 15000, 4),
            ("Standard", 2500, 1),("Deluxe", 4500, 2),
        ]
        amenity_map = {
            "Standard": "WiFi, TV, AC, Hot Water",
            "Deluxe": "WiFi, TV, AC, Mini-Bar, Balcony",
            "Suite": "WiFi, Smart TV, AC, Jacuzzi, Lounge, Mini-Bar",
            "Presidential": "WiFi, Smart TV, AC, Private Pool, Butler Service, Full Kitchen"
        }
        statuses = ["Available","Available","Available","Available","Occupied","Available","Available","Cleaning","Available","Available","Under Maintenance"]
        for i,(rt,rate,fl) in enumerate(room_types):
            rnum = f"{fl}0{i+1}"
            c.execute("INSERT OR IGNORE INTO rooms (room_number,room_type,floor,rate,status,amenities,description) VALUES (?,?,?,?,?,?,?)",
                      (rnum, rt, fl, rate, statuses[i], amenity_map[rt], f"Comfortable {rt} room on floor {fl}"))
        guests_data = [
            ("Arjun Mehta","9876543210","arjun@email.com","Passport","P123456","Mumbai","International"),
            ("Priya Sharma","9812345678","priya@email.com","Aadhar","A987654","Delhi","Domestic"),
            ("Rahul Verma","9900112233","rahul@email.com","License","L456789","Hyderabad","Domestic"),
            ("Ananya Patel","9711223344","ananya@email.com","Passport","P654321","Bengaluru","International"),
            ("Kiran Rao","9600998877","kiran@email.com","Aadhar","A112233","Chennai","Domestic"),
        ]
        for g in guests_data:
            c.execute("INSERT OR IGNORE INTO guests (name,phone,email,id_type,id_number,address,nationality) VALUES (?,?,?,?,?,?,?)", g)
        today = date.today()
        sample_res = [
            (1,4,str(today - timedelta(2)), str(today+timedelta(1)), 3, 13500, "Checked-In","Card","Paid"),
            (2,5,str(today), str(today+timedelta(2)), 2, 9000, "Confirmed","Cash","Pending"),
            (3,1,str(today - timedelta(5)), str(today - timedelta(2)), 3, 7500, "Checked-Out","UPI","Paid"),
            (4,6,str(today+timedelta(1)), str(today+timedelta(3)), 2, 9000, "Confirmed","Card","Paid"),
            (5,7,str(today - timedelta(1)), str(today+timedelta(1)), 2, 17000, "Checked-In","Cash","Pending"),
        ]
        for r in sample_res:
            c.execute("INSERT OR IGNORE INTO reservations (guest_id,room_id,check_in,check_out,nights,total_amount,status,payment_mode,payment_status) VALUES (?,?,?,?,?,?,?,?,?)", r)
        conn.commit()
    conn.close()

def log_action(user_id, action, details=""):
    conn = get_conn()
    conn.execute("INSERT INTO activity_log (user_id,action,details) VALUES (?,?,?)", (user_id, action, details))
    conn.commit()
    conn.close()

def login_page():
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown("""
    <div style="min-height:100vh;background:linear-gradient(135deg,#0a0a0f 0%,#13131c 50%,#0a0a0f 100%);display:flex;align-items:center;justify-content:center;padding:40px 20px;">
      <div style="width:100%;max-width:900px;">
        <div style="text-align:center;margin-bottom:48px;">
          <div style="display:inline-flex;align-items:center;gap:14px;margin-bottom:20px;">
            <div style="width:52px;height:52px;background:linear-gradient(135deg,#7c3aed,#4f46e5);border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:24px;">H</div>
            <div style="text-align:left">
              <div style="font-size:26px;font-weight:800;color:#f0f0f5;letter-spacing:-0.5px;">Grand Horizon</div>
              <div style="font-size:13px;color:#606070;font-weight:400;">Hotel Management System</div>
            </div>
          </div>
          <div style="font-size:36px;font-weight:800;color:#f0f0f5;line-height:1.2;margin-bottom:12px;">Welcome back</div>
          <div style="font-size:16px;color:#606070;">Sign in to manage your hotel operations</div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;align-items:start;">
          <div style="background:#16161f;border:1px solid #2a2a3a;border-radius:20px;padding:36px;">
            <div style="font-size:18px;font-weight:700;color:#f0f0f5;margin-bottom:24px;">Sign In</div>
    """, unsafe_allow_html=True)
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("Sign In", use_container_width=True)
        with col2:
            register_btn = st.form_submit_button("Register", use_container_width=True)
        if submit:
            if username and password:
                conn = get_conn()
                user = conn.execute("SELECT * FROM users WHERE username=? AND password=? AND status='active'",
                                    (username, hash_pw(password))).fetchone()
                conn.close()
                if user:
                    st.session_state.user = dict(user)
                    st.session_state.page = "dashboard"
                    log_action(user["id"], "Login", f"User {username} logged in")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")
            else:
                st.warning("Please enter both username and password.")
        if register_btn:
            st.session_state.page = "register"
            st.rerun()
    st.markdown("""
          </div>
          <div>
            <div style="background:linear-gradient(135deg,rgba(124,58,237,0.1),rgba(79,70,229,0.1));border:1px solid rgba(124,58,237,0.2);border-radius:20px;padding:28px;margin-bottom:16px;">
              <div style="font-size:15px;font-weight:700;color:#a78bfa;margin-bottom:16px;">System Access Roles</div>
              <div style="display:flex;flex-direction:column;gap:10px;">
                <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 14px;background:rgba(255,255,255,0.03);border-radius:10px;">
                  <span style="color:#c0c0d0;font-size:13px;font-weight:500;">System Administrator</span>
                  <span style="color:#7c3aed;font-size:11px;font-weight:600;background:rgba(124,58,237,0.15);padding:3px 10px;border-radius:20px;">Full Access</span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 14px;background:rgba(255,255,255,0.03);border-radius:10px;">
                  <span style="color:#c0c0d0;font-size:13px;font-weight:500;">Hotel Manager</span>
                  <span style="color:#3b82f6;font-size:11px;font-weight:600;background:rgba(59,130,246,0.15);padding:3px 10px;border-radius:20px;">Reports & Ops</span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 14px;background:rgba(255,255,255,0.03);border-radius:10px;">
                  <span style="color:#c0c0d0;font-size:13px;font-weight:500;">Front Desk Staff</span>
                  <span style="color:#10b981;font-size:11px;font-weight:600;background:rgba(16,185,129,0.15);padding:3px 10px;border-radius:20px;">Reservations</span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 14px;background:rgba(255,255,255,0.03);border-radius:10px;">
                  <span style="color:#c0c0d0;font-size:13px;font-weight:500;">Housekeeping</span>
                  <span style="color:#f59e0b;font-size:11px;font-weight:600;background:rgba(245,158,11,0.15);padding:3px 10px;border-radius:20px;">Room Care</span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 14px;background:rgba(255,255,255,0.03);border-radius:10px;">
                  <span style="color:#c0c0d0;font-size:13px;font-weight:500;">Maintenance</span>
                  <span style="color:#ef4444;font-size:11px;font-weight:600;background:rgba(239,68,68,0.15);padding:3px 10px;border-radius:20px;">Repairs</span>
                </div>
              </div>
            </div>
            <div style="background:#16161f;border:1px solid #2a2a3a;border-radius:16px;padding:20px;">
              <div style="font-size:13px;font-weight:600;color:#a0a0b0;margin-bottom:12px;">System Status</div>
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                <div style="width:8px;height:8px;background:#34d399;border-radius:50%;"></div>
                <span style="color:#c0c0d0;font-size:13px;">All systems operational</span>
              </div>
              <div style="display:flex;align-items:center;gap:8px;">
                <div style="width:8px;height:8px;background:#34d399;border-radius:50%;"></div>
                <span style="color:#c0c0d0;font-size:13px;">Database connected</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

def register_page():
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown("""
    <div style="min-height:100vh;background:#0a0a0f;display:flex;align-items:center;justify-content:center;padding:40px 20px;">
      <div style="width:100%;max-width:600px;">
        <div style="text-align:center;margin-bottom:36px;">
          <div style="font-size:30px;font-weight:800;color:#f0f0f5;margin-bottom:8px;">Create Account</div>
          <div style="font-size:15px;color:#606070;">Register for hotel system access</div>
        </div>
        <div style="background:#16161f;border:1px solid #2a2a3a;border-radius:20px;padding:36px;">
    """, unsafe_allow_html=True)
    with st.form("register_form"):
        c1, c2 = st.columns(2)
        with c1:
            full_name = st.text_input("Full Name", placeholder="Your full name")
        with c2:
            username = st.text_input("Username", placeholder="Choose a username")
        c3, c4 = st.columns(2)
        with c3:
            password = st.text_input("Password", type="password", placeholder="Create password")
        with c4:
            confirm = st.text_input("Confirm Password", type="password", placeholder="Repeat password")
        c5, c6 = st.columns(2)
        with c5:
            email = st.text_input("Email", placeholder="your@email.com")
        with c6:
            phone = st.text_input("Phone", placeholder="Phone number")
        role = st.selectbox("Role", ["staff","housekeeping","maintenance"])
        c7, c8 = st.columns(2)
        with c7:
            submit = st.form_submit_button("Create Account", use_container_width=True)
        with c8:
            back = st.form_submit_button("Back to Login", use_container_width=True)
        if submit:
            if not all([full_name, username, password, confirm]):
                st.error("Please fill in all required fields.")
            elif password != confirm:
                st.error("Passwords do not match.")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                try:
                    conn = get_conn()
                    conn.execute("INSERT INTO users (username,password,full_name,role,email,phone) VALUES (?,?,?,?,?,?)",
                                 (username, hash_pw(password), full_name, role, email, phone))
                    conn.commit()
                    conn.close()
                    st.success("Account created successfully! Please sign in.")
                    time.sleep(1)
                    st.session_state.page = "login"
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("Username already exists. Choose a different one.")
        if back:
            st.session_state.page = "login"
            st.rerun()
    st.markdown("</div></div></div>", unsafe_allow_html=True)

def topbar():
    user = st.session_state.user
    role_colors = {"admin":"#7c3aed","manager":"#3b82f6","staff":"#10b981","housekeeping":"#f59e0b","maintenance":"#ef4444"}
    rc = role_colors.get(user["role"],"#7c3aed")
    st.markdown(f"""
    <div style="background:#13131c;border-bottom:1px solid #2a2a3a;padding:14px 32px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:999;">
      <div style="display:flex;align-items:center;gap:12px;">
        <div style="width:38px;height:38px;background:linear-gradient(135deg,#7c3aed,#4f46e5);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:800;color:#fff;">H</div>
        <div>
          <div style="font-size:15px;font-weight:700;color:#f0f0f5;">Grand Horizon</div>
          <div style="font-size:11px;color:#606070;">Hotel Management</div>
        </div>
      </div>
      <div style="display:flex;align-items:center;gap:20px;">
        <div style="font-size:13px;color:#a0a0b0;">{datetime.now().strftime('%B %d, %Y  %H:%M')}</div>
        <div style="display:flex;align-items:center;gap:10px;">
          <div style="width:34px;height:34px;background:{rc}22;border:1px solid {rc}44;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;color:{rc};">{user['full_name'][0]}</div>
          <div>
            <div style="font-size:13px;font-weight:600;color:#f0f0f5;">{user['full_name']}</div>
            <div style="font-size:11px;color:{rc};font-weight:600;">{user['role'].upper()}</div>
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

def nav_menu():
    user = st.session_state.user
    role = user["role"]
    pages = []
    all_pages = [
        ("dashboard","Dashboard"),("rooms","Room Management"),("guests","Guest Registry"),
        ("reservations","Reservations"),("checkin","Check-In / Check-Out"),
        ("housekeeping","Housekeeping"),("maintenance","Maintenance"),
        ("billing","Billing & Payments"),("reports","Reports & Analytics"),("users","User Management"),
    ]
    access = {
        "admin": [p[0] for p in all_pages],
        "manager": ["dashboard","rooms","guests","reservations","checkin","housekeeping","maintenance","billing","reports"],
        "staff": ["dashboard","rooms","guests","reservations","checkin","billing"],
        "housekeeping": ["dashboard","rooms","housekeeping"],
        "maintenance": ["dashboard","rooms","maintenance"],
    }
    allowed = access.get(role,[])
    pages = [p for p in all_pages if p[0] in allowed]
    icons = {"dashboard":"D","rooms":"R","guests":"G","reservations":"B","checkin":"CI","housekeeping":"HK","maintenance":"MT","billing":"$","reports":"RP","users":"U"}
    cur = st.session_state.get("current_page","dashboard")
    cols = st.columns(len(pages) + 1)
    for i,(pid,pname) in enumerate(pages):
        with cols[i]:
            active = cur == pid
            bg = "background:#7c3aed;" if active else ""
            if st.button(pname, key=f"nav_{pid}", use_container_width=True):
                st.session_state.current_page = pid
                st.rerun()
    with cols[-1]:
        if st.button("Sign Out", key="nav_logout", use_container_width=True):
            log_action(user["id"], "Logout", f"User {user['username']} logged out")
            st.session_state.user = None
            st.session_state.page = "login"
            st.session_state.current_page = "dashboard"
            st.rerun()

def get_dashboard_stats():
    conn = get_conn()
    today = str(date.today())
    total_rooms = conn.execute("SELECT COUNT(*) FROM rooms").fetchone()[0]
    available = conn.execute("SELECT COUNT(*) FROM rooms WHERE status='Available'").fetchone()[0]
    occupied = conn.execute("SELECT COUNT(*) FROM rooms WHERE status='Occupied'").fetchone()[0]
    checked_in = conn.execute("SELECT COUNT(*) FROM reservations WHERE status='Checked-In'").fetchone()[0]
    today_checkins = conn.execute("SELECT COUNT(*) FROM reservations WHERE check_in=? AND status='Confirmed'", (today,)).fetchone()[0]
    today_checkouts = conn.execute("SELECT COUNT(*) FROM reservations WHERE check_out=? AND status='Checked-In'", (today,)).fetchone()[0]
    revenue = conn.execute("SELECT COALESCE(SUM(total_amount),0) FROM reservations WHERE status!='Cancelled' AND payment_status='Paid'").fetchone()[0]
    monthly = conn.execute("SELECT COALESCE(SUM(total_amount),0) FROM reservations WHERE strftime('%Y-%m',created_at)=strftime('%Y-%m','now') AND status!='Cancelled'").fetchone()[0]
    pending_hk = conn.execute("SELECT COUNT(*) FROM housekeeping WHERE status='Pending'").fetchone()[0]
    open_maint = conn.execute("SELECT COUNT(*) FROM maintenance WHERE status='Open'").fetchone()[0]
    pending_res = conn.execute("SELECT COUNT(*) FROM reservations WHERE status='Confirmed'").fetchone()[0]
    conn.close()
    return dict(total_rooms=total_rooms,available=available,occupied=occupied,checked_in=checked_in,
                today_checkins=today_checkins,today_checkouts=today_checkouts,revenue=revenue,
                monthly=monthly,pending_hk=pending_hk,open_maint=open_maint,pending_res=pending_res)

def dashboard_page():
    st.markdown(STYLE, unsafe_allow_html=True)
    s = get_dashboard_stats()
    st.markdown('<div style="padding:28px 32px 0;">', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="margin-bottom:28px;">
      <div style="font-size:26px;font-weight:800;color:#f0f0f5;margin-bottom:4px;">Good {('Morning' if datetime.now().hour<12 else 'Afternoon' if datetime.now().hour<17 else 'Evening')}, {st.session_state.user['full_name'].split()[0]}</div>
      <div style="font-size:14px;color:#606070;">Here's what's happening at the hotel today</div>
    </div>
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px;">
      <div style="background:#16161f;border:1px solid #2a2a3a;border-radius:16px;padding:22px;">
        <div style="font-size:12px;color:#606070;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:12px;">Total Rooms</div>
        <div style="font-size:36px;font-weight:800;color:#a78bfa;margin-bottom:6px;">{s['total_rooms']}</div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;">
          <span style="font-size:11px;color:#34d399;background:rgba(52,211,153,0.1);padding:2px 8px;border-radius:10px;">{s['available']} Available</span>
          <span style="font-size:11px;color:#f59e0b;background:rgba(245,158,11,0.1);padding:2px 8px;border-radius:10px;">{s['occupied']} Occupied</span>
        </div>
      </div>
      <div style="background:#16161f;border:1px solid #2a2a3a;border-radius:16px;padding:22px;">
        <div style="font-size:12px;color:#606070;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:12px;">Today's Activity</div>
        <div style="font-size:36px;font-weight:800;color:#3b82f6;margin-bottom:6px;">{s['today_checkins']+s['today_checkouts']}</div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;">
          <span style="font-size:11px;color:#3b82f6;background:rgba(59,130,246,0.1);padding:2px 8px;border-radius:10px;">{s['today_checkins']} Check-Ins</span>
          <span style="font-size:11px;color:#ef4444;background:rgba(239,68,68,0.1);padding:2px 8px;border-radius:10px;">{s['today_checkouts']} Check-Outs</span>
        </div>
      </div>
      <div style="background:#16161f;border:1px solid #2a2a3a;border-radius:16px;padding:22px;">
        <div style="font-size:12px;color:#606070;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:12px;">Total Revenue</div>
        <div style="font-size:36px;font-weight:800;color:#10b981;margin-bottom:6px;">₹{s['revenue']:,.0f}</div>
        <div style="font-size:12px;color:#606070;">Month: <span style="color:#10b981;font-weight:600;">₹{s['monthly']:,.0f}</span></div>
      </div>
      <div style="background:#16161f;border:1px solid #2a2a3a;border-radius:16px;padding:22px;">
        <div style="font-size:12px;color:#606070;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:12px;">Pending Tasks</div>
        <div style="font-size:36px;font-weight:800;color:#f59e0b;margin-bottom:6px;">{s['pending_hk']+s['open_maint']}</div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;">
          <span style="font-size:11px;color:#f59e0b;background:rgba(245,158,11,0.1);padding:2px 8px;border-radius:10px;">{s['pending_hk']} Housekeeping</span>
          <span style="font-size:11px;color:#ef4444;background:rgba(239,68,68,0.1);padding:2px 8px;border-radius:10px;">{s['open_maint']} Maintenance</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns([3, 2])
    with col1:
        conn = get_conn()
        monthly_data = []
        for i in range(6):
            d = date.today().replace(day=1) - timedelta(days=i*30)
            ym = d.strftime("%Y-%m")
            rev = conn.execute("SELECT COALESCE(SUM(total_amount),0) FROM reservations WHERE strftime('%Y-%m',created_at)=? AND status!='Cancelled'", (ym,)).fetchone()[0]
            cnt = conn.execute("SELECT COUNT(*) FROM reservations WHERE strftime('%Y-%m',created_at)=?", (ym,)).fetchone()[0]
            monthly_data.append({"Month": d.strftime("%b %Y"), "Revenue": rev, "Bookings": cnt})
        monthly_data.reverse()
        df_m = pd.DataFrame(monthly_data)
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(x=df_m["Month"], y=df_m["Revenue"], name="Revenue", marker_color="rgba(124,58,237,0.8)", marker_line_color="rgba(124,58,237,1)", marker_line_width=1), secondary_y=False)
        fig.add_trace(go.Scatter(x=df_m["Month"], y=df_m["Bookings"], name="Bookings", line=dict(color="#10b981", width=3), mode="lines+markers", marker=dict(size=8, color="#10b981")), secondary_y=True)
        fig.update_layout(plot_bgcolor="#16161f", paper_bgcolor="#16161f", font=dict(color="#a0a0b0", size=12),
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, bgcolor="rgba(0,0,0,0)"),
                          margin=dict(l=0,r=0,t=30,b=0), height=280)
        fig.update_xaxes(gridcolor="#2a2a3a", showgrid=True, gridwidth=1)
        fig.update_yaxes(gridcolor="#2a2a3a", showgrid=True, secondary_y=False, title_text="Revenue (₹)", title_font=dict(color="#a0a0b0"))
        fig.update_yaxes(gridcolor="#2a2a3a", showgrid=False, secondary_y=True, title_text="Bookings", title_font=dict(color="#a0a0b0"))
        st.markdown(f'<div style="background:#16161f;border:1px solid #2a2a3a;border-radius:16px;padding:20px;margin-bottom:20px;"><div style="font-size:15px;font-weight:700;color:#f0f0f5;margin-bottom:16px;">Revenue & Bookings Trend</div>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
        room_status = conn.execute("SELECT status, COUNT(*) as cnt FROM rooms GROUP BY status").fetchall()
        conn.close()
        status_df = pd.DataFrame(room_status, columns=["Status","Count"])
        colors_map = {"Available":"#34d399","Occupied":"#7c3aed","Cleaning":"#f59e0b","Under Maintenance":"#ef4444","Out of Service":"#64748b"}
        fig2 = go.Figure(go.Pie(labels=status_df["Status"], values=status_df["Count"],
                                marker=dict(colors=[colors_map.get(s,"#7c3aed") for s in status_df["Status"]], line=dict(color="#16161f", width=3)),
                                hole=0.65, textinfo="label+percent", textfont=dict(color="#f0f0f5", size=12)))
        fig2.update_layout(plot_bgcolor="#16161f", paper_bgcolor="#16161f", font=dict(color="#a0a0b0"),
                           showlegend=False, margin=dict(l=0,r=0,t=10,b=0), height=200)
        st.markdown(f'<div style="background:#16161f;border:1px solid #2a2a3a;border-radius:16px;padding:20px;"><div style="font-size:15px;font-weight:700;color:#f0f0f5;margin-bottom:16px;">Room Status Distribution</div>', unsafe_allow_html=True)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        conn = get_conn()
        recent_res = conn.execute("""SELECT r.id, g.name, rm.room_number, r.status, r.check_in, r.check_out, r.total_amount
            FROM reservations r JOIN guests g ON r.guest_id=g.id JOIN rooms rm ON r.room_id=rm.id
            ORDER BY r.created_at DESC LIMIT 6""").fetchall()
        status_colors = {"Confirmed":"#3b82f6","Checked-In":"#10b981","Checked-Out":"#606070","Cancelled":"#ef4444"}
        st.markdown('<div style="background:#16161f;border:1px solid #2a2a3a;border-radius:16px;padding:20px;">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:15px;font-weight:700;color:#f0f0f5;margin-bottom:16px;">Recent Reservations</div>', unsafe_allow_html=True)
        for r in recent_res:
            sc = status_colors.get(r["status"],"#606070")
            st.markdown(f"""
            <div style="padding:12px;background:#13131c;border-radius:12px;margin-bottom:8px;border:1px solid #1e1e2e;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                <span style="font-size:13px;font-weight:600;color:#f0f0f5;">{r['name']}</span>
                <span style="font-size:11px;color:{sc};background:{sc}22;padding:2px 8px;border-radius:10px;">{r['status']}</span>
              </div>
              <div style="display:flex;justify-content:space-between;">
                <span style="font-size:12px;color:#606070;">Room {r['room_number']}</span>
                <span style="font-size:12px;color:#a78bfa;font-weight:600;">₹{r['total_amount']:,.0f}</span>
              </div>
              <div style="font-size:11px;color:#404050;margin-top:2px;">{r['check_in']} - {r['check_out']}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        occupancy_rate = round((s['occupied']/s['total_rooms'])*100) if s['total_rooms'] else 0
        fig3 = go.Figure(go.Indicator(mode="gauge+number", value=occupancy_rate,
            domain={"x":[0,1],"y":[0,1]}, title={"text":"Occupancy %","font":{"color":"#a0a0b0","size":14}},
            number={"suffix":"%","font":{"color":"#a78bfa","size":32}},
            gauge={"axis":{"range":[0,100],"tickcolor":"#2a2a3a","tickfont":{"color":"#606070"}},
                   "bar":{"color":"#7c3aed","thickness":0.3},
                   "bgcolor":"#16161f","borderwidth":0,
                   "steps":[{"range":[0,40],"color":"rgba(52,211,153,0.1)"},{"range":[40,75],"color":"rgba(245,158,11,0.1)"},{"range":[75,100],"color":"rgba(239,68,68,0.1)"}],
                   "threshold":{"line":{"color":"#ef4444","width":2},"thickness":0.75,"value":85}}))
        fig3.update_layout(plot_bgcolor="#16161f", paper_bgcolor="#16161f", height=200, margin=dict(l=20,r=20,t=20,b=10))
        st.markdown('<div style="background:#16161f;border:1px solid #2a2a3a;border-radius:16px;padding:20px;margin-top:16px;">', unsafe_allow_html=True)
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
        conn.close()
    st.markdown('</div>', unsafe_allow_html=True)

def rooms_page():
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown('<div style="padding:28px 32px 0;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:24px;font-weight:800;color:#f0f0f5;margin-bottom:24px;">Room Management</div>', unsafe_allow_html=True)
    conn = get_conn()
    rooms = conn.execute("SELECT * FROM rooms ORDER BY floor, room_number").fetchall()
    conn.close()
    tab1, tab2, tab3 = st.tabs(["Room Grid", "Room List", "Add Room"])
    with tab1:
        status_filter = st.selectbox("Filter by Status", ["All","Available","Occupied","Cleaning","Under Maintenance","Out of Service"], key="room_status_filter")
        filtered = [r for r in rooms if status_filter=="All" or r["status"]==status_filter]
        floors = sorted(set(r["floor"] for r in filtered))
        colors = {"Available":"#34d399","Occupied":"#7c3aed","Cleaning":"#f59e0b","Under Maintenance":"#ef4444","Out of Service":"#64748b"}
        for fl in floors:
            st.markdown(f'<div style="font-size:13px;font-weight:700;color:#606070;text-transform:uppercase;letter-spacing:1px;margin:16px 0 10px;">Floor {fl}</div>', unsafe_allow_html=True)
            floor_rooms = [r for r in filtered if r["floor"]==fl]
            cols = st.columns(min(len(floor_rooms), 4))
            for i, r in enumerate(floor_rooms):
                c = colors.get(r["status"],"#606070")
                with cols[i % 4]:
                    st.markdown(f"""
                    <div style="background:#16161f;border:1px solid #2a2a3a;border-radius:14px;padding:18px;margin-bottom:12px;border-left:3px solid {c};">
                      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
                        <div style="font-size:20px;font-weight:800;color:#f0f0f5;">{r['room_number']}</div>
                        <span style="font-size:10px;color:{c};background:{c}22;padding:2px 8px;border-radius:10px;font-weight:600;">{r['status']}</span>
                      </div>
                      <div style="font-size:13px;color:#a0a0b0;margin-bottom:4px;">{r['room_type']}</div>
                      <div style="font-size:16px;color:#a78bfa;font-weight:700;margin-bottom:8px;">₹{r['rate']:,.0f}/night</div>
                      <div style="font-size:11px;color:#404050;">{r['amenities'][:40]}...</div>
                    </div>
                    """, unsafe_allow_html=True)
    with tab2:
        room_data = [{"Room #": r["room_number"], "Type": r["room_type"], "Floor": r["floor"],
                      "Rate/Night": f"₹{r['rate']:,.0f}", "Status": r["status"], "Capacity": r["capacity"],
                      "Amenities": r["amenities"]} for r in rooms]
        st.dataframe(pd.DataFrame(room_data), use_container_width=True, hide_index=True)
        update_options = {f"Room {r['room_number']} ({r['room_type']})": r["id"] for r in rooms}
        selected_room_label = st.selectbox("Select Room to Update Status", list(update_options.keys()), key="room_update_sel")
        new_status = st.selectbox("New Status", ["Available","Occupied","Cleaning","Under Maintenance","Out of Service"], key="room_new_status")
        if st.button("Update Room Status", key="update_room_status"):
            rid = update_options[selected_room_label]
            conn = get_conn()
            conn.execute("UPDATE rooms SET status=? WHERE id=?", (new_status, rid))
            conn.commit()
            conn.close()
            log_action(st.session_state.user["id"], "Room Status Update", f"Room {selected_room_label} -> {new_status}")
            st.success(f"Room status updated to {new_status}")
            st.rerun()
    with tab3:
        with st.form("add_room_form"):
            c1, c2 = st.columns(2)
            with c1:
                rnum = st.text_input("Room Number", placeholder="e.g. 301")
                rtype = st.selectbox("Room Type", ["Standard","Deluxe","Suite","Presidential"])
                rfloor = st.number_input("Floor", min_value=1, max_value=20, value=1)
            with c2:
                rrate = st.number_input("Rate per Night (₹)", min_value=500, value=3000)
                rcap = st.number_input("Capacity", min_value=1, max_value=6, value=2)
                rstatus = st.selectbox("Initial Status", ["Available","Out of Service"])
            ramen = st.text_input("Amenities", placeholder="WiFi, TV, AC, ...")
            rdesc = st.text_area("Description", placeholder="Room description...")
            if st.form_submit_button("Add Room", use_container_width=True):
                if rnum:
                    try:
                        conn = get_conn()
                        conn.execute("INSERT INTO rooms (room_number,room_type,floor,rate,capacity,status,amenities,description) VALUES (?,?,?,?,?,?,?,?)",
                                     (rnum, rtype, rfloor, rrate, rcap, rstatus, ramen, rdesc))
                        conn.commit()
                        conn.close()
                        st.success(f"Room {rnum} added successfully!")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Room number already exists.")
                else:
                    st.error("Room number is required.")
    st.markdown('</div>', unsafe_allow_html=True)

def guests_page():
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown('<div style="padding:28px 32px 0;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:24px;font-weight:800;color:#f0f0f5;margin-bottom:24px;">Guest Registry</div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["Guest List", "Register Guest", "Guest History"])
    with tab1:
        search = st.text_input("Search guests by name or phone", placeholder="Type to search...")
        conn = get_conn()
        if search:
            guests = conn.execute("SELECT * FROM guests WHERE name LIKE ? OR phone LIKE ? ORDER BY registered_at DESC",
                                  (f"%{search}%",f"%{search}%")).fetchall()
        else:
            guests = conn.execute("SELECT * FROM guests ORDER BY registered_at DESC").fetchall()
        conn.close()
        if guests:
            for g in guests:
                conn2 = get_conn()
                bookings = conn2.execute("SELECT COUNT(*) FROM reservations WHERE guest_id=?", (g["id"],)).fetchone()[0]
                total_spend = conn2.execute("SELECT COALESCE(SUM(total_amount),0) FROM reservations WHERE guest_id=? AND status!='Cancelled'", (g["id"],)).fetchone()[0]
                conn2.close()
                st.markdown(f"""
                <div style="background:#16161f;border:1px solid #2a2a3a;border-radius:14px;padding:20px;margin-bottom:12px;">
                  <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div style="display:flex;align-items:center;gap:14px;">
                      <div style="width:44px;height:44px;background:linear-gradient(135deg,#7c3aed,#4f46e5);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:800;color:#fff;">{g['name'][0]}</div>
                      <div>
                        <div style="font-size:15px;font-weight:700;color:#f0f0f5;">{g['name']}</div>
                        <div style="font-size:13px;color:#606070;">{g['phone']} • {g['email'] or 'No email'}</div>
                        <div style="font-size:12px;color:#404050;">{g['nationality']} • {g['id_type'] or 'N/A'}: {g['id_number'] or 'N/A'}</div>
                      </div>
                    </div>
                    <div style="display:flex;gap:20px;">
                      <div style="text-align:center"><div style="font-size:20px;font-weight:700;color:#3b82f6;">{bookings}</div><div style="font-size:11px;color:#606070;">Bookings</div></div>
                      <div style="text-align:center"><div style="font-size:20px;font-weight:700;color:#10b981;">₹{total_spend:,.0f}</div><div style="font-size:11px;color:#606070;">Total Spend</div></div>
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No guests found.")
    with tab2:
        with st.form("register_guest_form"):
            c1, c2 = st.columns(2)
            with c1:
                gname = st.text_input("Full Name*", placeholder="Guest full name")
                gphone = st.text_input("Phone*", placeholder="+91 XXXXX XXXXX")
                gemail = st.text_input("Email", placeholder="guest@email.com")
                gnationality = st.selectbox("Nationality", ["Domestic","International"])
            with c2:
                gidtype = st.selectbox("ID Type", ["Passport","Aadhar","License","PAN","Other"])
                gidnum = st.text_input("ID Number", placeholder="Document number")
                gaddress = st.text_area("Address", placeholder="Guest address...")
            if st.form_submit_button("Register Guest", use_container_width=True):
                if gname and gphone:
                    conn = get_conn()
                    conn.execute("INSERT INTO guests (name,phone,email,id_type,id_number,address,nationality) VALUES (?,?,?,?,?,?,?)",
                                 (gname, gphone, gemail, gidtype, gidnum, gaddress, gnationality))
                    conn.commit()
                    conn.close()
                    log_action(st.session_state.user["id"], "Guest Registered", f"Guest {gname} registered")
                    st.success(f"Guest {gname} registered successfully!")
                    st.rerun()
                else:
                    st.error("Name and phone are required.")
    with tab3:
        conn = get_conn()
        guests_list = conn.execute("SELECT id, name FROM guests ORDER BY name").fetchall()
        conn.close()
        if guests_list:
            options = {f"{g['name']} (ID:{g['id']})": g["id"] for g in guests_list}
            sel = st.selectbox("Select Guest", list(options.keys()), key="hist_guest_sel")
            gid = options[sel]
            conn2 = get_conn()
            history = conn2.execute("""SELECT r.id, rm.room_number, rm.room_type, r.check_in, r.check_out, r.nights, r.total_amount, r.status, r.payment_mode, r.payment_status
                FROM reservations r JOIN rooms rm ON r.room_id=rm.id WHERE r.guest_id=? ORDER BY r.created_at DESC""", (gid,)).fetchall()
            conn2.close()
            if history:
                hdf = pd.DataFrame([dict(r) for r in history])
                hdf.columns = ["ID","Room","Type","Check-In","Check-Out","Nights","Amount","Status","Payment","Pay Status"]
                st.dataframe(hdf, use_container_width=True, hide_index=True)
                total = sum(r["total_amount"] for r in history if r["status"] != "Cancelled")
                st.markdown(f'<div style="text-align:right;font-size:16px;font-weight:700;color:#a78bfa;margin-top:12px;">Total Spend: ₹{total:,.0f}</div>', unsafe_allow_html=True)
            else:
                st.info("No booking history for this guest.")
    st.markdown('</div>', unsafe_allow_html=True)

def reservations_page():
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown('<div style="padding:28px 32px 0;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:24px;font-weight:800;color:#f0f0f5;margin-bottom:24px;">Reservation Management</div>', unsafe_allow_html=True)
    tab1, tab2, tab3, tab4 = st.tabs(["All Reservations", "New Reservation", "Modify Reservation", "Cancel Reservation"])
    with tab1:
        conn = get_conn()
        c1, c2, c3 = st.columns(3)
        with c1:
            sf = st.selectbox("Status Filter", ["All","Confirmed","Checked-In","Checked-Out","Cancelled"], key="res_sf")
        with c2:
            search_res = st.text_input("Search by guest name", placeholder="Guest name...", key="res_search")
        with c3:
            date_filter = st.date_input("Filter by Date", value=None, key="res_date")
        query = """SELECT r.id, g.name, rm.room_number, rm.room_type, r.check_in, r.check_out, r.nights,
                   r.total_amount, r.status, r.payment_mode, r.payment_status, r.created_at
                   FROM reservations r JOIN guests g ON r.guest_id=g.id JOIN rooms rm ON r.room_id=rm.id WHERE 1=1"""
        params = []
        if sf != "All":
            query += " AND r.status=?"
            params.append(sf)
        if search_res:
            query += " AND g.name LIKE ?"
            params.append(f"%{search_res}%")
        if date_filter:
            query += " AND (r.check_in=? OR r.check_out=?)"
            params.extend([str(date_filter), str(date_filter)])
        query += " ORDER BY r.created_at DESC"
        reservations = conn.execute(query, params).fetchall()
        conn.close()
        status_colors = {"Confirmed":"#3b82f6","Checked-In":"#10b981","Checked-Out":"#606070","Cancelled":"#ef4444"}
        for r in reservations:
            sc = status_colors.get(r["status"],"#606070")
            pc = "#10b981" if r["payment_status"]=="Paid" else "#f59e0b"
            st.markdown(f"""
            <div style="background:#16161f;border:1px solid #2a2a3a;border-radius:14px;padding:18px;margin-bottom:10px;">
              <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
                <div>
                  <div style="font-size:14px;font-weight:700;color:#f0f0f5;">{r['name']} <span style="color:#404050;font-weight:400;font-size:12px;">#{r['id']}</span></div>
                  <div style="font-size:13px;color:#606070;margin-top:2px;">Room {r['room_number']} ({r['room_type']}) • {r['nights']} nights</div>
                  <div style="font-size:12px;color:#404050;margin-top:2px;">{r['check_in']} to {r['check_out']}</div>
                </div>
                <div style="display:flex;align-items:center;gap:12px;">
                  <div style="text-align:right">
                    <div style="font-size:18px;font-weight:700;color:#a78bfa;">₹{r['total_amount']:,.0f}</div>
                    <div style="font-size:11px;color:{pc}">{r['payment_mode']} • {r['payment_status']}</div>
                  </div>
                  <span style="font-size:11px;color:{sc};background:{sc}22;padding:4px 12px;border-radius:20px;font-weight:600;">{r['status']}</span>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)
        if not reservations:
            st.info("No reservations found with the selected filters.")
    with tab2:
        conn = get_conn()
        guests = conn.execute("SELECT id, name, phone FROM guests ORDER BY name").fetchall()
        avail_rooms = conn.execute("SELECT id, room_number, room_type, rate FROM rooms WHERE status='Available' ORDER BY room_number").fetchall()
        conn.close()
        if not guests:
            st.warning("No guests registered. Please register a guest first.")
        elif not avail_rooms:
            st.warning("No available rooms at the moment.")
        else:
            with st.form("new_res_form"):
                c1, c2 = st.columns(2)
                with c1:
                    guest_opts = {f"{g['name']} ({g['phone']})": g["id"] for g in guests}
                    sel_guest = st.selectbox("Select Guest*", list(guest_opts.keys()), key="nr_guest")
                    check_in = st.date_input("Check-In Date*", value=date.today(), key="nr_ci")
                    payment_mode = st.selectbox("Payment Mode", ["Cash","Card","UPI","Online"], key="nr_pm")
                with c2:
                    room_opts = {f"Room {r['room_number']} - {r['room_type']} (₹{r['rate']:,.0f}/night)": r["id"] for r in avail_rooms}
                    sel_room = st.selectbox("Select Room*", list(room_opts.keys()), key="nr_room")
                    check_out = st.date_input("Check-Out Date*", value=date.today()+timedelta(1), key="nr_co")
                    pay_status = st.selectbox("Payment Status", ["Pending","Paid"], key="nr_ps")
                special = st.text_area("Special Requests", placeholder="Any special requirements...", key="nr_sr")
                selected_room_id = room_opts[sel_room]
                conn3 = get_conn()
                selected_room = conn3.execute("SELECT rate FROM rooms WHERE id=?", (selected_room_id,)).fetchone()
                conn3.close()
                if check_out > check_in:
                    nights = (check_out - check_in).days
                    total = nights * selected_room["rate"]
                    st.markdown(f"""
                    <div style="background:rgba(124,58,237,0.1);border:1px solid rgba(124,58,237,0.3);border-radius:12px;padding:16px;margin:12px 0;">
                      <div style="display:flex;justify-content:space-between;">
                        <div><span style="color:#a0a0b0;">Nights:</span> <span style="color:#a78bfa;font-weight:700;">{nights}</span></div>
                        <div><span style="color:#a0a0b0;">Total:</span> <span style="color:#a78bfa;font-weight:700;font-size:18px;">₹{total:,.0f}</span></div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    nights = 0
                    total = 0
                    st.error("Check-out must be after check-in.")
                if st.form_submit_button("Create Reservation", use_container_width=True):
                    if nights > 0:
                        conflict = get_conn().execute("""SELECT id FROM reservations WHERE room_id=? AND status NOT IN ('Cancelled','Checked-Out')
                            AND ((check_in <= ? AND check_out > ?) OR (check_in < ? AND check_out >= ?))""",
                            (selected_room_id, str(check_out), str(check_in), str(check_out), str(check_in))).fetchone()
                        if conflict:
                            st.error("This room is already booked for the selected dates. Please choose different dates or a different room.")
                        else:
                            conn4 = get_conn()
                            conn4.execute("INSERT INTO reservations (guest_id,room_id,check_in,check_out,nights,total_amount,status,payment_mode,payment_status,special_requests,created_by) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                                         (guest_opts[sel_guest], selected_room_id, str(check_in), str(check_out), nights, total, "Confirmed", payment_mode, pay_status, special, st.session_state.user["id"]))
                            conn4.commit()
                            conn4.close()
                            log_action(st.session_state.user["id"], "Reservation Created", f"Guest {sel_guest} booked {sel_room}")
                            st.success("Reservation created successfully!")
                            st.rerun()
                    else:
                        st.error("Please select valid dates.")
    with tab3:
        conn = get_conn()
        mod_res = conn.execute("""SELECT r.id, g.name, rm.room_number, r.status, r.check_in, r.check_out, r.nights, r.total_amount
            FROM reservations r JOIN guests g ON r.guest_id=g.id JOIN rooms rm ON r.room_id=rm.id
            WHERE r.status IN ('Confirmed','Checked-In') ORDER BY r.check_in""").fetchall()
        conn.close()
        if not mod_res:
            st.info("No active reservations to modify.")
        else:
            options = {f"#{r['id']} - {r['name']} (Room {r['room_number']}, {r['check_in']} to {r['check_out']})": r["id"] for r in mod_res}
            sel = st.selectbox("Select Reservation to Modify", list(options.keys()), key="mod_res_sel")
            rid = options[sel]
            res_detail = next(r for r in mod_res if r["id"]==rid)
            with st.form("modify_res_form"):
                c1, c2 = st.columns(2)
                with c1:
                    new_ci = st.date_input("New Check-In", value=date.fromisoformat(res_detail["check_in"]), key="mod_ci")
                with c2:
                    new_co = st.date_input("New Check-Out", value=date.fromisoformat(res_detail["check_out"]), key="mod_co")
                new_pm = st.selectbox("Payment Mode", ["Cash","Card","UPI","Online"], key="mod_pm")
                new_ps = st.selectbox("Payment Status", ["Pending","Paid"], key="mod_ps")
                new_sr = st.text_area("Special Requests", key="mod_sr")
                if st.form_submit_button("Update Reservation", use_container_width=True):
                    if new_co > new_ci:
                        conn5 = get_conn()
                        room_id = conn5.execute("SELECT room_id FROM reservations WHERE id=?", (rid,)).fetchone()[0]
                        rate = conn5.execute("SELECT rate FROM rooms WHERE id=?", (room_id,)).fetchone()[0]
                        new_nights = (new_co - new_ci).days
                        new_total = new_nights * rate
                        conn5.execute("UPDATE reservations SET check_in=?,check_out=?,nights=?,total_amount=?,payment_mode=?,payment_status=?,special_requests=? WHERE id=?",
                                      (str(new_ci), str(new_co), new_nights, new_total, new_pm, new_ps, new_sr, rid))
                        conn5.commit()
                        conn5.close()
                        log_action(st.session_state.user["id"], "Reservation Modified", f"Reservation #{rid} updated")
                        st.success("Reservation updated successfully!")
                        st.rerun()
                    else:
                        st.error("Check-out must be after check-in.")
    with tab4:
        conn = get_conn()
        cancel_res = conn.execute("""SELECT r.id, g.name, rm.room_number, r.status, r.check_in, r.check_out, r.total_amount
            FROM reservations r JOIN guests g ON r.guest_id=g.id JOIN rooms rm ON r.room_id=rm.id
            WHERE r.status IN ('Confirmed') ORDER BY r.check_in""").fetchall()
        conn.close()
        if not cancel_res:
            st.info("No reservations eligible for cancellation.")
        else:
            options = {f"#{r['id']} - {r['name']} (Room {r['room_number']}, {r['check_in']})": r["id"] for r in cancel_res}
            sel = st.selectbox("Select Reservation to Cancel", list(options.keys()), key="cancel_res_sel")
            rid = options[sel]
            res_detail = next(r for r in cancel_res if r["id"]==rid)
            st.markdown(f"""
            <div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);border-radius:12px;padding:16px;margin:12px 0;">
              <div style="color:#ef4444;font-weight:600;margin-bottom:8px;">Cancellation Warning</div>
              <div style="color:#c0c0d0;font-size:14px;">You are about to cancel reservation #{res_detail['id']} for {res_detail['name']}.</div>
              <div style="color:#c0c0d0;font-size:14px;">Room {res_detail['room_number']} • {res_detail['check_in']} to {res_detail['check_out']} • ₹{res_detail['total_amount']:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
            confirm_cancel = st.checkbox("I confirm I want to cancel this reservation", key="cancel_confirm")
            if st.button("Cancel Reservation", key="do_cancel", type="primary"):
                if confirm_cancel:
                    conn6 = get_conn()
                    conn6.execute("UPDATE reservations SET status='Cancelled' WHERE id=?", (rid,))
                    room_id = conn6.execute("SELECT room_id FROM reservations WHERE id=?", (rid,)).fetchone()[0]
                    conn6.execute("UPDATE rooms SET status='Available' WHERE id=?", (room_id,))
                    conn6.commit()
                    conn6.close()
                    log_action(st.session_state.user["id"], "Reservation Cancelled", f"Reservation #{rid} cancelled")
                    st.success("Reservation cancelled and room released.")
                    st.rerun()
                else:
                    st.error("Please check the confirmation box first.")
    st.markdown('</div>', unsafe_allow_html=True)

def checkin_page():
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown('<div style="padding:28px 32px 0;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:24px;font-weight:800;color:#f0f0f5;margin-bottom:24px;">Check-In / Check-Out</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div style="background:#16161f;border:1px solid #2a2a3a;border-radius:16px;padding:24px;">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:17px;font-weight:700;color:#10b981;margin-bottom:16px;">Guest Check-In</div>', unsafe_allow_html=True)
        conn = get_conn()
        confirmed_res = conn.execute("""SELECT r.id, g.name, rm.room_number, rm.id as room_id, r.check_in, r.check_out, r.nights, r.total_amount, r.payment_mode
            FROM reservations r JOIN guests g ON r.guest_id=g.id JOIN rooms rm ON r.room_id=rm.id
            WHERE r.status='Confirmed' ORDER BY r.check_in""").fetchall()
        conn.close()
        if confirmed_res:
            opts = {f"#{r['id']} - {r['name']} (Room {r['room_number']})": (r["id"], r["room_id"]) for r in confirmed_res}
            sel = st.selectbox("Select Reservation", list(opts.keys()), key="ci_res_sel")
            rid, room_id = opts[sel]
            det = next(r for r in confirmed_res if r["id"]==rid)
            st.markdown(f"""
            <div style="background:#13131c;border-radius:10px;padding:14px;margin:12px 0;">
              <div style="color:#f0f0f5;font-weight:600;margin-bottom:6px;">{det['name']}</div>
              <div style="color:#606070;font-size:13px;">Room {det['room_number']} • {det['nights']} nights</div>
              <div style="color:#606070;font-size:13px;">{det['check_in']} to {det['check_out']}</div>
              <div style="color:#a78bfa;font-weight:700;font-size:16px;margin-top:6px;">₹{det['total_amount']:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Confirm Check-In", key="do_checkin", use_container_width=True):
                conn7 = get_conn()
                conn7.execute("UPDATE reservations SET status='Checked-In' WHERE id=?", (rid,))
                conn7.execute("UPDATE rooms SET status='Occupied' WHERE id=?", (room_id,))
                conn7.commit()
                conn7.close()
                log_action(st.session_state.user["id"], "Guest Check-In", f"Reservation #{rid} checked in")
                st.success(f"Check-in confirmed for {det['name']}! Room {det['room_number']} is now occupied.")
                st.rerun()
        else:
            st.info("No confirmed reservations for check-in.")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div style="background:#16161f;border:1px solid #2a2a3a;border-radius:16px;padding:24px;">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:17px;font-weight:700;color:#ef4444;margin-bottom:16px;">Guest Check-Out</div>', unsafe_allow_html=True)
        conn = get_conn()
        checked_in_res = conn.execute("""SELECT r.id, g.name, rm.room_number, rm.id as room_id, r.check_in, r.check_out, r.nights, r.total_amount, r.payment_mode, r.payment_status
            FROM reservations r JOIN guests g ON r.guest_id=g.id JOIN rooms rm ON r.room_id=rm.id
            WHERE r.status='Checked-In' ORDER BY r.check_out""").fetchall()
        conn.close()
        if checked_in_res:
            opts2 = {f"#{r['id']} - {r['name']} (Room {r['room_number']})": (r["id"], r["room_id"]) for r in checked_in_res}
            sel2 = st.selectbox("Select Reservation", list(opts2.keys()), key="co_res_sel")
            rid2, room_id2 = opts2[sel2]
            det2 = next(r for r in checked_in_res if r["id"]==rid2)
            st.markdown(f"""
            <div style="background:#13131c;border-radius:10px;padding:14px;margin:12px 0;">
              <div style="color:#f0f0f5;font-weight:600;margin-bottom:6px;">{det2['name']}</div>
              <div style="color:#606070;font-size:13px;">Room {det2['room_number']} • {det2['nights']} nights</div>
              <div style="color:#606070;font-size:13px;">Checked in: {det2['check_in']}</div>
              <div style="color:#a78bfa;font-weight:700;font-size:16px;margin-top:6px;">Total: ₹{det2['total_amount']:,.0f}</div>
              <div style="color:{'#10b981' if det2['payment_status']=='Paid' else '#f59e0b'};font-size:13px;">{det2['payment_mode']} • {det2['payment_status']}</div>
            </div>
            """, unsafe_allow_html=True)
            final_pay = st.selectbox("Final Payment Status", ["Paid","Pending"], key="co_ps")
            if st.button("Confirm Check-Out", key="do_checkout", use_container_width=True):
                conn8 = get_conn()
                conn8.execute("UPDATE reservations SET status='Checked-Out', payment_status=? WHERE id=?", (final_pay, rid2))
                conn8.execute("UPDATE rooms SET status='Cleaning' WHERE id=?", (room_id2,))
                conn8.execute("INSERT INTO housekeeping (room_id,status,notes) VALUES (?,?,?)", (room_id2,"Pending",f"Post checkout cleaning - {datetime.now().strftime('%Y-%m-%d %H:%M')}"))
                conn8.commit()
                conn8.close()
                log_action(st.session_state.user["id"], "Guest Check-Out", f"Reservation #{rid2} checked out")
                st.success(f"Check-out completed for {det2['name']}. Room {det2['room_number']} marked for cleaning.")
                st.rerun()
        else:
            st.info("No guests currently checked in.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div style="margin-top:24px;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:17px;font-weight:700;color:#f0f0f5;margin-bottom:16px;">Currently Checked-In Guests</div>', unsafe_allow_html=True)
    conn = get_conn()
    active = conn.execute("""SELECT g.name, rm.room_number, rm.room_type, r.check_in, r.check_out, r.total_amount, r.payment_status
        FROM reservations r JOIN guests g ON r.guest_id=g.id JOIN rooms rm ON r.room_id=rm.id
        WHERE r.status='Checked-In' ORDER BY r.check_out""").fetchall()
    conn.close()
    if active:
        adf = pd.DataFrame([dict(r) for r in active])
        adf.columns = ["Guest","Room","Type","Check-In","Check-Out","Amount","Payment"]
        st.dataframe(adf, use_container_width=True, hide_index=True)
    else:
        st.info("No guests currently checked in.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def housekeeping_page():
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown('<div style="padding:28px 32px 0;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:24px;font-weight:800;color:#f0f0f5;margin-bottom:24px;">Housekeeping Management</div>', unsafe_allow_html=True)
    conn = get_conn()
    hk_tasks = conn.execute("""SELECT h.id, rm.room_number, rm.room_type, rm.floor, h.status, h.assigned_to, h.notes, h.updated_at, rm.id as room_id
        FROM housekeeping h JOIN rooms rm ON h.room_id=rm.id ORDER BY h.updated_at DESC""").fetchall()
    rooms_needing_hk = conn.execute("SELECT id, room_number, room_type FROM rooms WHERE status IN ('Cleaning','Available') ORDER BY room_number").fetchall()
    conn.close()
    tab1, tab2 = st.tabs(["Active Tasks", "Assign / Update"])
    with tab1:
        status_filter = st.selectbox("Filter", ["All","Pending","In Progress","Completed"], key="hk_filter")
        filtered = [t for t in hk_tasks if status_filter=="All" or t["status"]==status_filter]
        sc_map = {"Pending":"#f59e0b","In Progress":"#3b82f6","Completed":"#10b981"}
        stats_c = st.columns(3)
        for i, (stat, label) in enumerate([("Pending","Pending"),("In Progress","In Progress"),("Completed","Done Today")]):
            count = len([t for t in hk_tasks if t["status"]==stat])
            with stats_c[i]:
                sc = sc_map[stat]
                st.markdown(f'<div style="background:#16161f;border:1px solid #2a2a3a;border-radius:14px;padding:20px;text-align:center;border-top:3px solid {sc};"><div style="font-size:28px;font-weight:800;color:{sc};">{count}</div><div style="font-size:13px;color:#606070;">{label}</div></div>', unsafe_allow_html=True)
        st.markdown('<div style="height:16px;"></div>', unsafe_allow_html=True)
        for t in filtered:
            sc = sc_map.get(t["status"],"#606070")
            st.markdown(f"""
            <div style="background:#16161f;border:1px solid #2a2a3a;border-radius:14px;padding:18px;margin-bottom:10px;border-left:3px solid {sc};">
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                  <div style="font-size:15px;font-weight:700;color:#f0f0f5;">Room {t['room_number']} - Floor {t['floor']}</div>
                  <div style="font-size:13px;color:#606070;">{t['room_type']}</div>
                  <div style="font-size:12px;color:#404050;margin-top:4px;">Assigned to: {t['assigned_to'] or 'Unassigned'}</div>
                  <div style="font-size:12px;color:#404050;">{t['notes'][:60] if t['notes'] else 'No notes'}</div>
                </div>
                <div style="text-align:right">
                  <span style="font-size:12px;color:{sc};background:{sc}22;padding:4px 12px;border-radius:20px;font-weight:600;">{t['status']}</span>
                  <div style="font-size:11px;color:#404050;margin-top:8px;">{t['updated_at'][:16]}</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div style="font-size:15px;font-weight:600;color:#f0f0f5;margin-bottom:12px;">Assign New Task</div>', unsafe_allow_html=True)
            with st.form("assign_hk_form"):
                room_opts = {f"Room {r['room_number']} ({r['room_type']})": r["id"] for r in rooms_needing_hk}
                if room_opts:
                    sel_rm = st.selectbox("Select Room", list(room_opts.keys()), key="hk_room_sel")
                    assigned = st.text_input("Assign To", placeholder="Staff name")
                    notes = st.text_area("Notes", placeholder="Cleaning instructions...")
                    if st.form_submit_button("Assign Task", use_container_width=True):
                        conn9 = get_conn()
                        conn9.execute("INSERT INTO housekeeping (room_id,status,assigned_to,notes) VALUES (?,?,?,?)",
                                      (room_opts[sel_rm], "Pending", assigned, notes))
                        conn9.execute("UPDATE rooms SET status='Cleaning' WHERE id=?", (room_opts[sel_rm],))
                        conn9.commit()
                        conn9.close()
                        log_action(st.session_state.user["id"], "Housekeeping Assigned", f"{sel_rm} assigned to {assigned}")
                        st.success("Task assigned!")
                        st.rerun()
                else:
                    st.info("No rooms need housekeeping currently.")
                    st.form_submit_button("Assign Task", disabled=True)
        with col2:
            st.markdown('<div style="font-size:15px;font-weight:600;color:#f0f0f5;margin-bottom:12px;">Update Task Status</div>', unsafe_allow_html=True)
            with st.form("update_hk_form"):
                if hk_tasks:
                    active_tasks = [t for t in hk_tasks if t["status"] != "Completed"]
                    if active_tasks:
                        task_opts = {f"#{t['id']} Room {t['room_number']} ({t['status']})": (t["id"], t["room_id"]) for t in active_tasks}
                        sel_task = st.selectbox("Select Task", list(task_opts.keys()), key="hk_task_sel")
                        new_stat = st.selectbox("New Status", ["In Progress","Completed"], key="hk_new_stat")
                        if st.form_submit_button("Update Status", use_container_width=True):
                            tid, rmid = task_opts[sel_task]
                            conn10 = get_conn()
                            conn10.execute("UPDATE housekeeping SET status=?, updated_at=datetime('now') WHERE id=?", (new_stat, tid))
                            if new_stat == "Completed":
                                conn10.execute("UPDATE rooms SET status='Available' WHERE id=?", (rmid,))
                            conn10.commit()
                            conn10.close()
                            log_action(st.session_state.user["id"], "Housekeeping Updated", f"Task #{tid} -> {new_stat}")
                            st.success(f"Task updated to {new_stat}!")
                            st.rerun()
                    else:
                        st.info("No active tasks to update.")
                        st.form_submit_button("Update", disabled=True)
                else:
                    st.info("No tasks found.")
                    st.form_submit_button("Update", disabled=True)
    st.markdown('</div>', unsafe_allow_html=True)

def maintenance_page():
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown('<div style="padding:28px 32px 0;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:24px;font-weight:800;color:#f0f0f5;margin-bottom:24px;">Maintenance Management</div>', unsafe_allow_html=True)
    conn = get_conn()
    tickets = conn.execute("""SELECT m.id, rm.room_number, rm.floor, m.issue, m.priority, m.status, m.assigned_to, m.notes, m.reported_at, m.resolved_at, rm.id as room_id
        FROM maintenance m JOIN rooms rm ON m.room_id=rm.id ORDER BY m.reported_at DESC""").fetchall()
    all_rooms = conn.execute("SELECT id, room_number, room_type FROM rooms ORDER BY room_number").fetchall()
    conn.close()
    tab1, tab2 = st.tabs(["Maintenance Tickets", "Report Issue"])
    with tab1:
        stat_filter = st.selectbox("Filter by Status", ["All","Open","In Progress","Completed"], key="mt_filter")
        filtered = [t for t in tickets if stat_filter=="All" or t["status"]==stat_filter]
        sc_map = {"Open":"#ef4444","In Progress":"#f59e0b","Completed":"#10b981"}
        pc_map = {"High":"#ef4444","Normal":"#f59e0b","Low":"#3b82f6"}
        stats_c = st.columns(3)
        for i, (st_name, label) in enumerate([("Open","Open"),("In Progress","In Progress"),("Completed","Resolved")]):
            count = len([t for t in tickets if t["status"]==st_name])
            with stats_c[i]:
                sc = sc_map[st_name]
                st.markdown(f'<div style="background:#16161f;border:1px solid #2a2a3a;border-radius:14px;padding:20px;text-align:center;border-top:3px solid {sc};"><div style="font-size:28px;font-weight:800;color:{sc};">{count}</div><div style="font-size:13px;color:#606070;">{label}</div></div>', unsafe_allow_html=True)
        st.markdown('<div style="height:16px;"></div>', unsafe_allow_html=True)
        for t in filtered:
            sc = sc_map.get(t["status"],"#606070")
            pc = pc_map.get(t["priority"],"#606070")
            st.markdown(f"""
            <div style="background:#16161f;border:1px solid #2a2a3a;border-radius:14px;padding:18px;margin-bottom:10px;border-left:3px solid {sc};">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div>
                  <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                    <span style="font-size:15px;font-weight:700;color:#f0f0f5;">Room {t['room_number']}</span>
                    <span style="font-size:11px;color:{pc};background:{pc}22;padding:2px 8px;border-radius:10px;font-weight:600;">{t['priority']}</span>
                    <span style="font-size:11px;color:{sc};background:{sc}22;padding:2px 8px;border-radius:10px;font-weight:600;">{t['status']}</span>
                  </div>
                  <div style="font-size:13px;color:#c0c0d0;">{t['issue']}</div>
                  <div style="font-size:12px;color:#404050;margin-top:4px;">Assigned: {t['assigned_to'] or 'Unassigned'} • Reported: {t['reported_at'][:16]}</div>
                  {f'<div style="font-size:12px;color:#10b981;margin-top:2px;">Resolved: {t["resolved_at"][:16]}</div>' if t['resolved_at'] else ''}
                </div>
                <div style="text-align:right">
                  <div style="font-size:11px;color:#404050;">#{t['id']}</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)
            if t["status"] != "Completed":
                c1, c2 = st.columns([3, 1])
                with c2:
                    if st.button(f"Mark Resolved #{t['id']}", key=f"resolve_{t['id']}", use_container_width=True):
                        conn11 = get_conn()
                        conn11.execute("UPDATE maintenance SET status='Completed', resolved_at=datetime('now') WHERE id=?", (t["id"],))
                        if t["status"] == "Open":
                            conn11.execute("UPDATE rooms SET status='Available' WHERE id=?", (t["room_id"],))
                        conn11.commit()
                        conn11.close()
                        log_action(st.session_state.user["id"], "Maintenance Resolved", f"Ticket #{t['id']} resolved")
                        st.success("Marked as resolved!")
                        st.rerun()
    with tab2:
        with st.form("report_issue_form"):
            room_opts = {f"Room {r['room_number']} ({r['room_type']})": r["id"] for r in all_rooms}
            sel_rm = st.selectbox("Select Room", list(room_opts.keys()), key="mt_room_sel")
            c1, c2 = st.columns(2)
            with c1:
                issue = st.text_area("Issue Description*", placeholder="Describe the maintenance issue...")
                priority = st.selectbox("Priority", ["Normal","High","Low"], key="mt_priority")
            with c2:
                assigned = st.text_input("Assign To", placeholder="Technician name")
                notes = st.text_area("Additional Notes", placeholder="Extra details...")
            if st.form_submit_button("Report Issue", use_container_width=True):
                if issue:
                    conn12 = get_conn()
                    conn12.execute("INSERT INTO maintenance (room_id,issue,priority,status,assigned_to,notes) VALUES (?,?,?,?,?,?)",
                                   (room_opts[sel_rm], issue, priority, "Open", assigned, notes))
                    conn12.execute("UPDATE rooms SET status='Under Maintenance' WHERE id=?", (room_opts[sel_rm],))
                    conn12.commit()
                    conn12.close()
                    log_action(st.session_state.user["id"], "Maintenance Reported", f"{sel_rm}: {issue[:50]}")
                    st.success("Maintenance issue reported and room marked as Under Maintenance.")
                    st.rerun()
                else:
                    st.error("Issue description is required.")
    st.markdown('</div>', unsafe_allow_html=True)

def billing_page():
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown('<div style="padding:28px 32px 0;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:24px;font-weight:800;color:#f0f0f5;margin-bottom:24px;">Billing & Payments</div>', unsafe_allow_html=True)
    conn = get_conn()
    tab1, tab2 = st.tabs(["Invoice Generator", "Payment Summary"])
    with tab1:
        all_res = conn.execute("""SELECT r.id, g.name, g.phone, g.email, rm.room_number, rm.room_type, rm.rate, r.check_in, r.check_out, r.nights, r.total_amount, r.status, r.payment_mode, r.payment_status, r.special_requests
            FROM reservations r JOIN guests g ON r.guest_id=g.id JOIN rooms rm ON r.room_id=rm.id
            WHERE r.status IN ('Checked-In','Checked-Out','Confirmed') ORDER BY r.created_at DESC""").fetchall()
        if all_res:
            opts = {f"#{r['id']} - {r['name']} ({r['status']})": r["id"] for r in all_res}
            sel = st.selectbox("Select Reservation for Invoice", list(opts.keys()), key="bill_res_sel")
            rid = opts[sel]
            r = next(x for x in all_res if x["id"]==rid)
            tax = r["total_amount"] * 0.12
            service = r["nights"] * 200
            grand_total = r["total_amount"] + tax + service
            st.markdown(f"""
            <div style="background:#16161f;border:1px solid #2a2a3a;border-radius:16px;padding:28px;max-width:700px;">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:24px;">
                <div>
                  <div style="font-size:22px;font-weight:800;color:#f0f0f5;">INVOICE</div>
                  <div style="font-size:13px;color:#606070;">Grand Horizon Hotel</div>
                  <div style="font-size:13px;color:#606070;">Reservation #{r['id']}</div>
                  <div style="font-size:12px;color:#404050;">{datetime.now().strftime('%B %d, %Y')}</div>
                </div>
                <div style="text-align:right">
                  <span style="font-size:12px;color:{'#10b981' if r['payment_status']=='Paid' else '#f59e0b'};background:{'rgba(16,185,129,0.1)' if r['payment_status']=='Paid' else 'rgba(245,158,11,0.1)'};padding:6px 16px;border-radius:20px;font-weight:600;">{r['payment_status'].upper()}</span>
                </div>
              </div>
              <div style="background:#13131c;border-radius:10px;padding:16px;margin-bottom:20px;">
                <div style="font-size:13px;font-weight:700;color:#a0a0b0;margin-bottom:10px;">GUEST DETAILS</div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
                  <div><span style="color:#606070;font-size:12px;">Name:</span> <span style="color:#f0f0f5;font-size:13px;font-weight:600;">{r['name']}</span></div>
                  <div><span style="color:#606070;font-size:12px;">Phone:</span> <span style="color:#f0f0f5;font-size:13px;">{r['phone']}</span></div>
                  <div><span style="color:#606070;font-size:12px;">Check-In:</span> <span style="color:#f0f0f5;font-size:13px;">{r['check_in']}</span></div>
                  <div><span style="color:#606070;font-size:12px;">Check-Out:</span> <span style="color:#f0f0f5;font-size:13px;">{r['check_out']}</span></div>
                </div>
              </div>
              <div style="background:#13131c;border-radius:10px;padding:16px;margin-bottom:20px;">
                <div style="font-size:13px;font-weight:700;color:#a0a0b0;margin-bottom:10px;">ROOM DETAILS</div>
                <div style="display:flex;justify-content:space-between;align-items:center;">
                  <div>
                    <div style="color:#f0f0f5;font-weight:600;">Room {r['room_number']} - {r['room_type']}</div>
                    <div style="color:#606070;font-size:12px;">₹{r['rate']:,.0f}/night x {r['nights']} nights</div>
                  </div>
                  <div style="color:#a78bfa;font-weight:700;font-size:16px;">₹{r['total_amount']:,.0f}</div>
                </div>
              </div>
              <div style="border-top:1px solid #2a2a3a;padding-top:16px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                  <span style="color:#606070;font-size:13px;">Room Charges</span>
                  <span style="color:#c0c0d0;font-size:13px;">₹{r['total_amount']:,.0f}</span>
                </div>
                <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                  <span style="color:#606070;font-size:13px;">Service Charges (₹200/night)</span>
                  <span style="color:#c0c0d0;font-size:13px;">₹{service:,.0f}</span>
                </div>
                <div style="display:flex;justify-content:space-between;margin-bottom:12px;">
                  <span style="color:#606070;font-size:13px;">GST (12%)</span>
                  <span style="color:#c0c0d0;font-size:13px;">₹{tax:,.0f}</span>
                </div>
                <div style="display:flex;justify-content:space-between;padding-top:12px;border-top:1px solid #2a2a3a;">
                  <span style="color:#f0f0f5;font-weight:700;font-size:16px;">Grand Total</span>
                  <span style="color:#a78bfa;font-weight:800;font-size:20px;">₹{grand_total:,.0f}</span>
                </div>
              </div>
              <div style="margin-top:16px;padding-top:16px;border-top:1px solid #2a2a3a;">
                <span style="color:#606070;font-size:12px;">Payment Mode: </span>
                <span style="color:#c0c0d0;font-size:12px;font-weight:600;">{r['payment_mode']}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)
            if r["payment_status"] == "Pending":
                if st.button("Mark as Paid", key="mark_paid", type="primary"):
                    conn_p = get_conn()
                    conn_p.execute("UPDATE reservations SET payment_status='Paid' WHERE id=?", (rid,))
                    conn_p.commit()
                    conn_p.close()
                    log_action(st.session_state.user["id"], "Payment Recorded", f"Reservation #{rid} marked Paid")
                    st.success("Payment recorded!")
                    st.rerun()
    with tab2:
        total_paid = conn.execute("SELECT COALESCE(SUM(total_amount),0) FROM reservations WHERE payment_status='Paid' AND status!='Cancelled'").fetchone()[0]
        total_pending = conn.execute("SELECT COALESCE(SUM(total_amount),0) FROM reservations WHERE payment_status='Pending' AND status NOT IN ('Cancelled','Checked-Out')").fetchone()[0]
        pm_data = conn.execute("SELECT payment_mode, COUNT(*) as cnt, SUM(total_amount) as revenue FROM reservations WHERE status!='Cancelled' GROUP BY payment_mode").fetchall()
        conn.close()
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Total Revenue Collected", f"₹{total_paid:,.0f}")
        with c2:
            st.metric("Pending Payments", f"₹{total_pending:,.0f}")
        with c3:
            st.metric("Net Revenue", f"₹{total_paid:,.2f}")
        if pm_data:
            pm_df = pd.DataFrame([dict(r) for r in pm_data])
            pm_df.columns = ["Mode","Bookings","Revenue"]
            fig = px.bar(pm_df, x="Mode", y="Revenue", color="Revenue", title="Revenue by Payment Mode",
                         color_continuous_scale=["#4f46e5","#7c3aed","#a78bfa"])
            fig.update_layout(plot_bgcolor="#16161f", paper_bgcolor="#16161f", font=dict(color="#a0a0b0"),
                              showlegend=False, margin=dict(l=0,r=0,t=40,b=0), height=300)
            fig.update_xaxes(gridcolor="#2a2a3a")
            fig.update_yaxes(gridcolor="#2a2a3a")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    st.markdown('</div>', unsafe_allow_html=True)

def reports_page():
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown('<div style="padding:28px 32px 0;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:24px;font-weight:800;color:#f0f0f5;margin-bottom:24px;">Reports & Analytics</div>', unsafe_allow_html=True)
    tab1, tab2, tab3, tab4 = st.tabs(["Occupancy Report", "Revenue Analysis", "Booking Trends", "Operations"])
    with tab1:
        conn = get_conn()
        room_status = conn.execute("SELECT status, COUNT(*) as cnt FROM rooms GROUP BY status").fetchall()
        rs_df = pd.DataFrame([dict(r) for r in room_status])
        rs_df.columns = ["Status","Count"]
        colors = {"Available":"#34d399","Occupied":"#7c3aed","Cleaning":"#f59e0b","Under Maintenance":"#ef4444","Out of Service":"#64748b"}
        fig1 = px.pie(rs_df, values="Count", names="Status", title="Current Room Status Distribution",
                      color="Status", color_discrete_map=colors, hole=0.5)
        fig1.update_layout(plot_bgcolor="#16161f", paper_bgcolor="#16161f", font=dict(color="#a0a0b0"), height=350)
        fig1.update_traces(textfont=dict(color="#f0f0f5"))
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar":False})
        type_occ = conn.execute("""SELECT rm.room_type, COUNT(*) as total, SUM(CASE WHEN rm.status='Occupied' THEN 1 ELSE 0 END) as occupied
            FROM rooms rm GROUP BY rm.room_type""").fetchall()
        conn.close()
        to_df = pd.DataFrame([dict(r) for r in type_occ])
        to_df.columns = ["Type","Total","Occupied"]
        to_df["Occupancy%"] = (to_df["Occupied"]/to_df["Total"]*100).round(1)
        fig2 = px.bar(to_df, x="Type", y="Occupancy%", title="Occupancy Rate by Room Type",
                      color="Occupancy%", color_continuous_scale=["#4f46e5","#7c3aed","#a78bfa"])
        fig2.update_layout(plot_bgcolor="#16161f", paper_bgcolor="#16161f", font=dict(color="#a0a0b0"),
                           showlegend=False, height=350, margin=dict(l=0,r=0,t=40,b=0))
        fig2.update_xaxes(gridcolor="#2a2a3a")
        fig2.update_yaxes(gridcolor="#2a2a3a", range=[0,100])
        with col2:
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})
        st.dataframe(to_df, use_container_width=True, hide_index=True)
    with tab2:
        conn = get_conn()
        monthly = []
        for i in range(12):
            d = date.today().replace(day=1) - timedelta(days=i*30)
            ym = d.strftime("%Y-%m")
            row = conn.execute("SELECT COALESCE(SUM(total_amount),0), COUNT(*) FROM reservations WHERE strftime('%Y-%m',created_at)=? AND status!='Cancelled'", (ym,)).fetchone()
            monthly.append({"Month": d.strftime("%b %Y"), "Revenue": row[0], "Bookings": row[1]})
        monthly.reverse()
        conn.close()
        m_df = pd.DataFrame(monthly)
        fig3 = px.area(m_df, x="Month", y="Revenue", title="Monthly Revenue (Last 12 Months)",
                       color_discrete_sequence=["#7c3aed"])
        fig3.update_traces(fill="tozeroy", fillcolor="rgba(124,58,237,0.15)", line=dict(color="#7c3aed", width=2))
        fig3.update_layout(plot_bgcolor="#16161f", paper_bgcolor="#16161f", font=dict(color="#a0a0b0"),
                           height=300, margin=dict(l=0,r=0,t=40,b=0))
        fig3.update_xaxes(gridcolor="#2a2a3a")
        fig3.update_yaxes(gridcolor="#2a2a3a")
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar":False})
        st.dataframe(m_df, use_container_width=True, hide_index=True)
    with tab3:
        conn = get_conn()
        status_counts = conn.execute("SELECT status, COUNT(*) as cnt FROM reservations GROUP BY status").fetchall()
        sc_df = pd.DataFrame([dict(r) for r in status_counts])
        sc_df.columns = ["Status","Count"]
        c1, c2 = st.columns(2)
        with c1:
            colors2 = {"Confirmed":"#3b82f6","Checked-In":"#10b981","Checked-Out":"#606070","Cancelled":"#ef4444"}
            fig4 = px.bar(sc_df, x="Status", y="Count", title="Reservations by Status",
                          color="Status", color_discrete_map=colors2)
            fig4.update_layout(plot_bgcolor="#16161f", paper_bgcolor="#16161f", font=dict(color="#a0a0b0"),
                               showlegend=False, height=300, margin=dict(l=0,r=0,t=40,b=0))
            fig4.update_xaxes(gridcolor="#2a2a3a")
            fig4.update_yaxes(gridcolor="#2a2a3a")
            st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar":False})
        with c2:
            nights_data = conn.execute("SELECT nights, COUNT(*) as cnt FROM reservations GROUP BY nights ORDER BY nights").fetchall()
            nd_df = pd.DataFrame([dict(r) for r in nights_data])
            if not nd_df.empty:
                nd_df.columns = ["Nights","Count"]
                fig5 = px.bar(nd_df, x="Nights", y="Count", title="Stay Duration Distribution", color_discrete_sequence=["#10b981"])
                fig5.update_layout(plot_bgcolor="#16161f", paper_bgcolor="#16161f", font=dict(color="#a0a0b0"),
                                   height=300, margin=dict(l=0,r=0,t=40,b=0))
                fig5.update_xaxes(gridcolor="#2a2a3a")
                fig5.update_yaxes(gridcolor="#2a2a3a")
                st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar":False})
        conn.close()
    with tab4:
        conn = get_conn()
        hk_summary = conn.execute("SELECT status, COUNT(*) FROM housekeeping GROUP BY status").fetchall()
        mt_summary = conn.execute("SELECT status, COUNT(*) FROM maintenance GROUP BY status").fetchall()
        conn.close()
        c1, c2 = st.columns(2)
        with c1:
            if hk_summary:
                hk_df = pd.DataFrame(hk_summary, columns=["Status","Count"])
                fig6 = px.pie(hk_df, values="Count", names="Status", title="Housekeeping Tasks", hole=0.5,
                              color_discrete_sequence=["#f59e0b","#3b82f6","#10b981"])
                fig6.update_layout(plot_bgcolor="#16161f", paper_bgcolor="#16161f", font=dict(color="#a0a0b0"), height=280)
                st.plotly_chart(fig6, use_container_width=True, config={"displayModeBar":False})
        with c2:
            if mt_summary:
                mt_df = pd.DataFrame(mt_summary, columns=["Status","Count"])
                fig7 = px.pie(mt_df, values="Count", names="Status", title="Maintenance Tickets", hole=0.5,
                              color_discrete_sequence=["#ef4444","#f59e0b","#10b981"])
                fig7.update_layout(plot_bgcolor="#16161f", paper_bgcolor="#16161f", font=dict(color="#a0a0b0"), height=280)
                st.plotly_chart(fig7, use_container_width=True, config={"displayModeBar":False})
    st.markdown('</div>', unsafe_allow_html=True)

def users_page():
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown('<div style="padding:28px 32px 0;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:24px;font-weight:800;color:#f0f0f5;margin-bottom:24px;">User Management</div>', unsafe_allow_html=True)
    if st.session_state.user["role"] != "admin":
        st.error("Access Denied: Only administrators can access this page.")
        return
    tab1, tab2, tab3 = st.tabs(["All Users", "Create User", "Activity Log"])
    with tab1:
        conn = get_conn()
        users = conn.execute("SELECT id, username, full_name, role, email, phone, status, created_at FROM users ORDER BY created_at DESC").fetchall()
        conn.close()
        role_colors = {"admin":"#7c3aed","manager":"#3b82f6","staff":"#10b981","housekeeping":"#f59e0b","maintenance":"#ef4444"}
        for u in users:
            rc = role_colors.get(u["role"],"#606070")
            status_c = "#10b981" if u["status"]=="active" else "#ef4444"
            st.markdown(f"""
            <div style="background:#16161f;border:1px solid #2a2a3a;border-radius:14px;padding:18px;margin-bottom:10px;">
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <div style="display:flex;align-items:center;gap:12px;">
                  <div style="width:40px;height:40px;background:{rc}22;border:1px solid {rc}44;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:700;color:{rc};">{u['full_name'][0]}</div>
                  <div>
                    <div style="font-size:14px;font-weight:700;color:#f0f0f5;">{u['full_name']}</div>
                    <div style="font-size:12px;color:#606070;">@{u['username']} • {u['email'] or 'No email'}</div>
                    <div style="font-size:11px;color:#404050;">Joined: {u['created_at'][:10]}</div>
                  </div>
                </div>
                <div style="display:flex;gap:10px;align-items:center;">
                  <span style="font-size:11px;color:{rc};background:{rc}22;padding:3px 10px;border-radius:10px;font-weight:600;">{u['role'].upper()}</span>
                  <span style="font-size:11px;color:{status_c};background:{status_c}22;padding:3px 10px;border-radius:10px;font-weight:600;">{u['status'].upper()}</span>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)
            c1, c2 = st.columns([4,1])
            with c2:
                if u["id"] != st.session_state.user["id"]:
                    new_s = "inactive" if u["status"]=="active" else "active"
                    if st.button(f"{'Deactivate' if u['status']=='active' else 'Activate'}", key=f"toggle_user_{u['id']}"):
                        conn_u = get_conn()
                        conn_u.execute("UPDATE users SET status=? WHERE id=?", (new_s, u["id"]))
                        conn_u.commit()
                        conn_u.close()
                        log_action(st.session_state.user["id"], "User Status Changed", f"User {u['username']} -> {new_s}")
                        st.rerun()
    with tab2:
        with st.form("create_user_form"):
            c1, c2 = st.columns(2)
            with c1:
                new_fn = st.text_input("Full Name*")
                new_un = st.text_input("Username*")
                new_pw = st.text_input("Password*", type="password")
            with c2:
                new_role = st.selectbox("Role", ["staff","housekeeping","maintenance","manager","admin"])
                new_email = st.text_input("Email")
                new_phone = st.text_input("Phone")
            if st.form_submit_button("Create User", use_container_width=True):
                if new_fn and new_un and new_pw:
                    try:
                        conn_c = get_conn()
                        conn_c.execute("INSERT INTO users (username,password,full_name,role,email,phone) VALUES (?,?,?,?,?,?)",
                                       (new_un, hash_pw(new_pw), new_fn, new_role, new_email, new_phone))
                        conn_c.commit()
                        conn_c.close()
                        log_action(st.session_state.user["id"], "User Created", f"New user {new_un} with role {new_role}")
                        st.success(f"User {new_fn} created successfully!")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Username already exists.")
                else:
                    st.error("Name, username, and password are required.")
    with tab3:
        conn = get_conn()
        logs = conn.execute("""SELECT a.id, u.full_name, u.username, a.action, a.details, a.timestamp
            FROM activity_log a LEFT JOIN users u ON a.user_id=u.id ORDER BY a.timestamp DESC LIMIT 50""").fetchall()
        conn.close()
        for l in logs:
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 14px;background:#16161f;border:1px solid #2a2a3a;border-radius:10px;margin-bottom:6px;">
              <div>
                <span style="font-size:13px;font-weight:600;color:#a78bfa;">{l['full_name'] or 'System'}</span>
                <span style="color:#606070;font-size:12px;margin:0 8px;">•</span>
                <span style="font-size:13px;color:#c0c0d0;">{l['action']}</span>
                <div style="font-size:12px;color:#404050;margin-top:2px;">{l['details']}</div>
              </div>
              <div style="font-size:11px;color:#404050;white-space:nowrap;">{l['timestamp'][:16]}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    init_db()
    if "user" not in st.session_state:
        st.session_state.user = None
    if "page" not in st.session_state:
        st.session_state.page = "login"
    if "current_page" not in st.session_state:
        st.session_state.current_page = "dashboard"
    if st.session_state.user is None:
        if st.session_state.page == "register":
            register_page()
        else:
            login_page()
    else:
        topbar()
        st.markdown(STYLE, unsafe_allow_html=True)
        st.markdown('<div style="padding:8px 32px;background:#0e0e17;border-bottom:1px solid #1e1e2e;">', unsafe_allow_html=True)
        nav_menu()
        st.markdown('</div>', unsafe_allow_html=True)
        cp = st.session_state.get("current_page","dashboard")
        page_map = {
            "dashboard": dashboard_page,
            "rooms": rooms_page,
            "guests": guests_page,
            "reservations": reservations_page,
            "checkin": checkin_page,
            "housekeeping": housekeeping_page,
            "maintenance": maintenance_page,
            "billing": billing_page,
            "reports": reports_page,
            "users": users_page,
        }
        role = st.session_state.user["role"]
        access = {
            "admin": list(page_map.keys()),
            "manager": ["dashboard","rooms","guests","reservations","checkin","housekeeping","maintenance","billing","reports"],
            "staff": ["dashboard","rooms","guests","reservations","checkin","billing"],
            "housekeeping": ["dashboard","rooms","housekeeping"],
            "maintenance": ["dashboard","rooms","maintenance"],
        }
        allowed = access.get(role,[])
        if cp not in allowed:
            cp = "dashboard"
            st.session_state.current_page = "dashboard"
        page_map[cp]()
        st.markdown('<div style="height:40px;"></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
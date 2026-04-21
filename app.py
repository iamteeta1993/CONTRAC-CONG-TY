import streamlit as st
import pandas as pd
import os
import requests
import hashlib
from datetime import datetime
import urllib.parse
import re

# --- 1. CẤU HÌNH HỆ THỐNG ---
DATA_FILE = "data_congty.xlsx"
USER_FILE = "users.xlsx"
COLUMNS = ["Tên Công Ty", "Mã Số Thuế", "Chủ Doanh Nghiệp", "Địa Chỉ", "Liên Hệ", "Ghi Chú", "Zalo", "Cập Nhật Cuối"]
ADMIN_USER = "admin" 
ADMIN_PASS = "123"

# --- 2. HÀM HỆ THỐNG ---
def hash_password(password): return hashlib.sha256(str.encode(password)).hexdigest()

def authenticate(username, password, login_type):
    if login_type == "admin":
        return "admin" if username == ADMIN_USER and password == ADMIN_PASS else None
    if os.path.exists(USER_FILE):
        users = pd.read_excel(USER_FILE, dtype=str)
        hashed_pwd = hash_password(password)
        if not users[(users["username"] == username) & (users["password"] == hashed_pwd)].empty:
            return "user"
    return None

def save_user(username, password):
    if not os.path.exists(USER_FILE):
        pd.DataFrame(columns=["username", "password"]).to_excel(USER_FILE, index=False)
    users = pd.read_excel(USER_FILE, dtype=str)
    if username in users["username"].values or username == ADMIN_USER: return False
    new_user = pd.DataFrame([{"username": username, "password": hash_password(password)}])
    pd.concat([users, new_user], ignore_index=True).to_excel(USER_FILE, index=False)
    return True

def get_business_info(mst):
    try:
        res = requests.get(f"https://vietqr.io{mst}", timeout=5)
        return res.json()['data'] if res.status_code == 200 and res.json()['code'] == "00" else None
    except: return None

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_excel(DATA_FILE, dtype=str)
            for col in COLUMNS:
                if col not in df.columns: df[col] = ""
            return df[COLUMNS]
        except: return pd.DataFrame(columns=COLUMNS)
    return pd.DataFrame(columns=COLUMNS)

def clean_phone(phone): return re.sub(r'\D', '', str(phone))

# --- 3. GIAO DIỆN ĐĂNG NHẬP / KHÁCH ---
st.set_page_config(page_title="TEETA CODE", layout="wide")
if "role" not in st.session_state: st.session_state["role"] = None

if st.session_state["role"] is None:
    st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>TEETA CODE</h1>", unsafe_allow_html=True)
    t1, t2, t3, t4 = st.tabs(["🔑 Thành viên", "📝 Đăng ký", "🛡️ Admin", "🌐 Khách"])
    with t1:
        u = st.text_input("Username"); p = st.text_input("Password", type="password")
        if st.button("ĐĂNG NHẬP THÀNH VIÊN"):
            r = authenticate(u, p, "user")
            if r: st.session_state["role"], st.session_state["username"] = r, u; st.rerun()
            else: st.error("Sai thông tin!")
    with t3:
        ua = st.text_input("Admin User"); pa = st.text_input("Admin Pass", type="password")
        if st.button("XÁC NHẬN ADMIN"):
            r = authenticate(ua, pa, "admin")
            if r: st.session_state["role"], st.session_state["username"] = r, "CHỦ APP"; st.rerun()
    with t4:
        st.info("Chế độ Khách: Chỉ xem thông tin cơ bản.")
        if st.button("VÀO XEM (FREE)"):
            st.session_state["role"], st.session_state["username"] = "guest", "Khách"; st.rerun()
    st.stop()

# --- 4. GIAO DIỆN CHÍNH ---
st.markdown("<div style='text-align: center; margin-top: -60px;'> <h1 style='color: #FF4B4B; font-family: Arial Black;'>TEETA <span style='color: #31333F;'>CODE</span></h1> </div>", unsafe_allow_html=True)

st.sidebar.write(f"👤 Quyền: **{st.session_state['role'].upper()}**")
if st.sidebar.button("Thoát"): st.session_state["role"] = None; st.rerun()

# NHẠC ZING MP3 (Ai cũng nghe được)
st.sidebar.divider()
zing_html = '<iframe title="Zing MP3" width="100%" height="400" src="https://zingmp3.vn" frameborder="0" allowfullscreen="true"></iframe>'
with st.sidebar: st.components.v1.html(zing_html, height=410)

df = load_data()

# PHÂN QUYỀN TRÊN SIDEBAR
if st.session_state["role"] == "admin":
    st.sidebar.subheader("➕ Thêm Công Ty")
    search_mst = st.sidebar.text_input("🔍 Gõ MST tra nhanh")
    n_v, a_v = "", ""
    if search_mst:
        info = get_business_info(search_mst)
        if info: n_v, a_v = info.get('name', ''), info.get('address', '')
    with st.sidebar.form("add_form", clear_on_submit=True):
        fn = st.text_input("Tên", value=n_v); fm = st.text_input("MST", value=search_mst); fa = st.text_input("Địa chỉ", value=a_v); fp = st.text_input("SĐT"); fg = st.text_area("Ghi chú")
        if st.form_submit_button("Lưu"):
            now = datetime.now().strftime("%d/%m/%Y %H:%M")
            new_row = pd.DataFrame([[fn, fm, "", fa, fp, fg, f"https://zalo.me{clean_phone(fp)}", now]], columns=COLUMNS)
            df = pd.concat([df, new_row], ignore_index=True); df.to_excel(DATA_FILE, index=False); st.rerun()
    # Chỉ Admin mới thấy nút tải file
    with open(DATA_FILE, "rb") as f: st.sidebar.download_button("📥 Tải file Excel", f, file_name="data.xlsx")

# TRANG CHÍNH: TRA CỨU
q = st.text_input("🔎 Tìm tên hoặc MST...")
if not df.empty:
    f_df = df[df['Tên Công Ty'].str.contains(q, case=False, na=False) | df['Mã Số Thuế'].str.contains(q, case=False, na=False)] if q else df
    for i, row in f_df.iterrows():
        with st.expander(f"🏢 {row['Tên Công Ty']} - {row['Mã Số Thuế']}"):
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"📍 {row['Địa Chỉ']}")
                maps_q = urllib.parse.quote(str(row['Địa Chỉ']))
                st.markdown(f"🌍 [Mở Google Maps](https://google.com{maps_q})")
                # CHỈ THÀNH VIÊN & ADMIN MỚI THẤY GHI CHÚ
                if st.session_state["role"] in ["admin", "user"]:
                    st.info(f"📝 **Ghi chú nội bộ:** {row['Ghi Chú']}")
            with c2:
                st.write(f"📞 {row['Liên Hệ']}")
                st.markdown(f"""<a href="https://zalo.me{clean_phone(row['Liên Hệ'])}" target="_blank" style="text-decoration:none;"><div style="background-color:#0068FF;color:white;padding:10px;border-radius:10px;text-align:center;font-weight:bold;">💬 NHẮN ZALO</div></a>""", unsafe_allow_html=True)
            # CHỈ ADMIN MỚI THẤY NÚT XÓA
            if st.session_state["role"] == "admin":
                if st.button("🗑️ Xóa", key=f"d_{i}"): df.drop(i).to_excel(DATA_FILE, index=False); st.rerun()
else: st.info("Trống.")

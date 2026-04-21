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
def hash_password(password): 
    return hashlib.sha256(str.encode(password)).hexdigest()

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
        res = requests.get(f"https://api.vietqr.io/v2/business/{mst}", timeout=5)
        data = res.json()
        return data['data'] if data.get('code') == "00" else None
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

def clean_phone(phone): 
    return re.sub(r'\D', '', str(phone))

# --- 3. GIAO DIỆN ĐĂNG NHẬP ---
st.set_page_config(page_title="TEETA CODE - Quản lý Doanh nghiệp", layout="wide")
if "role" not in st.session_state: st.session_state["role"] = None

if st.session_state["role"] is None:
    st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>TEETA CODE</h1>", unsafe_allow_html=True)
    t1, t2, t3, t4 = st.tabs(["🔑 Thành viên", "📝 Đăng ký", "🛡️ Admin", "🌐 Khách"])
    with t1:
        u = st.text_input("Username", key="login_u")
        p = st.text_input("Password", type="password", key="login_p")
        if st.button("ĐĂNG NHẬP THÀNH VIÊN", use_container_width=True):
            r = authenticate(u, p, "user")
            if r: 
                st.session_state["role"], st.session_state["username"] = r, u
                st.rerun()
            else: st.error("Sai tài khoản hoặc mật khẩu!")
    with t3:
        ua = st.text_input("Admin User", key="ad_u")
        pa = st.text_input("Admin Pass", type="password", key="ad_p")
        if st.button("XÁC NHẬN QUYỀN ADMIN", use_container_width=True):
            r = authenticate(ua, pa, "admin")
            if r: 
                st.session_state["role"], st.session_state["username"] = r, "QUẢN TRỊ VIÊN"
                st.rerun()
            else: st.error("Sai thông tin quản trị!")
    with t4:
        if st.button("VÀO XEM (FREE)", use_container_width=True):
            st.session_state["role"], st.session_state["username"] = "guest", "Khách"
            st.rerun()
    st.stop()

# --- 4. GIAO DIỆN CHÍNH ---
st.markdown("<div style='text-align: center; margin-top: -60px;'> <h1 style='color: #FF4B4B; font-family: Arial Black;'>TEETA <span style='color: #31333F;'>CODE</span></h1> </div>", unsafe_allow_html=True)

# SIDEBAR: Quản lý & Giải trí
st.sidebar.subheader(f"👋 {st.session_state['username']}")
if st.sidebar.button("Đăng xuất"): 
    st.session_state["role"] = None
    st.rerun()

if st.session_state["role"] == "admin" and os.path.exists(DATA_FILE):
    with open(DATA_FILE, "rb") as f:
        st.sidebar.download_button("📥 Xuất file Excel", f, file_name="data_teetacode.xlsx")

st.sidebar.divider()
st.sidebar.subheader("🎵 Giải Trí")
t_nct, t_spot, t_yt = st.sidebar.tabs(["NCT", "Spotify", "YouTube"])
with t_nct:
    st.components.v1.html('<iframe src="https://www.nhaccuatui.com/mh/background/L6Wv9X7Z2z3n" width="100%" height="150" frameborder="0" allowfullscreen allow="autoplay"></iframe>', height=160)
with t_spot:
    st.components.v1.html('<iframe src="http://googleusercontent.com/spotify.com/7" width="100%" height="152" frameBorder="0" allow="autoplay; encrypted-media"></iframe>', height=160)
with t_yt:
    st.components.v1.html('<iframe width="100%" height="152" src="https://www.youtube.com/embed/jfKfPfyJRdk" frameborder="0" allowfullscreen></iframe>', height=160)

# --- QUẢN LÝ TABS CHÍNH ---
df = load_data()
if st.session_state["role"] == "admin":
    tabs = st.tabs(["🔍 Tra cứu & Quản lý", "➕ Thêm Công Ty"])
else:
    tabs = st.tabs(["🔍 Tra cứu dữ liệu"])

# --- TAB 1: TRA CỨU & CHỈNH SỬA ---
with tabs[0]:
    q = st.text_input("🔎 Tìm nhanh Tên hoặc MST...")
    if not df.empty:
        f_df = df[df['Tên Công Ty'].str.contains(q, case=False, na=False) | df['Mã Số Thuế'].str.contains(q, case=False, na=False)] if q else df
        st.write(f"Tìm thấy **{len(f_df)}** kết quả.")

        for i, row in f_df.iterrows():
            edit_key = f"edit_mode_{i}"
            if edit_key not in st.session_state: st.session_state[edit_key] = False

            with st.expander(f"🏢 {row['Tên Công Ty']} - {row['Mã Số Thuế']}"):
                # NẾU ADMIN ĐANG BẤM SỬA
                if st.session_state[edit_key] and st.session_state["role"] == "admin":
                    with st.form(key=f"f_edit_{i}"):
                        c1, c2 = st.columns(2)
                        new_ten = c1.text_input("Tên Công Ty", value=row['Tên Công Ty'])
                        new_mst = c1.text_input("Mã Số Thuế", value=row['Mã Số Thuế'])
                        new_chu = c1.text_input("Chủ Doanh Nghiệp", value=row['Chủ Doanh Nghiệp'])
                        new_dc = c2.text_input("Địa Chỉ", value=row['Địa Chỉ'])
                        new_lh = c2.text_input("Liên Hệ", value=row['Liên Hệ'])
                        new_gc = st.text_area("Ghi Chú", value=row['Ghi Chú'])
                        
                        b1, b2 = st.columns(2)
                        if b1.form_submit_button("💾 LƯU LẠI", use_container_width=True):
                            df.loc[i] = [new_ten, new_mst, new_chu, new_dc, new_lh, new_gc, f"https://zalo.me/{clean_phone(new_lh)}", datetime.now().strftime("%d/%m/%Y %H:%M")]
                            df.to_excel(DATA_FILE, index=False)
                            st.session_state[edit_key] = False
                            st.rerun()
                        if b2.form_submit_button("❌ HỦY", use_container_width=True):
                            st.session_state[edit_key] = False
                            st.rerun()
                # HIỂN THỊ THÔNG THƯỜNG
                else:
                    col_a, col_b = st.columns([2, 1])
                    with col_a:
                        st.write(f"📍 **Địa chỉ:** {row['Địa Chỉ']}")
                        st.info(f"📝 **Ghi chú:** {row['Ghi Chú']}")
                    with col_b:
                        st.write(f"👤 **Chủ:** {row['Chủ Doanh Nghiệp']}")
                        st.write(f"📞 **LH:** {row['Liên Hệ']}")
                        if row['Liên Hệ']:
                            st.markdown(f'<a href="https://zalo.me/{clean_phone(row['Liên Hệ'])}" target="_blank" style="text-decoration:none;"><div style="background-color:#0068FF;color:white;padding:10px;border-radius:10px;text-align:center;font-weight:bold;">💬 ZALO</div></a>', unsafe_allow_html=True)

                    if st.session_state["role"] == "admin":
                        st.divider()
                        bt1, bt2 = st.columns(2)
                        if bt1.button("🗑️ Xóa", key=f"del_{i}", use_container_width=True):
                            df.drop(i).to_excel(DATA_FILE, index=False)
                            st.rerun()
                        if bt2.button("📝 Sửa", key=f"ed_btn_{i}", use_container_width=True):
                            st.session_state[edit_key] = True
                            st.rerun()

# --- TAB 2: THÊM MỚI (CHỈ ADMIN) ---
if st.session_state["role"] == "admin":
    with tabs[1]:
        st.subheader("➕ Thêm công ty mới")
        mst_s = st.text_input("🔍 Tra MST nhanh")
        n_v, a_v = "", ""
        if mst_s:
            info = get_business_info(mst_s)
            if info: n_v, a_v = info.get('name', ''), info.get('address', '')
        
        with st.form("add_f", clear_on_submit=True):
            f1, f2 = st.columns(2)
            fn = f1.text_input("Tên Công Ty", value=n_v)
            fm = f1.text_input("Mã Số Thuế", value=mst_s)
            fo = f1.text_input("Chủ Doanh Nghiệp")
            fa = f2.text_input("Địa chỉ", value=a_v)
            fp = f2.text_input("Liên hệ")
            fg = st.text_area("Ghi chú")
            if st.form_submit_button("LƯU HỆ THỐNG", use_container_width=True):
                if fn and fm:
                    new_r = pd.DataFrame([[fn, fm, fo, fa, fp, fg, f"https://zalo.me/{clean_phone(fp)}", datetime.now().strftime("%d/%m/%Y %H:%M")]], columns=COLUMNS)
                    pd.concat([load_data(), new_r], ignore_index=True).to_excel(DATA_FILE, index=False)
                    st.success("Đã thêm!"); st.rerun()

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
COLUMNS = ["Tên Công Ty", "Mã Số Thuế", "Chủ Doanh Nghiệp", "Địa Chỉ", "Liên Hệ", "Zalo", "Cập Nhật Cuối"]

ADMIN_USER = "admin" 
ADMIN_PASS = "teeta123"

# --- 2. CÁC HÀM HỆ THỐNG ---
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
    if username in users["username"].values or username == ADMIN_USER:
        return False
    new_user = pd.DataFrame([{"username": username, "password": hash_password(password)}])
    pd.concat([users, new_user], ignore_index=True).to_excel(USER_FILE, index=False)
    return True

def get_business_info(keyword):
    try:
        res = requests.get(f"https://vietqr.io{keyword}", timeout=5)
        return res.json()['data'] if res.status_code == 200 and res.json()['code'] == "00" else None
    except: return None

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_excel(DATA_FILE, dtype=str)
            for col in COLUMNS:
                if col not in df.columns: df[col] = "Chưa có"
            return df[COLUMNS]
        except: return pd.DataFrame(columns=COLUMNS)
    return pd.DataFrame(columns=COLUMNS)

def clean_phone(phone):
    return re.sub(r'\D', '', str(phone))

# --- 3. GIAO DIỆN ĐĂNG NHẬP / ĐĂNG KÝ ---
st.set_page_config(page_title="TEETA CODE - QUẢN TRỊ", layout="wide")

if "role" not in st.session_state:
    st.session_state["role"] = None

if st.session_state["role"] is None:
    st.markdown("<h1 style='text-align: center; color: #FF4B4B; font-family: Arial Black;'>TEETA CODE</h1>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🔑 Đăng nhập", "📝 Đăng ký", "🛡️ Quản trị viên"])
    
    with t1:
        u = st.text_input("Tên đăng nhập", key="u_login")
        p = st.text_input("Mật khẩu", type="password", key="p_login")
        if st.button("Vào App", use_container_width=True):
            role = authenticate(u, p, "user")
            if role:
                st.session_state["role"], st.session_state["username"] = role, u
                st.rerun()
            else: st.error("Sai tài khoản hoặc mật khẩu!")

    with t2:
        u_reg = st.text_input("Tạo tên mới", key="u_reg")
        p_reg = st.text_input("Tạo mật khẩu mới", type="password", key="p_reg")
        if st.button("Hoàn tất Đăng ký", use_container_width=True):
            if u_reg and p_reg and save_user(u_reg, p_reg): st.success("Thành công! Qua tab Đăng nhập nhé.")
            else: st.error("Tên đăng nhập đã tồn tại!")
    
    with t3:
        st.warning("Khu vực Quản trị dành cho Chủ App.")
        ua = st.text_input("Tài khoản Admin", key="ua_ad")
        pa = st.text_input("Mật khẩu Admin", type="password", key="pa_ad")
        if st.button("Đăng nhập quyền Admin", use_container_width=True):
            role = authenticate(ua, pa, "admin")
            if role:
                st.session_state["role"], st.session_state["username"] = role, "CHỦ APP"
                st.rerun()
            else: st.error("Thông tin Admin không chính xác!")
    st.stop()

# --- 4. GIAO DIỆN CHÍNH (SAU KHI ĐĂNG NHẬP) ---
st.markdown("<div style='text-align: center; margin-top: -60px;'> <h1 style='color: #FF4B4B; font-family: Arial Black; font-size: 45px;'>TEETA <span style='color: #31333F;'>CODE</span></h1> </div>", unsafe_allow_html=True)

st.sidebar.write(f"👤 Chào: **{st.session_state['username']}**")
if st.sidebar.button("Đăng xuất"):
    st.session_state["role"] = None; st.rerun()

# --- TRÌNH PHÁT NHẠC (LINK MỚI - AUTOPLAY 50%) ---
st.sidebar.divider()
st.sidebar.subheader("🎵 TEETA MUSIC")
music_html = """
    <div id="player"></div>
    <script src="https://youtube.com"></script>
    <script>
        var player;
        function onYouTubeIframeAPIReady() {
            player = new YT.Player('player', {
                height: '180', width: '100%', videoId: '3I0zIK1X0vk',
                playerVars: { 'autoplay': 1, 'controls': 1, 'mute': 0, 'loop': 1, 'playlist': '3I0zIK1X0vk' },
                events: { 'onReady': onPlayerReady }
            });
        }
        function onPlayerReady(event) { event.target.setVolume(50); event.target.playVideo(); }
    </script>
"""
with st.sidebar:
    st.components.v1.html(music_html, height=210)
st.sidebar.caption("🎧 Nhạc tự phát 50%. Tương tác với màn hình để nghe nhạc.")

df = load_data()

# Admin: Thêm công ty
if st.session_state["role"] == "admin":
    st.sidebar.divider()
    st.sidebar.subheader("➕ Thêm Công Ty")
    search_api = st.sidebar.text_input("🔍 Tra cứu nhanh MST/Tên")
    n_v, m_v, a_v = "", "", ""
    if search_api:
        with st.sidebar.spinner('Đang lấy dữ liệu...'):
            info = get_business_info(search_api)
            if info: n_v, m_v, a_v = info.get('name', ''), info.get('id', ''), info.get('address', '')
    
    with st.sidebar.form("add_form", clear_on_submit=True):
        f_n = st.text_input("Tên", value=n_v); f_m = st.text_input("MST", value=m_v)
        f_o = st.text_input("Chủ"); f_a = st.text_input("ĐC", value=a_v); f_p = st.text_input("SĐT")
        if st.form_submit_button("Lưu Vào Danh Sách", use_container_width=True):
            if f_n and f_m:
                now = datetime.now().strftime("%d/%m/%Y %H:%M")
                p_p = clean_phone(f_p)
                new_row = pd.DataFrame([[f_n, f_m, f_o, f_a, f_p, f"https://zalo.me{p_p}", now]], columns=COLUMNS)
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_excel(DATA_FILE, index=False); st.rerun()

# Tìm kiếm & Hiển thị
q = st.text_input("🔎 Tìm nhanh trong danh sách của bạn...")
if not df.empty:
    f_df = df[df['Tên Công Ty'].str.contains(q, case=False, na=False) | df['Mã Số Thuế'].str.contains(q, case=False, na=False)] if q else df
    for i, row in f_df.iterrows():
        with st.expander(f"🏢 {row['Tên Công Ty']} - MST: {row['Mã Số Thuế']}"):
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"📍 **ĐC:** {row['Địa Chỉ']}")
                m_q = urllib.parse.quote(str(row['Địa Chỉ']))
                st.markdown(f"🌍 [Google Maps](https://google.com{m_q})")
                st.caption(f"🕒 Cập nhật: {row['Cập Nhật Cuối']}")
            with c2:
                st.write(f"👤 **Chủ:** {row['Chủ Doanh Nghiệp']} | 📞 **SĐT:** {row['Liên Hệ']}")
                p_z = clean_phone(row['Liên Hệ'])
                st.markdown(f"""<a href="https://zalo.me{p_z}" target="_blank" style="text-decoration:none;"><div style="background-color:#0068FF;color:white;padding:10px;border-radius:10px;text-align:center;font-weight:bold;">💬 NHẮN ZALO</div></a>""", unsafe_allow_html=True)
            
            if st.session_state["role"] == "admin":
                ce, cd = st.columns(2)
                with ce:
                    if st.button("📝 Sửa", key=f"e_{i}"): st.session_state[f"edit_{i}"] = True
                with cd:
                    if st.button("🗑️ Xóa", key=f"d_{i}"): df.drop(i).to_excel(DATA_FILE, index=False); st.rerun()
                if st.session_state.get(f"edit_{i}"):
                    with st.form(f"f_e_{i}"):
                        en=st.text_input("Tên", value=row['Tên Công Ty']); em=st.text_input("MST", value=row['Mã Số Thuế'])
                        eo=st.text_input("Chủ", value=row['Chủ Doanh Nghiệp']); ea=st.text_input("ĐC", value=row['Địa Chỉ']); ep=st.text_input("SĐT", value=row['Liên Hệ'])
                        if st.form_submit_button("Cập nhật"):
                            df.iloc[i] = [en, em, eo, ea, ep, f"https://zalo.me{clean_phone(ep)}", datetime.now().strftime("%d/%m/%Y %H:%M")]
                            df.to_excel(DATA_FILE, index=False); st.session_state[f"edit_{i}"] = False; st.rerun()
else: st.info("Danh sách trống.")

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
# Hệ thống chạy chuẩn 7 cột dữ liệu
COLUMNS = ["Tên Công Ty", "Mã Số Thuế", "Chủ Doanh Nghiệp", "Địa Chỉ", "Liên Hệ", "Zalo", "Cập Nhật Cuối"]

# TÀI KHOẢN ADMIN DUY NHẤT CỦA BẠN
ADMIN_USER = "admin" 
ADMIN_PASS = "teeta123"

# --- 2. CÁC HÀM XỬ LÝ (BACKEND) ---
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
        # API VietQR tra cứu doanh nghiệp chuẩn
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
        u_reg = st.text_input("Tạo tên đăng nhập", key="u_reg")
        p_reg = st.text_input("Tạo mật khẩu", type="password", key="p_reg")
        if st.button("Hoàn tất Đăng ký", use_container_width=True):
            if u_reg and p_reg:
                if save_user(u_reg, p_reg): st.success("Thành công! Mời bạn qua tab Đăng nhập.")
                else: st.error("Tên đăng nhập đã tồn tại!")
    
    with t3:
        st.warning("Khu vực dành riêng cho Chủ sở hữu App.")
        ua = st.text_input("Tài khoản Admin", key="ua")
        pa = st.text_input("Mật khẩu Admin", type="password", key="pa")
        if st.button("Đăng nhập quyền Quản trị", use_container_width=True):
            role = authenticate(ua, pa, "admin")
            if role:
                st.session_state["role"], st.session_state["username"] = role, "CHỦ APP"
                st.rerun()
            else: st.error("Thông tin Admin không chính xác!")
    st.stop()

# --- 4. GIAO DIỆN CHÍNH (SAU KHI ĐĂNG NHẬP) ---

# Logo TEETA CODE chính giữa
st.markdown(
    """
    <div style="text-align: center; margin-top: -60px; margin-bottom: 10px;">
        <h1 style="color: #FF4B4B; font-family: 'Arial Black'; font-size: 45px; letter-spacing: 2px;">
            TEETA <span style="color: #31333F;">CODE</span>
        </h1>
        <p style="color: gray; font-style: italic; margin-top: -15px;">Hệ Thống Quản Lý Dữ Liệu Doanh Nghiệp Nội Bộ</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Sidebar: Thông tin & Nhạc
st.sidebar.write(f"👤 Chào: **{st.session_state['username']}**")
if st.sidebar.button("Đăng xuất"):
    st.session_state["role"] = None
    st.rerun()

# Trình phát nhạc tự động 50%
st.sidebar.divider()
st.sidebar.subheader("🎵 TEETA MUSIC")
music_html = """
    <div id="player"></div>
    <script src="https://youtube.com"></script>
    <script>
        var player;
        function onYouTubeIframeAPIReady() {
            player = new YT.Player('player', {
                height: '180', width: '100%', videoId: 'HaIjR05n1Vc',
                playerVars: { 'autoplay': 1, 'controls': 1, 'mute': 0 },
                events: { 'onReady': onPlayerReady }
            });
        }
        function onPlayerReady(event) { event.target.setVolume(50); event.target.playVideo(); }
    </script>
"""
with st.sidebar:
    st.components.v1.html(music_html, height=200)

df = load_data()

# Admin: Thêm công ty
if st.session_state["role"] == "admin":
    st.sidebar.divider()
    st.sidebar.subheader("➕ Thêm Công Ty")
    search_api = st.sidebar.text_input("🔍 Tra cứu nhanh MST/Tên")
    name_v, mst_v, addr_v = "", "", ""
    if search_api:
        with st.sidebar.spinner('Đang lấy dữ liệu...'):
            info = get_business_info(search_api)
            if info:
                name_v, mst_v, addr_v = info.get('name', ''), info.get('id', ''), info.get('address', '')
                st.sidebar.success("Tìm thấy thông tin!")

    with st.sidebar.form("add_form", clear_on_submit=True):
        f_name = st.text_input("Tên Công Ty", value=name_v)
        f_mst = st.text_input("Mã Số Thuế", value=mst_v)
        f_owner = st.text_input("Chủ Doanh Nghiệp")
        f_addr = st.text_input("Địa Chỉ", value=addr_v)
        f_phone = st.text_input("Số Điện Thoại")
        if st.form_submit_button("Lưu Vào Hệ Thống", use_container_width=True):
            if f_name and f_mst:
                now = datetime.now().strftime("%d/%m/%Y %H:%M")
                pure_p = clean_phone(f_phone)
                new_row = pd.DataFrame([[f_name, f_mst, f_owner, f_addr, f_phone, f"https://zalo.me{pure_p}", now]], columns=COLUMNS)
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_excel(DATA_FILE, index=False)
                st.rerun()

# Trang chính: Hiển thị & Tra cứu
q = st.text_input("🔎 Tìm nhanh trong danh sách của bạn...")
if not df.empty:
    f_df = df[df['Tên Công Ty'].str.contains(q, case=False, na=False) | df['Mã Số Thuế'].str.contains(q, case=False, na=False)] if q else df
    for i, row in f_df.iterrows():
        with st.expander(f"🏢 {row['Tên Công Ty']} - MST: {row['Mã Số Thuế']}"):
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"📍 **ĐC:** {row['Địa Chỉ']}")
                maps_q = urllib.parse.quote(str(row['Địa Chỉ']))
                st.markdown(f"🌍 [Xem trên Google Maps](https://google.com{maps_q})")
                st.caption(f"🕒 Cập nhật: {row['Cập Nhật Cuối']}")
            with c2:
                st.write(f"👤 **Chủ:** {row['Chủ Doanh Nghiệp']} | 📞 **SĐT:** {row['Liên Hệ']}")
                pure_z = clean_phone(row['Liên Hệ'])
                st.markdown(f"""<a href="https://zalo.me{pure_z}" target="_blank" style="text-decoration: none;"><div style="background-color: #0068FF; color: white; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold;">💬 NHẮN ZALO NGAY</div></a>""", unsafe_allow_html=True)
            
            # Chỉ Admin mới thấy nút Sửa/Xóa
            if st.session_state["role"] == "admin":
                ce, cd = st.columns(2)
                with ce:
                    if st.button(f"📝 Sửa", key=f"e_{i}"): st.session_state[f"edit_{i}"] = True
                with cd:
                    if st.button(f"🗑️ Xóa", key=f"d_{i}"):
                        df.drop(i).to_excel(DATA_FILE, index=False)
                        st.rerun()
                
                if st.session_state.get(f"edit_{i}"):
                    with st.form(f"f_edit_{i}"):
                        en = st.text_input("Tên", value=row['Tên Công Ty'])
                        em = st.text_input("MST", value=row['Mã Số Thuế'])
                        eo = st.text_input("Chủ", value=row['Chủ Doanh Nghiệp'])
                        ea = st.text_input("Địa chỉ", value=row['Địa Chỉ'])
                        ep = st.text_input("SĐT", value=row['Liên Hệ'])
                        if st.form_submit_button("Xác nhận Cập nhật"):
                            df.iloc[i] = [en, em, eo, ea, ep, f"https://zalo.me{clean_phone(ep)}", datetime.now().strftime("%d/%m/%Y %H:%M")]
                            df.to_excel(DATA_FILE, index=False)
                            st.session_state[f"edit_{i}"] = False
                            st.rerun()
else: st.info("Chưa có dữ liệu.")

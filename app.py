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
    if username in users["username"].values or username == ADMIN_USER:
        return False
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
                if col not in df.columns: df[col] = "Chưa có"
            return df[COLUMNS]
        except: return pd.DataFrame(columns=COLUMNS)
    return pd.DataFrame(columns=COLUMNS)

def clean_phone(phone):
    return re.sub(r'\D', '', str(phone))

# --- 3. GIAO DIỆN ĐĂNG NHẬP / ĐĂNG KÝ / KHÁCH ---
st.set_page_config(page_title="TEETA CODE", layout="wide")

if "role" not in st.session_state:
    st.session_state["role"] = None

if st.session_state["role"] is None:
    st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>TEETA CODE</h1>", unsafe_allow_html=True)
    t1, t2, t3, t4 = st.tabs(["🔑 Đăng nhập", "📝 Đăng ký", "🛡️ Quản trị viên", "🌐 Vào App (Khách)"])
    
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
        u_reg = st.text_input("Tên mới", key="u_reg")
        p_reg = st.text_input("Mật khẩu mới", type="password", key="p_reg")
        if st.button("Hoàn tất Đăng ký", use_container_width=True):
            if u_reg and p_reg and save_user(u_reg, p_reg): st.success("Xong! Qua tab Đăng nhập nhé.")
            else: st.error("Tên đã tồn tại!")
    
    with t3:
        ua = st.text_input("Tài khoản Admin", key="ua_ad")
        pa = st.text_input("Mật khẩu Admin", type="password", key="pa_ad")
        if st.button("Đăng nhập quyền Admin", use_container_width=True):
            role = authenticate(ua, pa, "admin")
            if role:
                st.session_state["role"], st.session_state["username"] = role, "CHỦ APP"
                st.rerun()
            else: st.error("Thông tin Admin không chính xác!")

    with t4:
        st.info("Chế độ Khách: Chỉ xem dữ liệu.")
        if st.button("VÀO XEM NGAY (FREE)", use_container_width=True):
            st.session_state["role"] = "guest"
            st.session_state["username"] = "Khách"
            st.rerun()
    st.stop()

# --- 4. GIAO DIỆN CHÍNH ---
st.markdown("<div style='text-align: center; margin-top: -60px;'> <h1 style='color: #FF4B4B; font-family: Arial Black; font-size: 45px;'>TEETA <span style='color: #31333F;'>CODE</span></h1> </div>", unsafe_allow_html=True)

st.sidebar.write(f"👤 Chào: **{st.session_state['username']}**")
if st.sidebar.button("Đăng xuất"):
    st.session_state["role"] = None; st.rerun()

# --- PHẦN NHẠC: ĐÃ SỬA LỖI LINK TRONG ẢNH ---
st.sidebar.divider()
st.sidebar.subheader("🎵 TEETA MUSIC")
music_id = "3I0zIK1X0vk" 
# Link chuẩn phải có dấu / sau youtube.com và chữ embed/
music_url = f"https://youtube.com{music_id}"

music_html = f"""
    <iframe width="100%" height="180" 
    src="{music_url}?autoplay=1&mute=0&enablejsapi=1" 
    frameborder="0" allow="autoplay; encrypted-media" id="video-player"></iframe>
    <script>
      var tag = document.createElement('script');
      tag.src = "https://youtube.com";
      var firstScriptTag = document.getElementsByTagName('script');
      firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

      var player;
      function onYouTubeIframeAPIReady() {{
        player = new YT.Player('video-player', {{
          events: {{
            'onReady': function(event) {{
              event.target.setVolume(50);
              event.target.playVideo();
            }}
          }}
        }});
      }}
    </script>
"""
with st.sidebar:
    st.components.v1.html(music_html, height=200)
st.sidebar.caption("🎧 Nhạc tự phát 50%. Hãy chạm vào App 1 lần để nghe tiếng.")

df = load_data()

# PHÂN QUYỀN
if st.session_state["role"] == "admin":
    st.sidebar.divider()
    st.sidebar.subheader("➕ Thêm Công Ty")
    search_mst = st.sidebar.text_input("🔍 Gõ MST tra cứu")
    n_v, a_v = "", ""
    if search_mst:
        info = get_business_info(search_mst)
        if info: n_v, a_v = info.get('name', ''), info.get('address', '')
    with st.sidebar.form("add", clear_on_submit=True):
        fn = st.text_input("Tên", value=n_v); fm = st.text_input("MST", value=search_mst); fp = st.text_input("SĐT")
        if st.form_submit_button("Lưu"):
            now = datetime.now().strftime("%d/%m/%Y %H:%M")
            new_row = pd.DataFrame([[fn, fm, "", a_v, fp, f"https://zalo.me{clean_phone(fp)}", now]], columns=COLUMNS)
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_excel(DATA_FILE, index=False); st.rerun()

# TRA CỨU
q = st.text_input("🔎 Tìm công ty...")
if not df.empty:
    f_df = df[df['Tên Công Ty'].str.contains(q, case=False, na=False) | df['Mã Số Thuế'].str.contains(q, case=False, na=False)] if q else df
    for i, row in f_df.iterrows():
        with st.expander(f"🏢 {row['Tên Công Ty']} - {row['Mã Số Thuế']}"):
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"📍 {row['Địa Chỉ']}")
                st.markdown(f"🌍 [Bản đồ](https://google.com{urllib.parse.quote(str(row['Địa Chỉ']))})")
            with c2:
                st.write(f"📞 {row['Liên Hệ']} | [💬 Zalo]({row['Zalo']})")
            if st.session_state["role"] == "admin":
                if st.button("🗑️ Xóa", key=f"d_{i}"): df.drop(i).to_excel(DATA_FILE, index=False); st.rerun()
else: st.info("Danh sách trống.")

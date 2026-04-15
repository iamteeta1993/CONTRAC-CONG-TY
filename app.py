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

# Hàm làm sạch số điện thoại để link Zalo không bị lỗi
def clean_phone(phone):
    return re.sub(r'\D', '', str(phone))

# --- 3. GIAO DIỆN ĐĂNG NHẬP ---
st.set_page_config(page_title="TEETA CODE - QUẢN TRỊ", layout="wide")
if "role" not in st.session_state: st.session_state["role"] = None

if st.session_state["role"] is None:
    st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>TEETA CODE</h1>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🔑 Đăng nhập", "📝 Đăng ký", "🛡️ Quản trị viên"])
    with t3:
        ua = st.text_input("Tài khoản Admin", key="ua")
        pa = st.text_input("Mật khẩu Admin", type="password", key="pa")
        if st.button("Vào quyền Quản trị", use_container_width=True):
            role = authenticate(ua, pa, "admin")
            if role:
                st.session_state["role"], st.session_state["username"] = role, "CHỦ APP"
                st.rerun()
            else: st.error("Sai thông tin Admin!")
    with t1:
        u = st.text_input("User", key="u"); p = st.text_input("Pass", type="password", key="p")
        if st.button("Vào xem dữ liệu"):
            role = authenticate(u, p, "user")
            if role: st.session_state["role"], st.session_state["username"] = role, u; st.rerun()
    st.stop()

# --- 4. GIAO DIỆN CHÍNH ---
st.markdown(f"<h1 style='text-align: center; color: #FF4B4B;'>TEETA CODE {'(ADMIN)' if st.session_state['role'] == 'admin' else ''}</h1>", unsafe_allow_html=True)
if st.sidebar.button("Đăng xuất"): st.session_state["role"] = None; st.rerun()

df = load_data()

if st.session_state["role"] == "admin":
    st.sidebar.subheader("➕ Thêm Công Ty")
    search_api = st.sidebar.text_input("🔍 Tra cứu nhanh MST/Tên")
    name_v, mst_v, addr_v = "", "", ""
    if search_api:
        info = get_business_info(search_api)
        if info: name_v, mst_v, addr_v = info.get('name', ''), info.get('id', ''), info.get('address', '')
    
    with st.sidebar.form("add_form", clear_on_submit=True):
        f_name = st.text_input("Tên", value=name_v); f_mst = st.text_input("MST", value=mst_v)
        f_owner = st.text_input("Chủ"); f_addr = st.text_input("Địa chỉ", value=addr_v)
        f_phone = st.text_input("SĐT")
        if st.form_submit_button("Lưu Mới", use_container_width=True):
            now = datetime.now().strftime("%d/%m/%Y %H:%M")
            pure_phone = clean_phone(f_phone)
            new_row = pd.DataFrame([[f_name, f_mst, f_owner, f_addr, f_phone, f"https://zalo.me{pure_phone}", now]], columns=COLUMNS)
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_excel(DATA_FILE, index=False); st.rerun()

# TRA CỨU
q = st.text_input("🔎 Tìm nhanh trong danh sách...")
if not df.empty:
    filtered_df = df[df['Tên Công Ty'].astype(str).str.contains(q, case=False, na=False) | df['Mã Số Thuế'].astype(str).str.contains(q, case=False, na=False)] if q else df
    
    for i, row in filtered_df.iterrows():
        with st.expander(f"🏢 {row['Tên Công Ty']} - MST: {row['Mã Số Thuế']}"):
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"📍 **ĐC:** {row['Địa Chỉ']}")
                clean_addr = urllib.parse.quote(str(row['Địa Chỉ']))
                st.markdown(f"🌍 [Xem trên Google Maps](https://google.com{clean_addr})")
                st.caption(f"🕒 Cập nhật: {row['Cập Nhật Cuối']}")
            with c2:
                st.write(f"👤 **Chủ:** {row['Chủ Doanh Nghiệp']} | 📞 **SĐT:** {row['Liên Hệ']}")
                # NÚT ZALO XỊN
                pure_p = clean_phone(row['Liên Hệ'])
                st.markdown(f"""<a href="https://zalo.me{pure_p}" target="_blank" style="text-decoration: none;"><div style="background-color: #0068FF; color: white; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold;">💬 NHẮN ZALO NGAY</div></a>""", unsafe_allow_html=True)
            
            if st.session_state["role"] == "admin":
                ce, cd = st.columns(2)
                with ce:
                    if st.button(f"📝 Sửa", key=f"e_{i}"): st.session_state[f"edit_{i}"] = True
                with cd:
                    if st.button(f"🗑️ Xóa", key=f"d_{i}"): df.drop(i).to_excel(DATA_FILE, index=False); st.rerun()
                
                if st.session_state.get(f"edit_{i}"):
                    with st.form(f"f_edit_{i}"):
                        en = st.text_input("Tên", value=row['Tên Công Ty']); em = st.text_input("MST", value=row['Mã Số Thuế'])
                        eo = st.text_input("Chủ", value=row['Chủ Doanh Nghiệp']); ea = st.text_input("Địa chỉ", value=row['Địa Chỉ'])
                        ep = st.text_input("SĐT", value=row['Liên Hệ'])
                        if st.form_submit_button("Xác nhận Cập nhật"):
                            pure_ep = clean_phone(ep)
                            df.iloc[i] = [en, em, eo, ea, ep, f"https://zalo.me{pure_ep}", datetime.now().strftime("%d/%m/%Y %H:%M")]
                            df.to_excel(DATA_FILE, index=False)
                            st.session_state[f"edit_{i}"] = False; st.rerun()
else: st.info("Chưa có dữ liệu.")
# --- TRÌNH PHÁT NHẠC TEETA MUSIC ---
st.sidebar.divider()
st.sidebar.subheader("🎵 Nhạc Làm Việc")

# Link bản nhạc bạn vừa gửi
default_music = "https://www.youtube.com/watch?v=HaIjR05n1Vc"

# Tạo ô dán link (đã để sẵn link nhạc của bạn làm mặc định)
url = st.sidebar.text_input("Dán link YouTube khác nếu muốn đổi nhạc:", value=default_music)

if url:
    # Trình phát này của Streamlit cho phép người dùng tự:
    # 1. Bấm Dừng/Phát
    # 2. Kéo thanh âm lượng (Tắt âm)
    # 3. Tua nhạc
    st.sidebar.video(url)
    st.sidebar.caption("🎧 Bạn có thể tùy chỉnh Âm lượng hoặc Tạm dừng ngay trên thanh điều khiển phía trên.")

st.sidebar.write("---")
# --- TRÌNH PHÁT NHẠC THÔNG MINH (AUTOPLAY 50%) ---
st.sidebar.divider()
st.sidebar.subheader("🎵 TEETA MUSIC")

# Sử dụng mã nhúng HTML để kiểm soát âm lượng 50%
st.sidebar.components.v1.html(
    """
    <div id="player"></div>
    <script src="https://youtube.com"></script>
    <script>
        var player;
        function onYouTubeIframeAPIReady() {
            player = new YT.Player('player', {
                height: '180',
                width: '100%',
                videoId: 'HaIjR05n1Vc',
                playerVars: {
                    'autoplay': 1,
                    'controls': 1,
                    'mute': 0
                },
                events: {
                    'onReady': onPlayerReady
                }
            });
        }
        function onPlayerReady(event) {
            event.target.setVolume(50); 
            event.target.playVideo();
        }
    </script>
    """,
    height=200,
)
st.sidebar.caption("🎧 Nhạc tự phát 50%. Bạn có thể tùy chỉnh to nhỏ.")

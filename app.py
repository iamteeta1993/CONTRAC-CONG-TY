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
        # API VietQR v2 chính xác
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
            
    with t2:
        nu = st.text_input("Tên đăng ký", key="reg_u")
        np = st.text_input("Mật khẩu", type="password", key="reg_p")
        if st.button("TẠO TÀI KHOẢN", use_container_width=True):
            if nu and np:
                if save_user(nu, np): st.success("Đăng ký thành công! Hãy đăng nhập.")
                else: st.error("Tên người dùng đã tồn tại.")
            else: st.warning("Vui lòng nhập đầy đủ.")

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
        st.info("Chế độ Khách: Chỉ xem các thông tin công khai.")
        if st.button("VÀO XEM (FREE)", use_container_width=True):
            st.session_state["role"], st.session_state["username"] = "guest", "Khách"
            st.rerun()
    st.stop()

# --- 4. GIAO DIỆN CHÍNH ---
st.markdown("<div style='text-align: center; margin-top: -60px;'> <h1 style='color: #FF4B4B; font-family: Arial Black;'>TEETA <span style='color: #31333F;'>CODE</span></h1> </div>", unsafe_allow_html=True)

# SIDEBAR
st.sidebar.subheader(f"👋 {st.session_state['username']}")
st.sidebar.write(f"Quyền hạn: **{st.session_state['role'].upper()}**")
if st.sidebar.button("Đăng xuất"): 
    st.session_state["role"] = None
    st.rerun()

# --- SIDEBAR: GIẢI TRÍ (SPOTIFY & YOUTUBE) ---
st.sidebar.divider()
st.sidebar.subheader("🎵 Giải Trí")
tab_music, tab_video = st.sidebar.tabs(["Spotify", "YouTube"])

with tab_music:
    # Link Playlist Spotify
    spotify_url = "https://open.spotify.com/embed/playlist/37i9dQZF1DXcBWIGoYBM5M" # Playlist Focus
    st.components.v1.html(f"""
        <iframe src="{spotify_url}" width="100%" height="152" frameBorder="0" 
        allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" 
        style="border-radius:12px;"></iframe>
    """, height=160)

with tab_video:
    # ID Video YouTube (Lofi Music)
    yt_id = "jfKfPfyJRdk" 
    st.components.v1.html(f"""
        <iframe width="100%" height="152" src="https://www.youtube.com/embed/{yt_id}" 
        frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
        allowfullscreen style="border-radius:12px;"></iframe>
    """, height=160)

# --- QUẢN LÝ DỮ LIỆU ---
df = load_data()

if st.session_state["role"] == "admin":
    st.sidebar.divider()
    st.sidebar.subheader("➕ Thêm Công Ty")
    search_mst = st.sidebar.text_input("🔍 Tra MST nhanh")
    n_v, a_v = "", ""
    
    if search_mst:
        info = get_business_info(search_mst)
        if info: 
            n_v, a_v = info.get('name', ''), info.get('address', '')
            st.sidebar.success("Đã tìm thấy dữ liệu!")
        else: st.sidebar.warning("Không tìm thấy MST này.")
            
    with st.sidebar.form("add_form", clear_on_submit=True):
        fn = st.text_input("Tên Công Ty", value=n_v)
        fm = st.text_input("Mã Số Thuế", value=search_mst)
        fa = st.text_input("Địa chỉ", value=a_v)
        fp = st.text_input("Số điện thoại")
        fg = st.text_area("Ghi chú")
        if st.form_submit_button("LƯU VÀO HỆ THỐNG"):
            now = datetime.now().strftime("%d/%m/%Y %H:%M")
            new_row = pd.DataFrame([[fn, fm, "", fa, fp, fg, f"https://zalo.me/{clean_phone(fp)}", now]], columns=COLUMNS)
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_excel(DATA_FILE, index=False)
            st.success("Đã lưu thành công!")
            st.rerun()

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "rb") as f:
            st.sidebar.download_button("📥 Xuất file Excel", f, file_name="data_teetacode.xlsx")

# --- TRANG CHỦ: TÌM KIẾM & HIỂN THỊ ---
q = st.text_input("🔎 Nhập Tên Công Ty hoặc Mã Số Thuế để tìm kiếm...")

if not df.empty:
    # Lọc dữ liệu
    f_df = df[df['Tên Công Ty'].str.contains(q, case=False, na=False) | 
              df['Mã Số Thuế'].str.contains(q, case=False, na=False)] if q else df
    
    st.write(f"Tìm thấy **{len(f_df)}** kết quả.")

    for i, row in f_df.iterrows():
        with st.expander(f"🏢 {row['Tên Công Ty']} - {row['Mã Số Thuế']}"):
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**📍 Địa chỉ:** {row['Địa Chỉ']}")
                # Sửa link Google Maps
                maps_q = urllib.parse.quote(str(row['Địa Chỉ']))
                st.markdown(f"🌍 [Xem bản đồ](https://www.google.com/maps/search/?api=1&query={maps_q})")
                
                if st.session_state["role"] in ["admin", "user"]:
                    st.info(f"📝 **Ghi chú nội bộ:** {row['Ghi Chú']}")
            
            with c2:
                st.write(f"**📞 Liên hệ:** {row['Liên Hệ']}")
                z_link = f"https://zalo.me/{clean_phone(row['Liên Hệ'])}"
                st.markdown(f"""
                    <a href="{z_link}" target="_blank" style="text-decoration:none;">
                        <div style="background-color:#0068FF;color:white;padding:10px;border-radius:10px;text-align:center;font-weight:bold;">
                            💬 NHẮN ZALO NGAY
                        </div>
                    </a>
                """, unsafe_allow_html=True)
                st.caption(f"Cập nhật lúc: {row['Cập Nhật Cuối']}")

            if st.session_state["role"] == "admin":
                if st.button("🗑️ Xóa dữ liệu này", key=f"del_{i}"):
                    df = df.drop(i)
                    df.to_excel(DATA_FILE, index=False)
                    st.rerun()
else:
    st.info("Hệ thống chưa có dữ liệu. Vui lòng đăng nhập quyền Admin để thêm.")

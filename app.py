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
        # Sửa lại URL API VietQR chính xác
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
st.set_page_config(page_title="TEETA CODE", layout="wide")
if "role" not in st.session_state: st.session_state["role"] = None

if st.session_state["role"] is None:
    st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>TEETA CODE</h1>", unsafe_allow_html=True)
    t1, t2, t3, t4 = st.tabs(["🔑 Thành viên", "📝 Đăng ký", "🛡️ Admin", "🌐 Khách"])
    
    with t1:
        u = st.text_input("Username", key="u_login")
        p = st.text_input("Password", type="password", key="p_login")
        if st.button("ĐĂNG NHẬP THÀNH VIÊN"):
            r = authenticate(u, p, "user")
            if r: 
                st.session_state["role"], st.session_state["username"] = r, u
                st.rerun()
            else: st.error("Sai thông tin đăng nhập!")
            
    with t2:
        nu = st.text_input("Tên đăng ký", key="u_reg")
        np = st.text_input("Mật khẩu", type="password", key="p_reg")
        if st.button("TẠO TÀI KHOẢN"):
            if nu and np:
                if save_user(nu, np): st.success("Đăng ký thành công! Hãy qua tab Đăng nhập.")
                else: st.error("Tên này đã tồn tại.")
            else: st.warning("Vui lòng điền đủ thông tin.")

    with t3:
        ua = st.text_input("Admin User", key="u_admin")
        pa = st.text_input("Admin Pass", type="password", key="p_admin")
        if st.button("XÁC NHẬN ADMIN"):
            r = authenticate(ua, pa, "admin")
            if r: 
                st.session_state["role"], st.session_state["username"] = r, "CHỦ APP"
                st.rerun()
            else: st.error("Sai mã quản trị!")
            
    with t4:
        st.info("Chế độ Khách: Chỉ xem thông tin công khai.")
        if st.button("VÀO XEM (FREE)"):
            st.session_state["role"], st.session_state["username"] = "guest", "Khách"
            st.rerun()
    st.stop()

# --- 4. GIAO DIỆN CHÍNH ---
st.markdown("<div style='text-align: center; margin-top: -60px;'> <h1 style='color: #FF4B4B; font-family: Arial Black;'>TEETA <span style='color: #31333F;'>CODE</span></h1> </div>", unsafe_allow_html=True)

st.sidebar.write(f"👤 Quyền: **{st.session_state['role'].upper()}**")
st.sidebar.write(f"👋 Chào: **{st.session_state['username']}**")
if st.sidebar.button("Thoát"): 
    st.session_state["role"] = None
    st.rerun()

# NHẠC ZING MP3 
st.sidebar.divider()
zing_html = '<iframe title="Zing MP3" width="100%" height="200" src="https://zingmp3.vn" frameborder="0" allowfullscreen="true"></iframe>'
with st.sidebar: st.components.v1.html(zing_html, height=210)

df = load_data()

# PHÂN QUYỀN TRÊN SIDEBAR
if st.session_state["role"] == "admin":
    st.sidebar.subheader("➕ Thêm Công Ty")
    search_mst = st.sidebar.text_input("🔍 Gõ MST tra nhanh")
    n_v, a_v = "", ""
    if search_mst:
        info = get_business_info(search_mst)
        if info: 
            n_v, a_v = info.get('name', ''), info.get('address', '')
            st.sidebar.success("Tìm thấy thông tin!")
        else: st.sidebar.warning("Không tìm thấy MST này.")
            
    with st.sidebar.form("add_form", clear_on_submit=True):
        fn = st.text_input("Tên Công Ty", value=n_v)
        fm = st.text_input("Mã Số Thuế", value=search_mst)
        fa = st.text_input("Địa chỉ", value=a_v)
        fp = st.text_input("Số Điện Thoại")
        fg = st.text_area("Ghi chú nội bộ")
        if st.form_submit_button("LƯU DỮ LIỆU"):
            now = datetime.now().strftime("%d/%m/%Y %H:%M")
            new_row = pd.DataFrame([[fn, fm, "", fa, fp, fg, f"https://zalo.me/{clean_phone(fp)}", now]], columns=COLUMNS)
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_excel(DATA_FILE, index=False)
            st.success("Đã thêm!")
            st.rerun()

    # Nút tải file Excel
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "rb") as f:
            st.sidebar.download_button("📥 Tải Database (Excel)", f, file_name=f"Data_{datetime.now().strftime('%d%m')}.xlsx")

# TRANG CHÍNH: TRA CỨU
q = st.text_input("🔎 Tìm kiếm tên công ty hoặc mã số thuế...")
if not df.empty:
    f_df = df[df['Tên Công Ty'].str.contains(q, case=False, na=False) | df['Mã Số Thuế'].str.contains(q, case=False, na=False)] if q else df
    
    st.write(f"Kết quả: {len(f_df)} công ty")
    
    for i, row in f_df.iterrows():
        with st.expander(f"🏢 {row['Tên Công Ty']} - MST: {row['Mã Số Thuế']}"):
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**📍 Địa chỉ:** {row['Địa Chỉ']}")
                maps_url = f"https://www.google.com/maps/search/{urllib.parse.quote(str(row['Địa Chỉ']))}"
                st.markdown(f"🌍 [Mở Google Maps]({maps_url})")
                
                if st.session_state["role"] in ["admin", "user"]:
                    st.info(f"📝 **Ghi chú:** {row['Ghi Chú']}")
            
            with c2:
                st.write(f"**📞 Liên hệ:** {row['Liên Hệ']}")
                zalo_link = f"https://zalo.me/{clean_phone(row['Liên Hệ'])}"
                st.markdown(f"""<a href="{zalo_link}" target="_blank" style="text-decoration:none;"><div style="background-color:#0068FF;color:white;padding:10px;border-radius:10px;text-align:center;font-weight:bold;">💬 NHẮN ZALO</div></a>""", unsafe_allow_html=True)
            
            if st.session_state["role"] == "admin":
                if st.button("🗑️ Xóa công ty này", key=f"del_{i}"):
                    df = df.drop(i)
                    df.to_excel(DATA_FILE, index=False)
                    st.rerun()
else:
    st.info("Hiện chưa có dữ liệu trong hệ thống.")

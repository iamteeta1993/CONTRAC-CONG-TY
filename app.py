import streamlit as st
import pandas as pd
import os
import requests
import hashlib

# --- 1. CẤU HÌNH HỆ THỐNG ---
USER_FILE = "users.xlsx"
DATA_FILE = "data_congty.xlsx"
COLUMNS = ["Tên Công Ty", "Mã Số Thuế", "Chủ Doanh Nghiệp", "Địa Chỉ", "Liên Hệ", "Zalo"]

# TÀI KHOẢN ADMIN DUY NHẤT CỦA BẠN (Bạn có thể đổi ở đây)
ADMIN_USER = "admin" 
ADMIN_PASS = "teeta123"

# --- 2. HÀM HỆ THỐNG ---
def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def load_users():
    if os.path.exists(USER_FILE):
        return pd.read_excel(USER_FILE, dtype=str)
    return pd.DataFrame(columns=["username", "password"])

def save_user(username, password):
    users = load_users()
    if username in users["username"].values or username == ADMIN_USER:
        return False
    new_user = pd.DataFrame([{"username": username, "password": hash_password(password)}])
    users = pd.concat([users, new_user], ignore_index=True)
    users.to_excel(USER_FILE, index=False)
    return True

def authenticate(username, password, login_type):
    if login_type == "admin":
        if username == ADMIN_USER and password == ADMIN_PASS:
            return "admin"
    else:
        users = load_users()
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
        df = pd.read_excel(DATA_FILE, dtype=str)
        for col in COLUMNS:
            if col not in df.columns: df[col] = ""
        return df
    return pd.DataFrame(columns=COLUMNS)

# --- 3. GIAO DIỆN ĐĂNG NHẬP ---
st.set_page_config(page_title="TEETA CODE", layout="wide")

if "role" not in st.session_state:
    st.session_state["role"] = None

if st.session_state["role"] is None:
    st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>TEETA CODE</h1>", unsafe_allow_html=True)
    
    # ĐÂY LÀ CHỖ THAY ĐỔI: Thêm tab Quản trị viên đúng vị trí bạn muốn
    tab1, tab2, tab3 = st.tabs(["🔑 Đăng nhập", "📝 Đăng ký tài khoản", "🛡️ Quản trị viên"])
    
    with tab1:
        u = st.text_input("Tên đăng nhập", key="u_user")
        p = st.text_input("Mật khẩu", type="password", key="p_user")
        if st.button("Xác nhận Đăng nhập", use_container_width=True):
            role = authenticate(u, p, "user")
            if role:
                st.session_state["role"] = role
                st.session_state["username"] = u
                st.rerun()
            else: st.error("Sai tài khoản hoặc mật khẩu người dùng!")
            
    with tab2:
        st.info("Đăng ký tài khoản dành cho người xem dữ liệu.")
        u2 = st.text_input("Tạo tên đăng nhập", key="u_reg")
        p2 = st.text_input("Tạo mật khẩu", type="password", key="p_reg")
        if st.button("Hoàn tất Đăng ký", use_container_width=True):
            if u2 and p2:
                if save_user(u2, p2): st.success("Thành công! Mời bạn qua tab Đăng nhập.")
                else: st.error("Tên đăng nhập này đã tồn tại!")
                
    with tab3:
        st.warning("Khu vực dành riêng cho Chủ sở hữu App.")
        ua = st.text_input("Tài khoản Admin", key="u_admin")
        pa = st.text_input("Mật khẩu Admin", type="password", key="p_admin")
        if st.button("Đăng nhập quyền Admin", use_container_width=True):
            role = authenticate(ua, pa, "admin")
            if role:
                st.session_state["role"] = role
                st.session_state["username"] = "CHỦ APP"
                st.rerun()
            else: st.error("Thông tin Admin không chính xác!")
    st.stop()

# --- 4. GIAO DIỆN SAU KHI ĐĂNG NHẬP ---
st.markdown(f"<h1 style='text-align: center; color: #FF4B4B;'>TEETA CODE {'(QUẢN TRỊ)' if st.session_state['role'] == 'admin' else ''}</h1>", unsafe_allow_html=True)

st.sidebar.write(f"👤 Chào: **{st.session_state['username']}**")
if st.sidebar.button("Đăng xuất"):
    st.session_state["role"] = None
    st.rerun()

df = load_data()

# CHỈ ADMIN MỚI THẤY PHẦN THÊM CÔNG TY
if st.session_state["role"] == "admin":
    st.sidebar.divider()
    st.sidebar.subheader("➕ Thêm Công Ty")
    search_api = st.sidebar.text_input("🔍 Tra cứu nhanh MST/Tên")
    name_v, mst_v, addr_v = "", "", ""
    if search_api:
        info = get_business_info(search_api)
        if info: name_v, mst_v, addr_v = info.get('name', ''), info.get('id', ''), info.get('address', '')
    
    with st.sidebar.form("add_form", clear_on_submit=True):
        f_name = st.text_input("Tên Công Ty", value=name_v)
        f_mst = st.text_input("Mã Số Thuế", value=mst_v)
        f_owner = st.text_input("Chủ Doanh Nghiệp")
        f_phone = st.text_input("Số Điện Thoại")
        if st.form_submit_button("Lưu Vào Hệ Thống", use_container_width=True):
            if f_name and f_mst:
                new_row = pd.DataFrame([[f_name, f_mst, f_owner, addr_v, f_phone, f"https://zalo.me{f_phone}"]], columns=COLUMNS)
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_excel(DATA_FILE, index=False)
                st.rerun()
else:
    st.sidebar.info("Bạn đang ở chế độ Xem. Vui lòng liên hệ Admin nếu cần chỉnh sửa.")

# TRANG CHÍNH: TRA CỨU
q = st.text_input("🔎 Tìm nhanh công ty...")
if not df.empty:
    display_df = df[df['Tên Công Ty'].str.contains(q, case=False, na=False) | df['Mã Số Thuế'].str.contains(q, case=False, na=False)] if q else df
    for i, row in display_df.iterrows():
        with st.expander(f"🏢 {row['Tên Công Ty']} - MST: {row['Mã Số Thuế']}"):
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"📍 **ĐC:** {row['Địa Chỉ']}")
                st.write(f"👤 **Chủ:** {row['Chủ Doanh Nghiệp']}")
            with c2:
                st.write(f"📞 **SĐT:** {row['Liên Hệ']} | [💬 Zalo]({row['Zalo']})")
            
            if st.session_state["role"] == "admin":
                if st.button(f"🗑️ Xóa công ty này", key=f"del_{i}"):
                    df.drop(i).to_excel(DATA_FILE, index=False)
                    st.rerun()
else:
    st.info("Chưa có dữ liệu.")

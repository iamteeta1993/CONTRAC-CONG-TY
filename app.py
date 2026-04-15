import streamlit as st
import pandas as pd
import os
import requests
import hashlib

# --- 1. CẤU HÌNH FILE & DỮ LIỆU ---
USER_FILE = "users.xlsx"
DATA_FILE = "data_congty.xlsx"
COLUMNS = ["Tên Công Ty", "Mã Số Thuế", "Chủ Doanh Nghiệp", "Địa Chỉ", "Liên Hệ", "Zalo"]

# --- 2. HÀM HỆ THỐNG (TÀI KHOẢN & BẢO MẬT) ---
def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def load_users():
    if os.path.exists(USER_FILE):
        return pd.read_excel(USER_FILE, dtype=str)
    return pd.DataFrame(columns=["username", "password"])

def save_user(username, password):
    users = load_users()
    if username in users["username"].values:
        return False
    new_user = pd.DataFrame([{"username": username, "password": hash_password(password)}])
    users = pd.concat([users, new_user], ignore_index=True)
    users.to_excel(USER_FILE, index=False)
    return True

def authenticate(username, password):
    users = load_users()
    hashed_pwd = hash_password(password)
    return not users[(users["username"] == username) & (users["password"] == hashed_pwd)].empty

def get_business_info(keyword):
    try:
        response = requests.get(f"https://vietqr.io{keyword}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == "00":
                return data.get('data')
        return None
    except:
        return None

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_excel(DATA_FILE, dtype=str)
            for col in COLUMNS:
                if col not in df.columns: df[col] = ""
            return df
        except:
            return pd.DataFrame(columns=COLUMNS)
    return pd.DataFrame(columns=COLUMNS)

# --- 3. GIAO DIỆN ĐĂNG NHẬP / ĐĂNG KÝ ---
st.set_page_config(page_title="TEETA CODE - Quản Lý Công Ty", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    # Logo cho trang đăng nhập
    st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>TEETA CODE</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 Đăng nhập", "📝 Đăng ký tài khoản"])
    
    with tab1:
        u1 = st.text_input("Tên đăng nhập", key="u1")
        p1 = st.text_input("Mật khẩu", type="password", key="p1")
        if st.button("Xác nhận Đăng nhập"):
            if authenticate(u1, p1):
                st.session_state["logged_in"] = True
                st.session_state["username"] = u1
                st.rerun()
            else:
                st.error("Sai tài khoản hoặc mật khẩu!")

    with tab2:
        u2 = st.text_input("Tạo tên đăng nhập", key="u2")
        p2 = st.text_input("Tạo mật khẩu", type="password", key="p2")
        if st.button("Hoàn tất Đăng ký"):
            if u2 and p2:
                if save_user(u2, p2):
                    st.success("Tạo tài khoản thành công! Mời bạn qua tab Đăng nhập.")
                else:
                    st.error("Tên đăng nhập này đã tồn tại!")
            else:
                st.warning("Vui lòng nhập đủ thông tin.")
    st.stop()

# --- 4. GIAO DIỆN CHÍNH (SAU KHI ĐĂNG NHẬP) ---

# Hiển thị Logo TEETA CODE ở giữa trên cùng
st.markdown(
    """
    <div style="text-align: center; margin-top: -60px; margin-bottom: 10px;">
        <h1 style="color: #FF4B4B; font-family: 'Arial Black'; font-size: 45px; letter-spacing: 2px; text-shadow: 2px 2px #ddd;">
            TEETA <span style="color: #31333F;">CODE</span>
        </h1>
        <p style="color: gray; font-style: italic; margin-top: -15px;">Hệ Thống Quản Lý Dữ Liệu Doanh Nghiệp Nội Bộ</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.write(f"👤 Chào: **{st.session_state['username']}**")
if st.sidebar.button("Đăng xuất"):
    st.session_state["logged_in"] = False
    st.rerun()

df = load_data()

# SIDEBAR: THÊM CÔNG TY MỚI
st.sidebar.divider()
st.sidebar.subheader("➕ Thêm Công Ty")
search_api = st.sidebar.text_input("🔍 Tra cứu nhanh (Tên hoặc MST)")

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
    
    if st.form_submit_button("Lưu Vào Hệ Thống"):
        if f_name and f_mst:
            new_row = pd.DataFrame([[f_name, f_mst, f_owner, f_addr, f_phone, f"https://zalo.me{f_phone}"]], columns=COLUMNS)
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_excel(DATA_FILE, index=False)
            st.success("Đã lưu thành công!")
            st.rerun()
        else:
            st.error("Vui lòng nhập Tên và MST")

# TRANG CHÍNH: HIỂN THỊ DANH SÁCH
q = st.text_input("🔎 Tìm kiếm nhanh trong danh sách của bạn...")

if not df.empty:
    display_df = df[df['Tên Công Ty'].str.contains(q, case=False, na=False) | 
                    df['Mã Số Thuế'].str.contains(q, case=False, na=False)] if q else df
    
    for i, row in display_df.iterrows():
        with st.expander(f"🏢 {row['Tên Công Ty']} - MST: {row['Mã Số Thuế']}"):
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"👤 **Chủ:** {row['Chủ Doanh Nghiệp']}")
                st.write(f"📍 **Địa chỉ:** {row['Địa Chỉ']}")
            with c2:
                st.write(f"📞 **SĐT:** {row['Liên Hệ']}")
                st.write(f"💬 [Nhắn Zalo ngay]({row['Zalo']})")
            
            if st.button(f"🗑️ Xóa", key=f"del_{i}"):
                df.drop(i).to_excel(DATA_FILE, index=False)
                st.rerun()
else:
    st.info("Chưa có dữ liệu. Bạn hãy thêm công ty ở cột bên trái nhé!")

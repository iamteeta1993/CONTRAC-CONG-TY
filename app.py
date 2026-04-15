import streamlit as st
import pandas as pd
import os
import requests
import hashlib

# --- CẤU HÌNH FILE DỮ LIỆU ---
USER_FILE = "users.xlsx"
DATA_FILE = "data_congty.xlsx"
COLUMNS = ["Tên Công Ty", "Mã Số Thuế", "Chủ Doanh Nghiệp", "Địa Chỉ", "Liên Hệ", "Zalo"]

# --- HÀM BẢO MẬT & TÀI KHOẢN ---
def hash_password(password):
    """Mã hóa mật khẩu để không ai đọc được trong file Excel."""
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

# --- HÀM TRA CỨU DOANH NGHIỆP ---
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

# --- GIAO DIỆN ĐĂNG NHẬP / ĐĂNG KÝ ---
st.set_page_config(page_title="Hệ Thống Quản Lý", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    tab1, tab2 = st.tabs(["🔑 Đăng nhập", "📝 Đăng ký tài khoản"])
    
    with tab1:
        u1 = st.text_input("Tên đăng nhập", key="u1")
        p1 = st.text_input("Mật khẩu", type="password", key="p1")
        if st.button("Đăng nhập"):
            if authenticate(u1, p1):
                st.session_state["logged_in"] = True
                st.session_state["username"] = u1
                st.success("Đang đăng nhập...")
                st.rerun()
            else:
                st.error("Sai tài khoản hoặc mật khẩu!")

    with tab2:
        u2 = st.text_input("Tạo tên đăng nhập", key="u2")
        p2 = st.text_input("Tạo mật khẩu", type="password", key="p2")
        if st.button("Tạo tài khoản"):
            if u2 and p2:
                if save_user(u2, p2):
                    st.success("Đã tạo tài khoản thành công! Hãy qua tab Đăng nhập.")
                else:
                    st.error("Tên đăng nhập này đã tồn tại!")
            else:
                st.warning("Vui lòng điền đầy đủ thông tin.")
    st.stop()

# --- CHƯƠNG TRÌNH CHÍNH (SAU KHI ĐĂNG NHẬP) ---
st.sidebar.write(f"👋 Chào, **{st.session_state['username']}**")
if st.sidebar.button("Đăng xuất"):
    st.session_state["logged_in"] = False
    st.rerun()

# (Phần code quản lý Công ty giữ nguyên như cũ)
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_excel(DATA_FILE, dtype=str)
        for col in COLUMNS:
            if col not in df.columns: df[col] = ""
        return df
    return pd.DataFrame(columns=COLUMNS)

df = load_data()

# Sidebar: Thêm công ty
st.sidebar.divider()
st.sidebar.subheader("➕ Thêm Công Ty")
search_api = st.sidebar.text_input("🔍 Gõ Tên hoặc MST để tra cứu")

name_v, mst_v, addr_v = "", "", ""
if search_api:
    info = get_business_info(search_api)
    if info:
        name_v, mst_v, addr_v = info.get('name', ''), info.get('id', ''), info.get('address', '')
        st.sidebar.success("Tìm thấy dữ liệu!")

with st.sidebar.form("add_form", clear_on_submit=True):
    f_name = st.text_input("Tên", value=name_v)
    f_mst = st.text_input("MST", value=mst_v)
    f_addr = st.text_input("Địa chỉ", value=addr_v)
    f_phone = st.text_input("SĐT")
    if st.form_submit_button("Lưu"):
        new_row = pd.DataFrame([[f_name, f_mst, "", f_addr, f_phone, f"https://zalo.me{f_phone}"]], columns=COLUMNS)
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_excel(DATA_FILE, index=False)
        st.rerun()

# Giao diện chính
st.title("📂 Danh Sách Công Ty")
q = st.text_input("🔎 Tìm kiếm nhanh...")
if not df.empty:
    filtered = df[df['Tên Công Ty'].str.contains(q, case=False, na=False)] if q else df
    for i, row in filtered.iterrows():
        with st.expander(f"🏢 {row['Tên Công Ty']} - {row['Mã Số Thuế']}"):
            st.write(f"📍 {row['Địa Chỉ']} | 📞 {row['Liên Hệ']}")
            if st.button("🗑️ Xóa", key=f"d_{i}"):
                df.drop(i).to_excel(DATA_FILE, index=False)
                st.rerun()

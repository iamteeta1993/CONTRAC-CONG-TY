import streamlit as st
import pandas as pd
import os
import requests
import hashlib
from datetime import datetime

# --- 1. CẤU HÌNH HỆ THỐNG ---
USER_FILE = "users.xlsx"
DATA_FILE = "data_congty.xlsx"
COLUMNS = ["Tên Công Ty", "Mã Số Thuế", "Chủ Doanh Nghiệp", "Địa Chỉ", "Liên Hệ", "Zalo", "Cập Nhật Cuối"]

ADMIN_USER = "admin" 
ADMIN_PASS = "teeta123"

# --- 2. HÀM HỆ THỐNG ---
def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def load_users():
    if os.path.exists(USER_FILE):
        return pd.read_excel(USER_FILE, dtype=str)
    return pd.DataFrame(columns=["username", "password"])

def authenticate(username, password, login_type):
    if login_type == "admin":
        return "admin" if username == ADMIN_USER and password == ADMIN_PASS else None
    users = load_users()
    hashed_pwd = hash_password(password)
    return "user" if not users[(users["username"] == username) & (users["password"] == hashed_pwd)].empty else None

def get_business_info(keyword):
    try:
        res = requests.get(f"https://vietqr.io{keyword}", timeout=5)
        return res.json()['data'] if res.status_code == 200 and res.json()['code'] == "00" else None
    except: return None

def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_excel(DATA_FILE, dtype=str)
        for col in COLUMNS:
            if col not in df.columns: df[col] = "Chưa cập nhật"
        return df
    return pd.DataFrame(columns=COLUMNS)

# --- 3. GIAO DIỆN ĐĂNG NHẬP ---
st.set_page_config(page_title="TEETA CODE", layout="wide")
if "role" not in st.session_state: st.session_state["role"] = None

if st.session_state["role"] is None:
    st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>TEETA CODE</h1>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🔑 Đăng nhập", "📝 Đăng ký", "🛡️ Quản trị viên"])
    with t1:
        u = st.text_input("User")
        p = st.text_input("Pass", type="password")
        if st.button("Vào App"):
            role = authenticate(u, p, "user")
            if role: st.session_state["role"], st.session_state["username"] = role, u; st.rerun()
    with t3:
        ua = st.text_input("Admin User")
        pa = st.text_input("Admin Pass", type="password")
        if st.button("Vào quyền Quản trị"):
            role = authenticate(ua, pa, "admin")
            if role: st.session_state["role"], st.session_state["username"] = role, "CHỦ APP"; st.rerun()
    st.stop()

# --- 4. GIAO DIỆN CHÍNH ---
st.markdown(f"<h1 style='text-align: center; color: #FF4B4B;'>TEETA CODE {'(QUẢN TRỊ)' if st.session_state['role'] == 'admin' else ''}</h1>", unsafe_allow_html=True)
if st.sidebar.button("Đăng xuất"): st.session_state["role"] = None; st.rerun()

df = load_data()

# ADMIN: THÊM MỚI
if st.session_state["role"] == "admin":
    st.sidebar.subheader("➕ Thêm Công Ty")
    search_api = st.sidebar.text_input("🔍 Tra cứu nhanh")
    name_v, mst_v, addr_v = "", "", ""
    if search_api:
        info = get_business_info(search_api)
        if info: name_v, mst_v, addr_v = info.get('name', ''), info.get('id', ''), info.get('address', '')
    
    with st.sidebar.form("add_form", clear_on_submit=True):
        f_name = st.text_input("Tên", value=name_v)
        f_mst = st.text_input("MST", value=mst_v)
        f_owner = st.text_input("Chủ")
        f_phone = st.text_input("SĐT")
        if st.form_submit_button("Lưu Mới"):
            now = datetime.now().strftime("%d/%m/%Y %H:%M")
            new_row = pd.DataFrame([[f_name, f_mst, f_owner, addr_v, f_phone, f"https://zalo.me{f_phone}", now]], columns=COLUMNS)
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_excel(DATA_FILE, index=False); st.rerun()

# TRA CỨU & HIỂN THỊ
q = st.text_input("🔎 Tìm nhanh...")
if not df.empty:
    display_df = df[df['Tên Công Ty'].str.contains(q, case=False, na=False) | df['Mã Số Thuế'].str.contains(q, case=False, na=False)] if q else df
    for i, row in display_df.iterrows():
        with st.expander(f"🏢 {row['Tên Công Ty']} - MST: {row['Mã Số Thuế']}"):
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"📍 **ĐC:** {row['Địa Chỉ']}\n👤 **Chủ:** {row['Chủ Doanh Nghiệp']}")
                st.caption(f"🕒 Cập nhật: {row['Cập Nhật Cuối']}")
            with c2:
                st.write(f"📞 **SĐT:** {row['Liên Hệ']}\n💬 [Zalo]({row['Zalo']})")
            
            # CHỨC NĂNG ADMIN: SỬA & XÓA
            if st.session_state["role"] == "admin":
                col_e, col_d = st.columns(2)
                with col_e:
                    if st.button(f"📝 Sửa", key=f"e_{i}"): st.session_state[f"edit_{i}"] = True
                with col_d:
                    if st.button(f"🗑️ Xóa", key=f"d_{i}"): df.drop(i).to_excel(DATA_FILE, index=False); st.rerun()
                
                if st.session_state.get(f"edit_{i}"):
                    with st.form(f"f_edit_{i}"):
                        en = st.text_input("Tên", value=row['Tên Công Ty'])
                        em = st.text_input("MST", value=row['Mã Số Thuế'])
                        eo = st.text_input("Chủ", value=row['Chủ Doanh Nghiệp'])
                        ea = st.text_input("Địa chỉ", value=row['Địa Chỉ'])
                        ep = st.text_input("SĐT", value=row['Liên Hệ'])
                        if st.form_submit_button("Xác nhận Cập nhật"):
                            df.loc[i] = [en, em, eo, ea, ep, f"https://zalo.me{ep}", datetime.now().strftime("%d/%m/%Y %H:%M")]
                            df.to_excel(DATA_FILE, index=False)
                            st.session_state[f"edit_{i}"] = False; st.rerun()
else: st.info("Chưa có dữ liệu.")

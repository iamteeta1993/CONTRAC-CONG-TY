import streamlit as st
import pandas as pd
import os
import requests
import hashlib
from datetime import datetime
import urllib.parse

# --- 1. CẤU HÌNH HỆ THỐNG ---
USER_FILE = "users.xlsx"
DATA_FILE = "data_congty.xlsx"
# Hệ thống chạy chuẩn 7 cột dữ liệu
COLUMNS = ["Tên Công Ty", "Mã Số Thuế", "Chủ Doanh Nghiệp", "Địa Chỉ", "Liên Hệ", "Zalo", "Cập Nhật Cuối"]

ADMIN_USER = "admin" 
ADMIN_PASS = "teeta123"

# --- 2. CÁC HÀM XỬ LÝ DỮ LIỆU ---
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
            # Tự động sửa lỗi nếu file thiếu cột hoặc thừa cột
            for col in COLUMNS:
                if col not in df.columns: df[col] = "Chưa có"
            return df[COLUMNS]
        except:
            return pd.DataFrame(columns=COLUMNS)
    return pd.DataFrame(columns=COLUMNS)

# --- 3. GIAO DIỆN ĐĂNG NHẬP ---
st.set_page_config(page_title="TEETA CODE - QUẢN TRỊ", layout="wide")
if "role" not in st.session_state: st.session_state["role"] = None

if st.session_state["role"] is None:
    st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>TEETA CODE</h1>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🔑 Đăng nhập", "📝 Đăng ký", "🛡️ Quản trị viên"])
    with t3:
        ua = st.text_input("Tài khoản Admin", key="ua")
        pa = st.text_input("Mật khẩu Admin", type="password", key="pa")
        if st.button("Đăng nhập quyền Quản trị", use_container_width=True):
            role = authenticate(ua, pa, "admin")
            if role:
                st.session_state["role"], st.session_state["username"] = role, "CHỦ APP"
                st.rerun()
            else: st.error("Sai thông tin Quản trị viên!")
    with t1:
        u = st.text_input("User", key="u")
        p = st.text_input("Pass", type="password", key="p")
        if st.button("Vào xem dữ liệu"):
            role = authenticate(u, p, "user")
            if role: st.session_state["role"], st.session_state["username"] = role, u; st.rerun()
    st.stop()

# --- 4. GIAO DIỆN CHÍNH (SAU KHI ĐĂNG NHẬP) ---
st.markdown(f"<h1 style='text-align: center; color: #FF4B4B;'>TEETA CODE {'(ADMIN)' if st.session_state['role'] == 'admin' else ''}</h1>", unsafe_allow_html=True)
if st.sidebar.button("Đăng xuất"): st.session_state["role"] = None; st.rerun()

df = load_data()

# SIDEBAR: THÊM MỚI (CHỈ ADMIN)
if st.session_state["role"] == "admin":
    st.sidebar.subheader("➕ Thêm Công Ty")
    search_api = st.sidebar.text_input("🔍 Tra cứu nhanh MST/Tên")
    name_v, mst_v, addr_v = "", "", ""
    if search_api:
        info = get_business_info(search_api)
        if info: name_v, mst_v, addr_v = info.get('name', ''), info.get('id', ''), info.get('address', '')
    
    with st.sidebar.form("add_form", clear_on_submit=True):
        f_name = st.text_input("Tên", value=name_v)
        f_mst = st.text_input("MST", value=mst_v)
        f_owner = st.text_input("Chủ")
        f_addr = st.text_input("Địa chỉ", value=addr_v)
        f_phone = st.text_input("SĐT")
        if st.form_submit_button("Lưu Mới", use_container_width=True):
            now = datetime.now().strftime("%d/%m/%Y %H:%M")
            new_row = pd.DataFrame([[f_name, f_mst, f_owner, f_addr, f_phone, f"https://zalo.me{f_phone}", now]], columns=COLUMNS)
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_excel(DATA_FILE, index=False); st.rerun()

# TRANG CHÍNH: HIỂN THỊ & SỬA ĐỔI
q = st.text_input("🔎 Tìm nhanh trong danh sách của bạn...")
if not df.empty:
    filtered_df = df[df['Tên Công Ty'].astype(str).str.contains(q, case=False, na=False) | df['Mã Số Thuế'].astype(str).str.contains(q, case=False, na=False)] if q else df
    
    for i, row in filtered_df.iterrows():
        with st.expander(f"🏢 {row['Tên Công Ty']} - MST: {row['Mã Số Thuế']}"):
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"📍 **ĐC:** {row['Địa Chỉ']}")
                # Link Google Maps tự động
                clean_addr = urllib.parse.quote(str(row['Địa Chỉ']))
                st.markdown(f"[🌍 Xem vị trí trên Google Maps](https://google.com{clean_addr})")
                st.caption(f"🕒 Cập nhật: {row['Cập Nhật Cuối']}")
            with c2:
                st.write(f"👤 **Chủ:** {row['Chủ Doanh Nghiệp']} | 📞 **SĐT:** {row['Liên Hệ']}")
                st.markdown(f"[💬 Nhắn Zalo]({row['Zalo']})")
            
            # --- CHỨC NĂNG SỬA TRỰC TIẾP CHO QUẢN TRỊ VIÊN ---
            if st.session_state["role"] == "admin":
                col_edit, col_del = st.columns(2)
                with col_edit:
                    if st.button(f"📝 Sửa thông tin", key=f"btn_e_{i}"): st.session_state[f"edit_mode_{i}"] = True
                with col_del:
                    if st.button(f"🗑️ Xóa", key=f"btn_d_{i}"):
                        df = df.drop(i)
                        df.to_excel(DATA_FILE, index=False); st.rerun()
                
                # Form hiện ra khi bấm nút Sửa
                if st.session_state.get(f"edit_mode_{i}"):
                    with st.form(f"form_edit_{i}"):
                        st.write("--- **CHỈNH SỬA TRỰC TIẾP** ---")
                        en = st.text_input("Tên Công Ty", value=row['Tên Công Ty'])
                        em = st.text_input("Mã Số Thuế", value=row['Mã Số Thuế'])
                        eo = st.text_input("Chủ Doanh Nghiệp", value=row['Chủ Doanh Nghiệp'])
                        ea = st.text_input("Địa Chỉ", value=row['Địa Chỉ'])
                        ep = st.text_input("Số Điện Thoại", value=row['Liên Hệ'])
                        
                        if st.form_submit_button("Xác nhận Cập nhật", use_container_width=True):
                            now_time = datetime.now().strftime("%d/%m/%Y %H:%M")
                            # Cập nhật đúng 7 giá trị cho 7 cột để tránh lỗi ValueError
                            df.iloc[i] = [en, em, eo, ea, ep, f"https://zalo.me{ep}", now_time]
                            df.to_excel(DATA_FILE, index=False)
                            st.session_state[f"edit_mode_{i}"] = False
                            st.success("Đã cập nhật dữ liệu mới!")
                            st.rerun()
else:
    st.info("Chưa có dữ liệu. Hãy thêm ở cột bên trái.")

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
st.sidebar

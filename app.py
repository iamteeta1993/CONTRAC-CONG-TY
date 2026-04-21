import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime
import urllib.parse
import re

# --- 1. CẤU HÌNH HỆ THỐNG ---
DATA_FILE = "data_congty.xlsx"
CONTACT_FILE = "contact_canhan.xlsx"
USER_FILE = "users.xlsx"
COLUMNS_CTY = ["Tên Công Ty", "Mã Số Thuế", "Chủ Doanh Nghiệp", "Địa Chỉ", "Liên Hệ", "Ghi Chú", "Zalo", "Cập Nhật Cuối"]
COLUMNS_PERS = ["Tên Liên Hệ", "Công Ty Đang Làm", "Địa Chỉ", "Zalo", "Facebook", "Ghi Chú", "Cập Nhật Cuối"]
ADMIN_USER = "admin" 
ADMIN_PASS = "123"

# --- 2. HÀM HỆ THỐNG ---
def clean_phone(phone): return re.sub(r'\D', '', str(phone))

def load_data(file_path, columns):
    if os.path.exists(file_path):
        try:
            df = pd.read_excel(file_path, dtype=str)
            for col in columns:
                if col not in df.columns: df[col] = ""
            return df[columns]
        except: return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

def hash_pwd(pwd): return hashlib.sha256(str.encode(pwd)).hexdigest()

# --- 3. GIAO DIỆN ĐĂNG NHẬP ---
st.set_page_config(page_title="TEETA CODE - Quản Lý Bảo Mật", layout="wide")
if "role" not in st.session_state: st.session_state["role"] = None

if st.session_state["role"] is None:
    st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>TEETA CODE</h1>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🔑 Thành viên", "🛡️ Admin", "🌐 Khách"])
    with t1:
        u = st.text_input("Username", key="l_u")
        p = st.text_input("Password", type="password", key="l_p")
        if st.button("ĐĂNG NHẬP", use_container_width=True):
            if os.path.exists(USER_FILE):
                users = pd.read_excel(USER_FILE, dtype=str)
                if not users[(users["username"] == u) & (users["password"] == hash_pwd(p))].empty:
                    st.session_state["role"], st.session_state["username"] = "user", u
                    st.rerun()
            st.error("Sai tài khoản hoặc chưa được Admin cấp quyền!")
    with t2:
        ua = st.text_input("Admin User", key="a_u")
        pa = st.text_input("Admin Pass", type="password", key="a_p")
        if st.button("XÁC NHẬN ADMIN", use_container_width=True):
            if ua == ADMIN_USER and pa == ADMIN_PASS:
                st.session_state["role"], st.session_state["username"] = "admin", "QUẢN TRỊ VIÊN"
                st.rerun()
            else: st.error("Sai thông tin Admin!")
    with t3:
        if st.button("VÀO XEM (GUEST)", use_container_width=True):
            st.session_state["role"], st.session_state["username"] = "guest", "Khách"
            st.rerun()
    st.stop()

# --- 4. GIAO DIỆN CHÍNH ---
st.sidebar.subheader(f"👋 {st.session_state['username']}")
if st.sidebar.button("🚪 Đăng xuất"): st.session_state["role"] = None; st.rerun()

# --- MỚI: TÍNH NĂNG TẢI FILE CHO ADMIN ---
if st.session_state["role"] == "admin":
    st.sidebar.divider()
    st.sidebar.subheader("📥 Xuất dữ liệu")
    
    # Tải file Công ty
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "rb") as file:
            st.sidebar.download_button(
                label="📊 Tải file Công Ty",
                data=file,
                file_name=f"Danh_sach_Cong_ty_{datetime.now().strftime('%d%m%Y')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
    # Tải file Liên hệ cá nhân
    if os.path.exists(CONTACT_FILE):
        with open(CONTACT_FILE, "rb") as file:
            st.sidebar.download_button(
                label="👤 Tải file Liên Hệ",
                data=file,
                file_name=f"Danh_ba_Ca_nhan_{datetime.now().strftime('%d%m%Y')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

st.sidebar.divider()
st.sidebar.subheader("🎵 Giải Trí")
with st.sidebar:
    st.components.v1.html('<iframe src="https://www.nhaccuatui.com/mh/background/L6Wv9X7Z2z3n" width="100%" height="150" frameborder="0"></iframe>', height=160)

# PHÂN QUYỀN TABS
if st.session_state["role"] == "admin":
    tab_cty, tab_pers, tab_add = st.tabs(["🏢 Công Ty", "👤 Liên Hệ Cá Nhân", "➕ Quản Lý Hệ Thống"])
else:
    tab_cty, tab_pers = st.tabs(["🏢 Xem Công Ty", "👤 Xem Liên Hệ"])

# (Phần xử lý Tab Công Ty, Liên Hệ Cá Nhân và Quản Lý Hệ Thống giữ nguyên như bản trước)
# ...

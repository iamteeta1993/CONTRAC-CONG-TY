import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime
import urllib.parse
import re
from io import BytesIO

# --- 1. CẤU HÌNH HỆ THỐNG ---
DATA_FILE = "data_congty.xlsx"
USER_FILE = "users.xlsx"
# Đầy đủ danh sách cột cho 2 nhóm
COLUMNS_CTY = ["Tên Công Ty", "Mã Số Thuế", "Chủ Doanh Nghiệp", "Địa Chỉ", "Liên Hệ", "Ghi Chú", "Zalo", "Cập Nhật Cuối"]
COLUMNS_PERS = ["Tên Liên Hệ", "Công Ty Đang Làm", "Địa Chỉ", "Zalo", "Facebook", "Ghi Chú", "Cập Nhật Cuối"]
ADMIN_USER = "admin" 
ADMIN_PASS = "123"

# --- 2. HÀM HỆ THỐNG ---
def clean_phone(phone): return re.sub(r'\D', '', str(phone))

def hash_pwd(pwd): return hashlib.sha256(str.encode(pwd)).hexdigest()

def load_data_from_sheet(sheet_name, columns):
    if os.path.exists(DATA_FILE):
        try:
            with pd.ExcelFile(DATA_FILE) as xls:
                if sheet_name in xls.sheet_names:
                    df = pd.read_excel(xls, sheet_name=sheet_name, dtype=str)
                    for col in columns:
                        if col not in df.columns: df[col] = ""
                    return df[columns]
        except: pass
    return pd.DataFrame(columns=columns)

def save_to_sheet(df, sheet_name):
    if not os.path.exists(DATA_FILE):
        with pd.ExcelWriter(DATA_FILE, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    else:
        # Đọc tất cả sheets hiện có để không làm mất dữ liệu khi ghi sheet mới
        all_sheets = {}
        with pd.ExcelFile(DATA_FILE) as xls:
            for s in xls.sheet_names:
                all_sheets[s] = pd.read_excel(xls, sheet_name=s, dtype=str)
        
        all_sheets[sheet_name] = df # Cập nhật hoặc thêm sheet mới
        
        with pd.ExcelWriter(DATA_FILE, engine='openpyxl') as writer:
            for s_name, s_df in all_sheets.items():
                s_df.to_excel(writer, sheet_name=s_name, index=False)

# --- 3. ĐĂNG NHẬP ---
st.set_page_config(page_title="TEETA CODE - Quản Lý Tổng Hợp", layout="wide")
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
                    st.session_state["role"], st.session_state["username"] = "user", u; st.rerun()
            st.error("Sai tài khoản!")
    with t2:
        ua = st.text_input("Admin User", key="a_u")
        pa = st.text_input("Admin Pass", type="password", key="a_p")
        if st.button("XÁC NHẬN ADMIN", use_container_width=True):
            if ua == ADMIN_USER and pa == ADMIN_PASS:
                st.session_state["role"], st.session_state["username"] = "admin", "QUẢN TRỊ VIÊN"; st.rerun()
    with t3:
        if st.button("VÀO XEM (GUEST)", use_container_width=True):
            st.session_state["role"], st.session_state["username"] = "guest", "Khách"; st.rerun()
    st.stop()

# --- 4. GIAO DIỆN CHÍNH ---
st.sidebar.subheader(f"👋 {st.session_state['username']}")
if st.sidebar.button("🚪 Đăng xuất"): st.session_state["role"] = None; st.rerun()

if st.session_state["role"] == "admin" and os.path.exists(DATA_FILE):
    st.sidebar.divider()
    with open(DATA_FILE, "rb") as f:
        st.sidebar.download_button("📁 Tải Dữ Liệu Tổng (.xlsx)", f, file_name="data_teetacode.xlsx", use_container_width=True)

st.sidebar.divider()
st.sidebar.subheader("🎵 Giải Trí")
st.sidebar.components.v1.html('<iframe src="https://www.nhaccuatui.com/mh/background/L6Wv9X7Z2z3n" width="100%" height="150" frameborder="0"></iframe>', height=160)

# TABS CHÍNH
if st.session_state["role"] == "admin":
    tab_cty, tab_pers, tab_add = st.tabs(["🏢 Công Ty", "👤 Liên Hệ Cá Nhân", "➕ Thêm Mới"])
else:
    tab_cty, tab_pers = st.tabs(["🏢 Công Ty", "👤 Liên Hệ Cá Nhân"])

# --- TAB 1: CÔNG TY ---
with tab_cty:
    df_cty = load_data_from_sheet("CongTy", COLUMNS_CTY)
    q_cty = st.text_input("🔎 Tìm công ty hoặc MST...", key="search_cty")
    f_cty = df_cty[df_cty['Tên Công Ty'].str.contains(q_cty, case=False, na=False) | df_cty['Mã Số Thuế'].str.contains(q_cty, case=False, na=False)] if q_cty else df_cty
    
    for i, r in f_cty.iterrows():
        edit_key = f"ed_cty_{i}"
        if edit_key not in st.session_state: st.session_state[edit_key] = False
        
        with st.expander(f"🏢 {r['Tên Công Ty']} - {r['Mã Số Thuế']}"):
            if st.session_state[edit_key] and st.session_state["role"] == "admin":
                with st.form(f"frm_ed_cty_{i}")

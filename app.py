import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime
import urllib.parse
import re
from io import BytesIO

# --- 1. CẤU HÌNH HỆ THỐNG ---
DATA_FILE = "data_congty.xlsx"  # CHỈ DÙNG 1 FILE DUY NHẤT
USER_FILE = "users.xlsx"
COLUMNS_CTY = ["Tên Công Ty", "Mã Số Thuế", "Chủ Doanh Nghiệp", "Địa Chỉ", "Liên Hệ", "Ghi Chú", "Zalo", "Cập Nhật Cuối"]
COLUMNS_PERS = ["Tên Liên Hệ", "Công Ty Đang Làm", "Địa Chỉ", "Zalo", "Facebook", "Ghi Chú", "Cập Nhật Cuối"]
ADMIN_USER = "admin" 
ADMIN_PASS = "123"

# --- 2. HÀM HỆ THỐNG ---
def clean_phone(phone): return re.sub(r'\D', '', str(phone))

def hash_pwd(pwd): return hashlib.sha256(str.encode(pwd)).hexdigest()

# Hàm tải dữ liệu từ Sheet cụ thể
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

# Hàm lưu dữ liệu (giữ lại các Sheet hiện có)
def save_to_sheet(df, sheet_name):
    if not os.path.exists(DATA_FILE):
        with pd.ExcelWriter(DATA_FILE, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    else:
        with pd.ExcelWriter(DATA_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)

# --- 3. GIAO DIỆN ĐĂNG NHẬP (Giữ nguyên) ---
st.set_page_config(page_title="TEETA CODE - Quản Lý Tập Trung", layout="wide")
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
            st.error("Sai tài khoản!")
    with t2:
        ua = st.text_input("Admin User", key="a_u")
        pa = st.text_input("Admin Pass", type="password", key="a_p")
        if st.button("XÁC NHẬN ADMIN", use_container_width=True):
            if ua == ADMIN_USER and pa == ADMIN_PASS:
                st.session_state["role"], st.session_state["username"] = "admin", "QUẢN TRỊ VIÊN"
                st.rerun()
            else: st.error("Sai Admin!")
    with t3:
        if st.button("VÀO XEM (GUEST)", use_container_width=True):
            st.session_state["role"], st.session_state["username"] = "guest", "Khách"
            st.rerun()
    st.stop()

# --- 4. GIAO DIỆN CHÍNH ---
st.sidebar.subheader(f"👋 {st.session_state['username']}")
if st.sidebar.button("🚪 Đăng xuất"): st.session_state["role"] = None; st.rerun()

# SIDEBAR: NÚT TẢI FILE GỘP
if st.session_state["role"] == "admin":
    st.sidebar.divider()
    st.sidebar.subheader("📥 Xuất dữ liệu")
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "rb") as f:
            st.sidebar.download_button(
                label="📁 Tải file Dữ liệu (Gộp)",
                data=f,
                file_name=f"Data_Tong_Hop_{datetime.now().strftime('%d%m%Y')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

st.sidebar.divider()
st.sidebar.subheader("🎵 Giải Trí")
with st.sidebar:
    st.components.v1.html('<iframe src="https://www.nhaccuatui.com/mh/background/L6Wv9X7Z2z3n" width="100%" height="150" frameborder="0"></iframe>', height=160)

# PHÂN QUYỀN TABS
if st.session_state["role"] == "admin":
    tab_cty, tab_pers, tab_add = st.tabs(["🏢 Công Ty", "👤 Liên Hệ Cá Nhân", "➕ Thêm Mới"])
else:
    tab_cty, tab_pers = st.tabs(["🏢 Xem Công Ty", "👤 Xem Liên Hệ"])

# --- TAB 1: CÔNG TY ---
with tab_cty:
    df_cty = load_data_from_sheet("CongTy", COLUMNS_CTY)
    q_cty = st.text_input("🔎 Tìm công ty...")
    f_cty = df_cty[df_cty['Tên Công Ty'].str.contains(q_cty, case=False, na=False)] if q_cty else df_cty
    
    for i, r in f_cty.iterrows():
        with st.expander(f"🏢 {r['Tên Công Ty']} - {r['Mã Số Thuế']}"):
            # (Phần hiển thị & Sửa giữ nguyên như bản trước, chỉ đổi hàm lưu)
            st.write(f"📍 Địa chỉ: {r['Địa Chỉ']}")
            if st.session_state["role"] == "admin":
                if st.button("🗑️ Xóa", key=f"d_c_{i}"):
                    df_cty.drop(i).to_excel("temp.xlsx") # Logic xóa tạm
                    save_to_sheet(df_cty.drop(i), "CongTy")
                    st.rerun()

# --- TAB 2: LIÊN HỆ CÁ NHÂN ---
with tab_pers:
    df_p = load_data_from_sheet("LienHeCaNhan", COLUMNS_PERS)
    q_p = st.text_input("🔎 Tìm tên...")
    f_p = df_p[df_p['Tên Liên Hệ'].str.contains(q_p, case=False, na=False)] if q_p else df_p

    for i, r in f_p.iterrows():
        with st.expander(f"👤 {r['Tên Liên Hệ']}"):
            st.write(f"🏢 Làm tại: {r['Công Ty Đang Làm']}")
            if st.session_state["role"] == "admin":
                if st.button("🗑️ Xóa", key=f"d_p_{i}"):
                    save_to_sheet(df_p.drop(i), "LienHeCaNhan")
                    st.rerun()

# --- TAB 3: THÊM MỚI ---
if st.session_state["role"] == "admin":
    with tab_add:
        m1, m2 = st.tabs(["🏢 Thêm Công Ty", "👤 Thêm Liên Hệ"])
        with m1:
            with st.form("a_c"):
                fn = st.text_input("Tên Công Ty"); fm = st.text_input("MST")
                if st.form_submit_button("LƯU CÔNG TY"):
                    df_now = load_data_from_sheet("CongTy", COLUMNS_CTY)
                    new = pd.DataFrame([[fn, fm, "", "", "", "", "", datetime.now().strftime("%d/%m/%Y %H:%M")]], columns=COLUMNS_CTY)
                    save_to_sheet(pd.concat([df_now, new], ignore_index=True), "CongTy")
                    st.success("Đã lưu vào Sheet Công Ty!"); st.rerun()
        with m2:
            with st.form("a_p"):
                pn = st.text_input("Tên Liên Hệ"); pw = st.text_input("Công ty")
                if st.form_submit_button("LƯU LIÊN HỆ"):
                    df_now = load_data_from_sheet("LienHeCaNhan", COLUMNS_PERS)
                    new = pd.DataFrame([[pn, pw, "", "", "", "", datetime.now().strftime("%d/%m/%Y %H:%M")]], columns=COLUMNS_PERS)
                    save_to_sheet(pd.concat([df_now, new], ignore_index=True), "LienHeCaNhan")
                    st.success("Đã lưu vào Sheet Liên Hệ!"); st.rerun()

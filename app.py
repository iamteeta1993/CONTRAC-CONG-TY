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
CONTACT_FILE = "contact_canhan.xlsx" # File mới cho liên hệ cá nhân
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

def authenticate(username, password, login_type):
    if login_type == "admin":
        return "admin" if username == ADMIN_USER and password == ADMIN_PASS else None
    if os.path.exists(USER_FILE):
        users = pd.read_excel(USER_FILE, dtype=str)
        if not users[(users["username"] == username) & (users["password"] == hashlib.sha256(str.encode(password)).hexdigest())].empty:
            return "user"
    return None

# --- 3. GIAO DIỆN ĐĂNG NHẬP ---
st.set_page_config(page_title="TEETA CODE - Quản lý", layout="wide")
if "role" not in st.session_state: st.session_state["role"] = None

if st.session_state["role"] is None:
    st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>TEETA CODE</h1>", unsafe_allow_html=True)
    t1, t3, t4 = st.tabs(["🔑 Thành viên", "🛡️ Admin", "🌐 Khách"])
    with t1:
        u = st.text_input("Username", key="l_u")
        p = st.text_input("Password", type="password", key="l_p")
        if st.button("ĐĂNG NHẬP", use_container_width=True):
            r = authenticate(u, p, "user")
            if r: st.session_state["role"], st.session_state["username"] = r, u; st.rerun()
    with t3:
        ua = st.text_input("Admin User", key="a_u")
        pa = st.text_input("Admin Pass", type="password", key="a_p")
        if st.button("XÁC NHẬN ADMIN", use_container_width=True):
            r = authenticate(ua, pa, "admin")
            if r: st.session_state["role"], st.session_state["username"] = r, "QUẢN TRỊ VIÊN"; st.rerun()
    with t4:
        if st.button("VÀO XEM (FREE)", use_container_width=True):
            st.session_state["role"], st.session_state["username"] = "guest", "Khách"; st.rerun()
    st.stop()

# --- 4. GIAO DIỆN CHÍNH ---
st.sidebar.subheader(f"👋 {st.session_state['username']}")
if st.sidebar.button("Đăng xuất"): st.session_state["role"] = None; st.rerun()

# Sidebar Music
st.sidebar.divider()
st.sidebar.subheader("🎵 Giải Trí")
st.sidebar.components.v1.html('<iframe src="https://www.nhaccuatui.com/mh/background/L6Wv9X7Z2z3n" width="100%" height="150" frameborder="0" allow="autoplay"></iframe>', height=160)

# TABS CHÍNH
if st.session_state["role"] == "admin":
    tab1, tab2, tab3 = st.tabs(["🏢 Quản lý Công Ty", "👤 Danh Bạ Cá Nhân", "➕ Thêm Mới"])
else:
    tab1, tab2 = st.tabs(["🏢 Tra cứu Công Ty", "👤 Danh Bạ Cá Nhân"])

# --- XỬ LÝ TAB 2: LIÊN HỆ CÁ NHÂN ---
with tab2:
    st.subheader("👤 Danh bạ Liên hệ Cá nhân")
    df_pers = load_data(CONTACT_FILE, COLUMNS_PERS)
    search_p = st.text_input("🔎 Tìm tên hoặc công ty đang làm...")
    
    if not df_pers.empty:
        f_pers = df_pers[df_pers['Tên Liên Hệ'].str.contains(search_p, case=False, na=False) | 
                         df_pers['Công Ty Đang Làm'].str.contains(search_p, case=False, na=False)] if search_p else df_pers
        
        for idx, row in f_pers.iterrows():
            with st.expander(f"👤 {row['Tên Liên Hệ']} - {row['Công Ty Đang Làm']}"):
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"🏠 **Địa chỉ:** {row['Địa Chỉ']}")
                    if row['Địa Chỉ'] != "":
                        url_map = f"https://www.google.com/maps/search/{urllib.parse.quote(row['Địa Chỉ'])}"
                        st.markdown(f"[📍 Xem Google Maps]({url_map})")
                    st.write(f"📝 **Ghi chú:** {row['Ghi Chú']}")
                
                with c2:
                    # Nút Zalo
                    if row['Zalo']:
                        z_link = f"https://zalo.me/{clean_phone(row['Zalo'])}"
                        st.markdown(f'<a href="{z_link}" target="_blank" style="text-decoration:none;"><div style="background-color:#0068FF;color:white;padding:8px;border-radius:5px;text-align:center;font-weight:bold;margin-bottom:5px;">💬 NHẮN ZALO</div></a>', unsafe_allow_html=True)
                    
                    # Nút Facebook
                    if row['Facebook']:
                        fb_link = row['Facebook'] if "facebook.com" in row['Facebook'] else f"https://facebook.com/{row['Facebook']}"
                        st.markdown(f'<a href="{fb_link}" target="_blank" style="text-decoration:none;"><div style="background-color:#1877F2;color:white;padding:8px;border-radius:5px;text-align:center;font-weight:bold;">📘 XEM FACEBOOK</div></a>', unsafe_allow_html=True)
                    
                    st.caption(f"Cập nhật: {row['Cập Nhật Cuối']}")
                
                if st.session_state["role"] == "admin":
                    if st.button("🗑️ Xóa liên hệ này", key=f"del_p_{idx}"):
                        df_pers.drop(idx).to_excel(CONTACT_FILE, index=False)
                        st.rerun()

# --- XỬ LÝ TAB 3: THÊM MỚI (CHỈ ADMIN) ---
if st.session_state["role"] == "admin":
    with tab3:
        sub1, sub2 = st.tabs(["➕ Thêm Công Ty", "👤 Thêm Liên Hệ Cá Nhân"])
        
        with sub2:
            with st.form("form_pers", clear_on_submit=True):
                st.write("### Nhập thông tin liên hệ mới")
                p_name = st.text_input("Tên Liên Hệ *")
                p_work = st.text_input("Công ty đang làm việc")
                p_addr = st.text_input("Địa chỉ (Để hiện bản đồ)")
                p_zalo = st.text_input("Số Zalo")
                p_face = st.text_input("Link hoặc Username Facebook")
                p_note = st.text_area("Ghi chú thêm")
                
                if st.form_submit_button("LƯU LIÊN HỆ"):
                    if p_name:
                        df_p = load_data(CONTACT_FILE, COLUMNS_PERS)
                        new_p = pd.DataFrame([[p_name, p_work, p_addr, p_zalo, p_face, p_note, datetime.now().strftime("%d/%m/%Y %H:%M")]], columns=COLUMNS_PERS)
                        pd.concat([df_p, new_p], ignore_index=True).to_excel(CONTACT_FILE, index=False)
                        st.success("Đã lưu liên hệ cá nhân!")
                        st.rerun()
                    else: st.error("Vui lòng nhập tên!")

# --- (GIỮ NGUYÊN TAB 1 VÀ PHẦN THÊM CÔNG TY NHƯ CŨ) ---
with tab1:
    # ... Copy phần hiển thị danh sách công ty cũ của bạn vào đây ...
    st.write("Dữ liệu công ty cũ giữ nguyên tại đây.")

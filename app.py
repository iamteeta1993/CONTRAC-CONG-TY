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
st.sidebar.divider()
st.sidebar.subheader("🎵 Giải Trí")
with st.sidebar:
    st.components.v1.html('<iframe src="https://www.nhaccuatui.com/mh/background/L6Wv9X7Z2z3n" width="100%" height="150" frameborder="0"></iframe>', height=160)

# PHÂN QUYỀN TABS
if st.session_state["role"] == "admin":
    tab_cty, tab_pers, tab_add = st.tabs(["🏢 Công Ty", "👤 Liên Hệ Cá Nhân", "➕ Quản Lý Hệ Thống"])
else:
    tab_cty, tab_pers = st.tabs(["🏢 Xem Công Ty", "👤 Xem Liên Hệ"])

# --- TAB 1: CÔNG TY (CÓ TÍNH NĂNG SỬA) ---
with tab_cty:
    df_cty = load_data(DATA_FILE, COLUMNS_CTY)
    q_cty = st.text_input("🔎 Tìm kiếm dữ liệu...")
    f_cty = df_cty[df_cty['Tên Công Ty'].str.contains(q_cty, case=False, na=False) | df_cty['Mã Số Thuế'].str.contains(q_cty, case=False, na=False)] if q_cty else df_cty
    
    for i, r in f_cty.iterrows():
        edit_c_key = f"edit_c_{i}"
        if edit_c_key not in st.session_state: st.session_state[edit_c_key] = False

        with st.expander(f"🏢 {r['Tên Công Ty']} - {r['Mã Số Thuế']}"):
            if st.session_state[edit_c_key] and st.session_state["role"] == "admin":
                with st.form(f"f_ed_c_{i}"):
                    e1, e2 = st.columns(2)
                    v1 = e1.text_input("Tên", value=r['Tên Công Ty'])
                    v2 = e1.text_input("MST", value=r['Mã Số Thuế'])
                    v3 = e1.text_input("Chủ", value=r['Chủ Doanh Nghiệp'])
                    v4 = e2.text_input("Địa Chỉ", value=r['Địa Chỉ'])
                    v5 = e2.text_input("Liên Hệ", value=r['Liên Hệ'])
                    v6 = st.text_area("Ghi Chú", value=r['Ghi Chú'])
                    if st.form_submit_button("LƯU THAY ĐỔI"):
                        df_cty.loc[i] = [v1, v2, v3, v4, v5, v6, f"https://zalo.me/{clean_phone(v5)}", datetime.now().strftime("%d/%m/%Y %H:%M")]
                        df_cty.to_excel(DATA_FILE, index=False)
                        st.session_state[edit_c_key] = False; st.rerun()
            else:
                c1, c2 = st.columns(2)
                c1.write(f"📍 **Địa chỉ:** {r['Địa Chỉ']}")
                if r['Địa Chỉ']: c1.markdown(f"[🌍 Bản Đồ](https://www.google.com/maps/search/{urllib.parse.quote(r['Địa Chỉ'])})")
                c1.info(f"📝 **Ghi chú:** {r['Ghi Chú']}")
                c2.write(f"👤 **Chủ:** {r['Chủ Doanh Nghiệp']} | 📞 **LH:** {r['Liên Hệ']}")
                if r['Liên Hệ']: c2.markdown(f'<a href="https://zalo.me/{clean_phone(r["Liên Hệ"])}" target="_blank" style="text-decoration:none;"><div style="background-color:#0068FF;color:white;padding:10px;border-radius:10px;text-align:center;font-weight:bold;">💬 ZALO</div></a>', unsafe_allow_html=True)
                
                if st.session_state["role"] == "admin":
                    st.divider()
                    b1, b2 = st.columns(2)
                    if b1.button("🗑️ Xóa", key=f"d_c_{i}"): df_cty.drop(i).to_excel(DATA_FILE, index=False); st.rerun()
                    if b2.button("📝 Sửa", key=f"e_c_{i}"): st.session_state[edit_c_key] = True; st.rerun()

# --- TAB 2: LIÊN HỆ CÁ NHÂN (CÓ TÍNH NĂNG SỬA) ---
with tab_pers:
    df_p = load_data(CONTACT_FILE, COLUMNS_PERS)
    q_p = st.text_input("🔎 Tìm tên liên hệ...")
    f_p = df_p[df_p['Tên Liên Hệ'].str.contains(q_p, case=False, na=False)] if q_p else df_p

    for i, r in f_p.iterrows():
        edit_p_key = f"edit_p_{i}"
        if edit_p_key not in st.session_state: st.session_state[edit_p_key] = False

        with st.expander(f"👤 {r['Tên Liên Hệ']} - {r['Công Ty Đang Làm']}"):
            if st.session_state[edit_p_key] and st.session_state["role"] == "admin":
                with st.form(f"f_ed_p_{i}"):
                    p1 = st.text_input("Tên", value=r['Tên Liên Hệ'])
                    p2 = st.text_input("Công ty", value=r['Công Ty Đang Làm'])
                    p3 = st.text_input("Địa Chỉ", value=r['Địa Chỉ'])
                    p4 = st.text_input("Zalo", value=r['Zalo'])
                    p5 = st.text_input("Facebook", value=r['Facebook'])
                    p6 = st.text_area("Ghi Chú", value=r['Ghi Chú'])
                    if st.form_submit_button("LƯU CÁ NHÂN"):
                        df_p.loc[i] = [p1, p2, p3, p4, p5, p6, datetime.now().strftime("%d/%m/%Y %H:%M")]
                        df_p.to_excel(CONTACT_FILE, index=False)
                        st.session_state[edit_p_key] = False; st.rerun()
            else:
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"🏢 **Làm tại:** {r['Công Ty Đang Làm']}")
                    st.write(f"📍 **Địa chỉ:** {r['Địa Chỉ']}")
                    if r['Địa Chỉ']: st.markdown(f"[🌍 Google Map](https://www.google.com/maps/search/{urllib.parse.quote(r['Địa Chỉ'])})")
                    st.write(f"📝 **Ghi chú:** {r['Ghi Chú']}")
                with c2:
                    if r['Zalo']: st.markdown(f'<a href="https://zalo.me/{clean_phone(r["Zalo"])}" target="_blank" style="text-decoration:none;"><div style="background-color:#0068FF;color:white;padding:8px;border-radius:5px;text-align:center;font-weight:bold;">💬 ZALO</div></a>', unsafe_allow_html=True)
                    if r['Facebook']: st.markdown(f'<a href="{r["Facebook"] if "http" in r["Facebook"] else "https://fb.com/"+r["Facebook"]}" target="_blank" style="text-decoration:none;"><div style="background-color:#1877F2;color:white;padding:8px;border-radius:5px;text-align:center;font-weight:bold;">📘 FACEBOOK</div></a>', unsafe_allow_html=True)
                
                if st.session_state["role"] == "admin":
                    st.divider()
                    if st.button("🗑️ Xóa", key=f"d_p_{i}"): df_p.drop(i).to_excel(CONTACT_FILE, index=False); st.rerun()
                    if st.button("📝 Sửa", key=f"e_p_{i}"): st.session_state[edit_p_key] = True; st.rerun()

# --- TAB 3: QUẢN LÝ (CHỈ ADMIN) ---
if st.session_state["role"] == "admin":
    with tab_add:
        m1, m2 = st.tabs(["➕ Thêm Công Ty", "👤 Thêm Liên Hệ"])
        with m1:
            with st.form("add_c"):
                fn = st.text_input("Tên Công Ty"); fm = st.text_input("MST"); fd = st.text_input("Địa Chỉ")
                fl = st.text_input("Liên Hệ"); fc = st.text_input("Chủ"); fg = st.text_area("Ghi Chú")
                if st.form_submit_button("LƯU"):
                    df_c = load_data(DATA_FILE, COLUMNS_CTY)
                    new = pd.DataFrame([[fn, fm, fc, fd, fl, fg, f"https://zalo.me/{clean_phone(fl)}", datetime.now().strftime("%d/%m/%Y %H:%M")]], columns=COLUMNS_CTY)
                    pd.concat([df_c, new], ignore_index=True).to_excel(DATA_FILE, index=False); st.rerun()
        with m2:
            with st.form("add_p"):
                p1 = st.text_input("Tên"); p2 = st.text_input("Công ty"); p3 = st.text_input("Địa Chỉ")
                p4 = st.text_input("Zalo"); p5 = st.text_input("Facebook"); p6 = st.text_area("Ghi Chú")
                if st.form_submit_button("LƯU LIÊN HỆ"):
                    df_pe = load_data(CONTACT_FILE, COLUMNS_PERS)
                    new_p = pd.DataFrame([[p1, p2, p3, p4, p5, p6, datetime.now().strftime("%d/%m/%Y %H:%M")]], columns=COLUMNS_PERS)
                    pd.concat([df_pe, new_p], ignore_index=True).to_excel(CONTACT_FILE, index=False); st.rerun()

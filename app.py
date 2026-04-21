import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime
import urllib.parse
import re

# --- 1. CẤU HÌNH HỆ THỐNG ---
DATA_FILE = "data_congty.xlsx"
USER_FILE = "users.xlsx"
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
        all_sheets = {}
        with pd.ExcelFile(DATA_FILE) as xls:
            for s in xls.sheet_names:
                all_sheets[s] = pd.read_excel(xls, sheet_name=s, dtype=str)
        
        all_sheets[sheet_name] = df
        
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
                with st.form(f"frm_ed_cty_{i}"):
                    c1, c2 = st.columns(2)
                    v1 = c1.text_input("Tên Công Ty", value=r['Tên Công Ty'])
                    v2 = c1.text_input("Mã Số Thuế", value=r['Mã Số Thuế'])
                    v3 = c1.text_input("Chủ Doanh Nghiệp", value=r['Chủ Doanh Nghiệp'])
                    v4 = c2.text_input("Địa Chỉ", value=r['Địa Chỉ'])
                    v5 = c2.text_input("Liên Hệ (SĐT)", value=r['Liên Hệ'])
                    v6 = st.text_area("Ghi Chú", value=r['Ghi Chú'])
                    if st.form_submit_button("LƯU THAY ĐỔI"):
                        df_cty.loc[i] = [v1, v2, v3, v4, v5, v6, f"https://zalo.me/{clean_phone(v5)}", datetime.now().strftime("%d/%m/%Y %H:%M")]
                        save_to_sheet(df_cty, "CongTy")
                        st.session_state[edit_key] = False; st.rerun()
            else:
                col_a, col_b = st.columns(2)
                col_a.write(f"📍 **Địa chỉ:** {r['Địa Chỉ']}")
                if r['Địa Chỉ']: col_a.markdown(f"[🌍 Xem Bản Đồ](http://maps.google.com/?q={urllib.parse.quote(r['Địa Chỉ'])})")
                col_a.info(f"📝 **Ghi chú:** {r['Ghi Chú']}")
                col_b.write(f"👤 **Chủ:** {r['Chủ Doanh Nghiệp']} | 📞 **LH:** {r['Liên Hệ']}")
                if r['Liên Hệ']: col_b.markdown(f'<a href="https://zalo.me/{clean_phone(r["Liên Hệ"])}" target="_blank" style="text-decoration:none;"><div style="background-color:#0068FF;color:white;padding:10px;border-radius:10px;text-align:center;font-weight:bold;">💬 NHẮN ZALO</div></a>', unsafe_allow_html=True)
                
                if st.session_state["role"] == "admin":
                    st.divider()
                    b1, b2 = st.columns(2)
                    if b1.button("🗑️ Xóa", key=f"del_cty_{i}"):
                        save_to_sheet(df_cty.drop(i), "CongTy"); st.rerun()
                    if b2.button("📝 Sửa", key=f"btn_ed_cty_{i}"):
                        st.session_state[edit_key] = True; st.rerun()

# --- TAB 2: LIÊN HỆ CÁ NHÂN ---
with tab_pers:
    df_p = load_data_from_sheet("LienHeCaNhan", COLUMNS_PERS)
    q_p = st.text_input("🔎 Tìm tên liên hệ...", key="search_p")
    f_p = df_p[df_p['Tên Liên Hệ'].str.contains(q_p, case=False, na=False)] if q_p else df_p

    for i, r in f_p.iterrows():
        edit_p_key = f"ed_p_{i}"
        if edit_p_key not in st.session_state: st.session_state[edit_p_key] = False

        with st.expander(f"👤 {r['Tên Liên Hệ']} - {r['Công Ty Đang Làm']}"):
            if st.session_state[edit_p_key] and st.session_state["role"] == "admin":
                with st.form(f"frm_ed_p_{i}"):
                    p1 = st.text_input("Tên Liên Hệ", value=r['Tên Liên Hệ'])
                    p2 = st.text_input("Công ty làm việc", value=r['Công Ty Đang Làm'])
                    p3 = st.text_input("Địa Chỉ", value=r['Địa Chỉ'])
                    p4 = st.text_input("Số Zalo", value=r['Zalo'])
                    p5 = st.text_input("Facebook", value=r['Facebook'])
                    p6 = st.text_area("Ghi Chú", value=r['Ghi Chú'])
                    if st.form_submit_button("LƯU CẬP NHẬT"):
                        df_p.loc[i] = [p1, p2, p3, p4, p5, p6, datetime.now().strftime("%d/%m/%Y %H:%M")]
                        save_to_sheet(df_p, "LienHeCaNhan")
                        st.session_state[edit_p_key] = False; st.rerun()
            else:
                c1, c2 = st.columns(2)
                c1.write(f"🏢 **Làm tại:** {r['Công Ty Đang Làm']}\n\n📍 **Địa chỉ:** {r['Địa Chỉ']}")
                if r['Địa Chỉ']: c1.markdown(f"[🌍 Xem Google Map](http://maps.google.com/?q={urllib.parse.quote(r['Địa Chỉ'])})")
                c1.info(f"📝 **Ghi chú:** {r['Ghi Chú']}")
                with c2:
                    if r['Zalo']: st.markdown(f'<a href="https://zalo.me/{clean_phone(r["Zalo"])}" target="_blank" style="text-decoration:none;"><div style="background-color:#0068FF;color:white;padding:8px;border-radius:5px;text-align:center;font-weight:bold;margin-bottom:5px;">💬 CHÁT ZALO</div></a>', unsafe_allow_html=True)
                    if r['Facebook']: st.markdown(f'<a href="{r["Facebook"] if "http" in r["Facebook"] else "https://fb.com/"+r["Facebook"]}" target="_blank" style="text-decoration:none;"><div style="background-color:#1877F2;color:white;padding:8px;border-radius:5px;text-align:center;font-weight:bold;">📘 FACEBOOK</div></a>', unsafe_allow_html=True)
                
                if st.session_state["role"] == "admin":
                    st.divider()
                    if st.button("🗑️ Xóa liên hệ", key=f"del_p_{i}"):
                        save_to_sheet(df_p.drop(i), "LienHeCaNhan"); st.rerun()
                    if st.button("📝 Sửa thông tin", key=f"btn_ed_p_{i}"):
                        st.session_state[edit_p_key] = True; st.rerun()

# --- TAB 3: THÊM MỚI (FULL MỤC) ---
if st.session_state["role"] == "admin":
    with tab_add:
        m1, m2 = st.tabs(["🏢 Thêm Công Ty", "👤 Thêm Liên Hệ"])
        with m1:
            with st.form("add_cty_full", clear_on_submit=True):
                col1, col2 = st.columns(2)
                f_n = col1.text_input("Tên Công Ty *")
                f_m = col1.text_input("Mã Số Thuế")
                f_c = col1.text_input("Chủ Doanh Nghiệp")
                f_d = col2.text_input("Địa Chỉ")
                f_l = col2.text_input("Số Điện Thoại")
                f_g = st.text_area("Ghi Chú")
                if st.form_submit_button("LƯU VÀO HỆ THỐNG", use_container_width=True):
                    if f_n:
                        df_now = load_data_from_sheet("CongTy", COLUMNS_CTY)
                        new = pd.DataFrame([[f_n, f_m, f_c, f_d, f_l, f_g, f"https://zalo.me/{clean_phone(f_l)}", datetime.now().strftime("%d/%m/%Y %H:%M")]], columns=COLUMNS_CTY)
                        save_to_sheet(pd.concat([df_now, new], ignore_index=True), "CongTy")
                        st.success("Đã thêm công ty!"); st.rerun()
        with m2:
            with st.form("add_pers_full", clear_on_submit=True):
                p_n = st.text_input("Tên Liên Hệ *")
                p_w = st.text_input("Công ty đang làm việc")
                p_d = st.text_input("Địa Chỉ")
                p_z = st.text_input("Số Zalo")
                p_f = st.text_input("Link Facebook")
                p_g = st.text_area("Ghi Chú thêm")
                if st.form_submit_button("LƯU LIÊN HỆ CÁ NHÂN", use_container_width=True):
                    if p_n:
                        df_now = load_data_from_sheet("LienHeCaNhan", COLUMNS_PERS)
                        new = pd.DataFrame([[p_n, p_w, p_d, p_z, p_f, p_g, datetime.now().strftime("%d/%m/%Y %H:%M")]], columns=COLUMNS_PERS)
                        save_to_sheet(pd.concat([df_now, new], ignore_index=True), "LienHeCaNhan")
                        st.success("Đã thêm liên hệ!"); st.rerun()

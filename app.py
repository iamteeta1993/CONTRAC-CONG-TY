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
ADMIN_PASS = "123" # Nên đổi khi đưa lên thực tế

# --- 2. HÀM HỖ TRỢ ---
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

def get_business_info(mst):
    """Gọi API lấy thông tin doanh nghiệp tự động"""
    try:
        # Sử dụng API mở của VietQR hoặc các đơn vị tương đương
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

# --- 3. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Hệ Thống Khuôn Mẫu Miền Nam", layout="wide", page_icon="🏗️")

if "role" not in st.session_state: 
    st.session_state["role"] = None

# GIAO DIỆN ĐĂNG NHẬP
if st.session_state["role"] is None:
    st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>TEETA CODE - DATABASE</h1>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🔑 Thành viên", "🛡️ Quản trị", "🌐 Khách"])
    
    with t1:
        u = st.text_input("Tên đăng nhập", key="user_u")
        p = st.text_input("Mật khẩu", type="password", key="user_p")
        if st.button("VÀO HỆ THỐNG"):
            r = authenticate(u, p, "user")
            if r: 
                st.session_state["role"], st.session_state["username"] = r, u
                st.rerun()
            else: st.error("Thông tin không chính xác!")
            
    with t2:
        ua = st.text_input("Admin ID", key="admin_u")
        pa = st.text_input("Admin Key", type="password", key="admin_p")
        if st.button("XÁC NHẬN QUYỀN ADMIN"):
            r = authenticate(ua, pa, "admin")
            if r: 
                st.session_state["role"], st.session_state["username"] = r, "ADMIN"
                st.rerun()
                
    with t3:
        st.info("Chế độ xem tự do (Bị hạn chế thông tin nội bộ)")
        if st.button("XEM DANH SÁCH FREE"):
            st.session_state["role"], st.session_state["username"] = "guest", "Khách"
            st.rerun()
    st.stop()

# --- 4. TRANG CHÍNH ---
st.title("🏗️ DỮ LIỆU CÔNG TY KHUÔN MẪU MIỀN NAM")
st.sidebar.markdown(f"### Chào, **{st.session_state['username']}**")
if st.sidebar.button("Đăng xuất"):
    st.session_state["role"] = None
    st.rerun()

df = load_data()

# SIDEBAR: CÔNG CỤ ADMIN
if st.session_state["role"] == "admin":
    st.sidebar.divider()
    st.sidebar.subheader("➕ Thêm mới công ty")
    search_mst = st.sidebar.text_input("Nhập MST để lấy thông tin nhanh")
    
    name_init, addr_init = "", ""
    if search_mst:
        info = get_business_info(search_mst)
        if info:
            name_init, addr_init = info.get('name', ''), info.get('address', '')
            st.sidebar.success("Đã tìm thấy thông tin!")

    with st.sidebar.form("add_company_form"):
        f_name = st.text_input("Tên Công Ty", value=name_init)
        f_mst = st.text_input("Mã Số Thuế", value=search_mst)
        f_addr = st.text_input("Địa Chỉ", value=addr_init)
        f_phone = st.text_input("Số Điện Thoại")
        f_note = st.text_area("Ghi chú (Năng lực sản xuất...)")
        
        if st.form_submit_button("LƯU VÀO DATABASE"):
            now = datetime.now().strftime("%d/%m/%Y %H:%M")
            zalo_url = f"https://zalo.me/{clean_phone(f_phone)}"
            new_data = pd.DataFrame([[f_name, f_mst, "", f_addr, f_phone, f_note, zalo_url, now]], columns=COLUMNS)
            df = pd.concat([df, new_data], ignore_index=True)
            df.to_excel(DATA_FILE, index=False)
            st.sidebar.success("Đã thêm thành công!")
            st.rerun()

# KHU VỰC TRA CỨU
search_q = st.text_input("🔎 Tìm kiếm theo Tên công ty, MST hoặc Địa chỉ...", placeholder="Ví dụ: Khuôn mẫu, Bình Dương, 0314...")

if not df.empty:
    # Lọc dữ liệu thông minh
    mask = df.apply(lambda row: row.astype(str).str.contains(search_q, case=False).any(), axis=1)
    filtered_df = df[mask] if search_q else df

    st.write(f"Tìm thấy **{len(filtered_df)}** kết quả.")

    for i, row in filtered_df.iterrows():
        with st.expander(f"🏢 **{row['Tên Công Ty']}** - MST: {row['Mã Số Thuế']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**📍 Địa chỉ:** {row['Địa Chỉ']}")
                # Tạo link Google Maps chuẩn
                maps_link = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(str(row['Địa Chỉ']))}"
                st.markdown(f"🔗 [Xem trên Google Maps]({maps_link})")
                
                if st.session_state["role"] in ["admin", "user"]:
                    st.info(f"📝 **Ghi chú nội bộ:** {row['Ghi Chú']}")
                else:
                    st.warning("🔒 Đăng nhập để xem ghi chú năng lực.")
            
            with col2:
                phone_display = row['Liên Hệ'] if row['Liên Hệ'] else "Chưa cập nhật"
                st.markdown(f"**📞 Liên hệ:** {phone_display}")
                if row['Liên Hệ']:
                    st.markdown(f"""
                        <a href="{row['Zalo']}" target="_blank" style="text-decoration:none;">
                            <div style="background-color:#0068FF;color:white;padding:8px;border-radius:5px;text-align:center;font-weight:bold;">
                                💬 NHẮN ZALO
                            </div>
                        </a>
                    """, unsafe_allow_html=True)
            
            if st.session_state["role"] == "admin":
                if st.button(f"🗑️ Xóa công ty", key=f"del_{i}"):
                    df = df.drop(i)
                    df.to_excel(DATA_FILE, index=False)
                    st.rerun()
else:
    st.info("Chưa có dữ liệu. Vui lòng dùng tài quyền Admin để thêm mới.")

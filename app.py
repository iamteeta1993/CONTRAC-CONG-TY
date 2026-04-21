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

# --- 3. CẤU HÌNH TRANG & ĐĂNG NHẬP ---
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

# --- 4. GIAO DIỆN CHÍNH (SAU KHI ĐĂNG NHẬP) ---
st.markdown("""
<style>
    [data-testid="stExpander"] { border-radius: 10px; border: 1px solid #444; margin-bottom: 15px; }
    .stButton > button { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<div style='text-align: center; margin-top: -60px;'> <h1 style='color: #FF4B4B; font-family: Arial Black;'>TEETA <span style='color: #31333F;'>CODE</span></h1> </div>", unsafe_allow_html=True)

df = load_data()

# --- SIDEBAR ---
st.sidebar.subheader(f"👋 {st.session_state['username']}")
st.sidebar.write(f"Quyền hạn: **{st.session_state['role'].upper()}**")

c_sb1, c_sb2 = st.sidebar.columns(2)
with c_sb1:
    if st.button("🚪 Đăng xuất", use_container_width=True): 
        st.session_state["role"] = None
        st.rerun()
with c_sb2:
    if st.session_state["role"] == "admin" and os.path.exists(DATA_FILE):
        with open(DATA_FILE, "rb") as f:
            st.sidebar.download_button("📥 Xuất Excel", f, file_name="data_teetacode.xlsx", use_container_width=True)

st.sidebar.divider()
st.sidebar.subheader("🎵 Giải Trí")
tab_nct, tab_music, tab_video = st.sidebar.tabs(["NCT", "Spotify", "YouTube"])

with tab_nct:
    nct_url = "https://www.nhaccuatui.com/mh/background/L6Wv9X7Z2z3n"
    st.components.v1.html(f'<iframe src="{nct_url}" width="100%" height="150" frameborder="0" allowfullscreen allow="autoplay"></iframe>', height=160)
with tab_music:
    spotify_url = "https://open.spotify.com/embed/playlist/37i9dQZF1DWZeKHA6V9v9u" 
    st.components.v1.html(f'<iframe src="{spotify_url}" width="100%" height="152" frameBorder="0" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"></iframe>', height=160)
with tab_video:
    yt_id = "jfKfPfyJRdk" 
    st.components.v1.html(f'<iframe width="100%" height="152" src="https://www.youtube.com/embed/{yt_id}" frameborder="0" allowfullscreen></iframe>', height=160)

# --- NỘI DUNG CHÍNH (TABS) ---
if st.session_state["role"] == "admin":
    tabs_main = st.tabs(["🔍 Tra cứu & Quản lý", "➕ Thêm Công Ty Mới"])
else:
    tabs_main = st.tabs(["🔍 Tra cứu dữ liệu"])

# --- TAB 1: TRA CỨU & HIỂN THỊ ---
with tabs_main[0]:
    q = st.text_input("🔎 Tìm kiếm nhanh", placeholder="Nhập Tên Công Ty hoặc Mã Số Thuế...")

    if not df.empty:
        f_df = df[df['Tên Công Ty'].str.contains(q, case=False, na=False) | 
                  df['Mã Số Thuế'].str.contains(q, case=False, na=False)] if q else df
        
        st.write(f"Tìm thấy **{len(f_df)}** kết quả.")

        for i, row in f_df.iterrows():
            with st.expander(f"🏢 {row['Tên Công Ty']} - MST: {row['Mã Số Thuế']}"):
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**📍 Địa chỉ:** {row['Địa Chỉ']}")
                    maps_q = urllib.parse.quote(str(row['Địa Chỉ']))
                    st.markdown(f"🌍 [Xem bản đồ](https://www.google.com/maps/search/?api=1&query={maps_q})")
                    if st.session_state["role"] in ["admin", "user"]:
                        st.info(f"📝 **Ghi chú:** {row['Ghi Chú']}")
                
                with c2:
                    st.write(f"**👨‍💼 Chủ doanh nghiệp:** {row['Chủ Doanh Nghiệp']}")
                    st.write(f"**📞 Liên hệ:** {row['Liên Hệ']}")
                    if row['Liên Hệ']:
                        z_link = f"https://zalo.me/{clean_phone(row['Liên Hệ'])}"
                        st.markdown(f"""<a href="{z_link}" target="_blank" style="text-decoration:none;"><div style="background-color:#0068FF;color:white;padding:10px;border-radius:10px;text-align:center;font-weight:bold;">💬 NHẮN ZALO</div></a>""", unsafe_allow_html=True)
                    st.caption(f"Cập nhật: {row['Cập Nhật Cuối']}")

                if st.session_state["role"] == "admin":
                    st.divider()
                    col_del, col_edit = st.columns(2)
                    with col_del:
                        if st.button("🗑️ Xóa", key=f"del_{i}", use_container_width=True):
                            df = df.drop(i)
                            df.to_excel(DATA_FILE, index=False)
                            st.rerun()
                    with col_edit:
                        st.info("Tính năng Sửa đang cập nhật...")

# --- TAB 2: THÊM MỚI (CHỈ ADMIN) ---
if st.session_state["role"] == "admin":
    with tabs_main[1]:
        st.subheader("➕ Thêm Công Ty Mới")
        search_mst = st.text_input("🔍 Tra MST nhanh", placeholder="Nhập MST để lấy thông tin tự động...")
        n_v, a_v = "", ""
        
        if search_mst:
            info = get_business_info(search_mst)
            if info: 
                n_v, a_v = info.get('name', ''), info.get('address', '')
                st.success("Đã tìm thấy dữ liệu!")
            else: st.warning("Không tìm thấy MST này.")
                
        with st.form("add_form", clear_on_submit=True):
            f1, f2 = st.columns(2)
            with f1:
                fn = st.text_input("Tên Công Ty", value=n_v)
                fm = st.text_input("Mã Số Thuế", value=search_mst)
                fo = st.text_input("Chủ Doanh Nghiệp")
            with f2:
                fa = st.text_input("Địa chỉ", value=a_v)
                fp = st.text_input("Số điện thoại")
            fg = st.text_area("Ghi chú")
            
            if st.form_submit_button("LƯU VÀO HỆ THỐNG", use_container_width=True):
                if fn and fm:
                    df_curr = load_data()
                    now = datetime.now().strftime("%d/%m/%Y %H:%M")
                    new_row = pd.DataFrame([[fn, fm, fo, fa, fp, fg, f"https://zalo.me/{clean_phone(fp)}", now]], columns=COLUMNS)
                    pd.concat([df_curr, new_row], ignore_index=True).to_excel(DATA_FILE, index=False)
                    st.success("Đã thêm thành công!")
                    st.rerun()
                else: st.error("Vui lòng điền Tên và MST!")
# --- TAB 1: TRA CỨU & HIỂN THỊ (CÓ TÍNH NĂNG SỬA & LƯU) ---
with tabs_main[0]:
    q = st.text_input("🔎 Tìm kiếm nhanh", placeholder="Nhập Tên Công Ty hoặc Mã Số Thuế...")

    if not df.empty:
        # Lọc dữ liệu theo tìm kiếm
        f_df = df[df['Tên Công Ty'].str.contains(q, case=False, na=False) | 
                  df['Mã Số Thuế'].str.contains(q, case=False, na=False)] if q else df
        
        st.write(f"Tìm thấy **{len(f_df)}** kết quả.")

        for i, row in f_df.iterrows():
            # Tạo key trạng thái riêng cho từng dòng để quản lý việc mở form sửa
            edit_mode_key = f"edit_mode_{i}"
            if edit_mode_key not in st.session_state:
                st.session_state[edit_mode_key] = False

            with st.expander(f"🏢 {row['Tên Công Ty']} - MST: {row['Mã Số Thuế']}"):
                
                # --- CHẾ ĐỘ CHỈNH SỬA (DÀNH CHO ADMIN) ---
                if st.session_state[edit_mode_key] and st.session_state["role"] == "admin":
                    st.markdown("### 📝 Hiệu chỉnh thông tin")
                    with st.form(key=f"form_edit_{i}"):
                        c_edit1, c_edit2 = st.columns(2)
                        with c_edit1:
                            new_ten = st.text_input("Tên Công Ty", value=row['Tên Công Ty'])
                            new_mst = st.text_input("Mã Số Thuế", value=row['Mã Số Thuế'])
                            new_chu = st.text_input("Chủ doanh nghiệp", value=row['Chủ Doanh Nghiệp'])
                        with c_edit2:
                            new_dc = st.text_input("Địa chỉ", value=row['Địa Chỉ'])
                            new_lh = st.text_input("Liên hệ", value=row['Liên Hệ'])
                        
                        new_gc = st.text_area("Ghi chú", value=row['Ghi Chú'], height=150)
                        
                        col_save1, col_save2 = st.columns(2)
                        with col_save1:
                            if st.form_submit_button("💾 LƯU THAY ĐỔI", use_container_width=True):
                                # Cập nhật vào DataFrame tổng
                                now = datetime.now().strftime("%d/%m/%Y %H:%M")
                                df.loc[i] = [
                                    new_ten, new_mst, new_chu, new_dc, 
                                    new_lh, new_gc, f"https://zalo.me/{clean_phone(new_lh)}", now
                                ]
                                # Lưu xuống file Excel
                                df.to_excel(DATA_FILE, index=False)
                                st.session_state[edit_mode_key] = False
                                st.success("Đã cập nhật dữ liệu thành công!")
                                st.rerun()
                        with col_save2:
                            if st.form_submit_button("❌ HỦY BỎ", use_container_width=True):
                                st.session_state[edit_mode_key] = False
                                st.rerun()

                # --- CHẾ ĐỘ HIỂN THỊ (MẶC ĐỊNH) ---
                else:
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        st.markdown(f"**📍 Địa chỉ:** {row['Địa Chỉ']}")
                        maps_q = urllib.parse.quote(str(row['Địa Chỉ']))
                        st.markdown(f"🔗 [Xem bản đồ](https://www.google.com/maps/search/?api=1&query={maps_q})")
                        st.info(f"📝 **Ghi chú:**\n\n{row['Ghi Chú']}")
                    
                    with c2:
                        st.markdown(f"**👤 Chủ doanh nghiệp:** {row['Chủ Doanh Nghiệp']}")
                        st.markdown(f"**📞 Liên hệ:** {row['Liên Hệ']}")
                        if row['Liên Hệ']:
                            z_link = f"https://zalo.me/{clean_phone(row['Liên Hệ'])}"
                            st.markdown(f"""
                                <a href="{z_link}" target="_blank" style="text-decoration:none;">
                                    <div style="background-color:#0068FF;color:white;padding:10px;border-radius:10px;text-align:center;font-weight:bold;">
                                        💬 NHẮN ZALO
                                    </div>
                                </a>
                            """, unsafe_allow_html=True)
                        st.caption(f"Cập nhật: {row['Cập Nhật Cuối']}")

                    # Nút chức năng cho Admin (Xóa & Sửa)
                    if st.session_state["role"] == "admin":
                        st.divider()
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button("🗑️ Xóa dữ liệu", key=f"del_{i}", use_container_width=True):
                                df = df.drop(i)
                                df.to_excel(DATA_FILE, index=False)
                                st.warning("Đã xóa dữ liệu!")
                                st.rerun()
                        with col_btn2:
                            if st.button("📝 Chỉnh sửa", key=f"edit_btn_{i}", use_container_width=True):
                                st.session_state[edit_mode_key] = True
                                st.rerun()

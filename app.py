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
def clean_phone(phone):
    if pd.isna(phone) or str(phone).strip() == "": return ""
    return re.sub(r'\D', '', str(phone))

def hash_pwd(pwd): return hashlib.sha256(str.encode(pwd)).hexdigest()

def load_data_from_sheet(sheet_name, columns):
    if os.path.exists(DATA_FILE):
        try:
            with pd.ExcelFile(DATA_FILE) as xls:
                if sheet_name in xls.sheet_names:
                    # Đọc dữ liệu và ép kiểu string, xử lý giá trị trống thành chuỗi rỗng
                    df = pd.read_excel(xls, sheet_name=sheet_name, dtype=str).fillna("")
                    for col in columns:
                        if col not in df.columns: df[col] = ""
                    return df[columns]
        except: pass
    return pd.DataFrame(columns=columns)

def save_to_sheet(df, sheet_name):
    all_sheets = {}
    if os.path.exists(DATA_FILE):
        with pd.ExcelFile(DATA_FILE) as xls:
            for s in xls.sheet_names:
                all_sheets[s] = pd.read_excel(xls, sheet_name=s, dtype=str).fillna("")
    all_sheets[sheet_name] = df
    with pd.ExcelWriter(DATA_FILE, engine='openpyxl') as writer:
        for s_name, s_df in all_sheets.items():
            s_df.to_excel(writer, sheet_name=s_name, index=False)

# --- 3. GIAO DIỆN ---
st.set_page_config(page_title="TEETA CODE", layout="wide")
if "role" not in st.session_state: st.session_state["role"] = None

if st.session_state["role"] is None:
    st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>TEETA CODE</h1>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🔑 Thành viên", "🛡️ Admin", "🌐 Khách"])
    with t1:
        u = st.text_input("Username", key="l_u")
        p = st.text_input("Password", type="password", key="l_p")
        if st.button("ĐĂNG NHẬP"):
            if os.path.exists(USER_FILE):
                users = pd.read_excel(USER_FILE, dtype=str).fillna("")
                if not users[(users["username"] == u) & (users["password"] == hash_pwd(p))].empty:
                    st.session_state["role"], st.session_state["username"] = "user", u; st.rerun()
            st.error("Sai tài khoản!")
    with t2:
        ua = st.text_input("Admin User")
        pa = st.text_input("Admin Pass", type="password")
        if st.button("XÁC NHẬN ADMIN"):
            if ua == ADMIN_USER and pa == ADMIN_PASS:
                st.session_state["role"], st.session_state["username"] = "admin", "QUẢN TRỊ VIÊN"; st.rerun()
    with t3:
        if st.button("VÀO XEM (GUEST)"):
            st.session_state["role"], st.session_state["username"] = "guest", "Khách"; st.rerun()
    st.stop()

# --- 4. TRANG CHỦ ---
st.sidebar.subheader(f"👋 {st.session_state['username']}")
if st.sidebar.button("🚪 Đăng xuất"): st.session_state["role"] = None; st.rerun()
st.sidebar.divider()
st.sidebar.markdown('🎵 **Giải Trí**')
st.sidebar.markdown('<iframe src="https://www.nhaccuatui.com/mh/background/L6Wv9X7Z2z3n" width="100%" height="150" frameborder="0"></iframe>', unsafe_allow_html=True)

tab_cty, tab_pers, tab_add = st.tabs(["🏢 Công Ty", "👤 Liên Hệ Cá Nhân", "➕ Thêm Mới"])

# --- XỬ LÝ CÔNG TY ---
with tab_cty:
    df_cty = load_data_from_sheet("CongTy", COLUMNS_CTY)
    q_cty = st.text_input("🔎 Tìm kiếm công ty...", key="q_cty")
    f_cty = df_cty[df_cty['Tên Công Ty'].str.contains(q_cty, case=False) | df_cty['Mã Số Thuế'].str.contains(q_cty, case=False)] if q_cty else df_cty
    
    for i, r in f_cty.iterrows():
        with st.expander(f"🏢 {r['Tên Công Ty']} - {r['Mã Số Thuế']}"):
            c1, c2 = st.columns(2)
            c1.write(f"📍 **Địa chỉ:** {r['Địa Chỉ']}")
            # FIX LỖI: Kiểm tra có địa chỉ mới hiện link bản đồ
            if str(r['Địa Chỉ']).strip():
                addr_encoded = urllib.parse.quote(str(r['Địa Chỉ']))
                c1.markdown(f"[🌍 Xem Bản Đồ](https://www.google.com/maps/search/?api=1&query={addr_encoded})")
            
            c2.write(f"👤 **Chủ:** {r['Chủ Doanh Nghiệp']} | 📞 **LH:** {r['Liên Hệ']}")
            # FIX LỖI: Kiểm tra có SĐT mới hiện nút Zalo
            phone_clean = clean_phone(r['Liên Hệ'])
            if phone_clean:
                c2.markdown(f'<a href="https://zalo.me/{phone_clean}" target="_blank" style="text-decoration:none;"><div style="background-color:#0068FF;color:white;padding:10px;border-radius:10px;text-align:center;font-weight:bold;">💬 NHẮN ZALO</div></a>', unsafe_allow_html=True)
            
            st.info(f"📝 **Ghi chú:** {r['Ghi Chú']}")
            if st.session_state["role"] == "admin":
                if st.button("🗑️ Xóa", key=f"del_cty_{i}"):
                    save_to_sheet(df_cty.drop(i), "CongTy"); st.rerun()

# --- XỬ LÝ LIÊN HỆ ---
with tab_pers:
    df_p = load_data_from_sheet("LienHeCaNhan", COLUMNS_PERS)
    q_p = st.text_input("🔎 Tìm tên người...", key="q_p")
    f_p = df_p[df_p['Tên Liên Hệ'].str.contains(q_p, case=False)] if q_p else df_p
    for i, r in f_p.iterrows():
        with st.expander(f"👤 {r['Tên Liên Hệ']} - {r['Công Ty Đang Làm']}"):
            c1, c2 = st.columns(2)
            c1.write(f"📍 **Địa chỉ:** {r['Địa Chỉ']}")
            if str(r['Địa Chỉ']).strip():
                addr_p_encoded = urllib.parse.quote(str(r['Địa Chỉ']))
                c1.markdown(f"[🌍 Xem Bản Đồ](https://www.google.com/maps/search/?api=1&query={addr_p_encoded})")
            
            p_zalo = clean_phone(r['Zalo'])
            if p_zalo: c2.markdown(f'[💬 Zalo](https://zalo.me/{p_zalo})')
            if str(r['Facebook']).strip(): c2.markdown(f'[📘 Facebook]({r["Facebook"]})')
            st.info(f"📝 **Ghi chú:** {r['Ghi Chú']}")

# --- THÊM MỚI ---
with tab_add:
    if st.session_state["role"] != "admin":
        st.warning("Chỉ Admin mới có quyền thêm dữ liệu.")
    else:
        with st.form("add_new"):
            st.subheader("Thêm Công Ty Mới")
            f1, f2 = st.columns(2)
            name = f1.text_input("Tên Công Ty")
            mst = f1.text_input("Mã Số Thuế")
            owner = f1.text_input("Chủ Doanh Nghiệp")
            addr = f2.text_input("Địa Chỉ")
            phone = f2.text_input("Số Điện Thoại")
            note = st.text_area("Ghi Chú")
            if st.form_submit_button("LƯU HỆ THỐNG"):
                if name:
                    df_now = load_data_from_sheet("CongTy", COLUMNS_CTY)
                    new_row = pd.DataFrame([[name, mst, owner, addr, phone, note, "", datetime.now().strftime("%d/%m/%Y %H:%M")]], columns=COLUMNS_CTY)
                    save_to_sheet(pd.concat([df_now, new_row], ignore_index=True), "CongTy")
                    st.success("Đã thêm!"); st.rerun()

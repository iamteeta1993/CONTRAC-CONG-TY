import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime
import urllib.parse
import re
from tempfile import NamedTemporaryFile

# ================= CONFIG =================
DATA_FILE = "data_congty.xlsx"
USER_FILE = "users.xlsx"

COLUMNS_CTY = ["Tên Công Ty", "Mã Số Thuế", "Chủ Doanh Nghiệp", "Địa Chỉ", "Liên Hệ", "Ghi Chú", "Zalo", "Cập Nhật Cuối"]
COLUMNS_PERS = ["Tên Liên Hệ", "Công Ty Đang Làm", "Địa Chỉ", "Zalo", "Facebook", "Ghi Chú", "Cập Nhật Cuối"]

ADMIN_USER = "admin"
ADMIN_PASS_HASH = hashlib.sha256("123".encode()).hexdigest()

# ================= UTILS =================
def clean_phone(phone):
    return re.sub(r'\D', '', str(phone))

def hash_pwd(pwd):
    return hashlib.sha256(str(pwd).encode()).hexdigest()

def load_data(sheet, columns):
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_excel(DATA_FILE, sheet_name=sheet, dtype=str).fillna("")
            for c in columns:
                if c not in df.columns:
                    df[c] = ""
            return df[columns]
        except:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

def save_data(df, sheet):
    temp = NamedTemporaryFile(delete=False)

    all_sheets = {}
    if os.path.exists(DATA_FILE):
        try:
            xls = pd.ExcelFile(DATA_FILE)
            for s in xls.sheet_names:
                all_sheets[s] = pd.read_excel(xls, sheet_name=s, dtype=str).fillna("")
        except:
            pass

    all_sheets[sheet] = df.fillna("")

    with pd.ExcelWriter(temp.name, engine='openpyxl') as writer:
        for s, d in all_sheets.items():
            d.to_excel(writer, sheet_name=s, index=False)

    os.replace(temp.name, DATA_FILE)

# ================= LOGIN =================
st.set_page_config(page_title="TEETA CODE", layout="wide")

if "role" not in st.session_state:
    st.session_state.role = None

if st.session_state.role is None:
    st.title("🔐 TEETA CODE")

    tab1, tab2, tab3 = st.tabs(["User", "Admin", "Guest"])

    # USER
    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login User"):
            if os.path.exists(USER_FILE):
                users = pd.read_excel(USER_FILE, dtype=str).fillna("")
                if "username" in users.columns and "password" in users.columns:
                    if not users[(users.username == u) & (users.password == hash_pwd(p))].empty:
                        st.session_state.role = "user"
                        st.session_state.username = u
                        st.rerun()
            st.error("Sai tài khoản")

    # ADMIN
    with tab2:
        ua = st.text_input("Admin User")
        pa = st.text_input("Admin Pass", type="password")
        if st.button("Login Admin"):
            if ua == ADMIN_USER and hash_pwd(pa) == ADMIN_PASS_HASH:
                st.session_state.role = "admin"
                st.session_state.username = "ADMIN"
                st.rerun()
            st.error("Sai admin")

    # GUEST
    with tab3:
        if st.button("Vào Guest"):
            st.session_state.role = "guest"
            st.session_state.username = "Khách"
            st.rerun()

    st.stop()

# ================= SIDEBAR =================
st.sidebar.write(f"👋 {st.session_state.username}")
if st.sidebar.button("Đăng xuất"):
    st.session_state.role = None
    st.rerun()

# ================= TABS =================
if st.session_state.role == "admin":
    tab1, tab2, tab3 = st.tabs(["Công Ty", "Liên Hệ", "Thêm"])
else:
    tab1, tab2 = st.tabs(["Công Ty", "Liên Hệ"])

# ================= CÔNG TY =================
with tab1:
    df = load_data("CongTy", COLUMNS_CTY)

    q = st.text_input("Tìm công ty")
    if q:
        df = df[df["Tên Công Ty"].str.contains(q, case=False, na=False) |
                df["Mã Số Thuế"].str.contains(q, case=False, na=False)]

    for i, r in df.iterrows():
        with st.expander(f"{r['Tên Công Ty']} - {r['Mã Số Thuế']}"):

            st.write("📍", r["Địa Chỉ"])
            if r["Địa Chỉ"]:
                st.markdown(f"[Map](http://maps.google.com/?q={urllib.parse.quote(r['Địa Chỉ'])})")

            st.write("📞", r["Liên Hệ"])

            if clean_phone(r["Liên Hệ"]):
                st.markdown(f"[Zalo](https://zalo.me/{clean_phone(r['Liên Hệ'])})")

            st.write("📝", r["Ghi Chú"])

            if st.session_state.role == "admin":
                if st.button("Xóa", key=f"del_cty_{i}"):
                    save_data(df.drop(i).reset_index(drop=True), "CongTy")
                    st.rerun()

# ================= LIÊN HỆ =================
with tab2:
    df = load_data("LienHeCaNhan", COLUMNS_PERS)

    q = st.text_input("Tìm liên hệ")
    if q:
        df = df[df["Tên Liên Hệ"].str.contains(q, case=False, na=False)]

    for i, r in df.iterrows():
        with st.expander(r["Tên Liên Hệ"]):
            st.write("🏢", r["Công Ty Đang Làm"])
            st.write("📍", r["Địa Chỉ"])

            if r["Zalo"]:
                st.markdown(f"[Zalo](https://zalo.me/{clean_phone(r['Zalo'])})")

            if r["Facebook"]:
                fb = r["Facebook"]
                if "http" not in fb:
                    fb = "https://fb.com/" + fb
                st.markdown(f"[Facebook]({fb})")

            if st.session_state.role == "admin":
                if st.button("Xóa", key=f"del_p_{i}"):
                    save_data(df.drop(i).reset_index(drop=True), "LienHeCaNhan")
                    st.rerun()

# ================= THÊM =================
if st.session_state.role == "admin":
    with tab3:

        st.subheader("Thêm công ty")
        name = st.text_input("Tên công ty")
        mst = st.text_input("MST")
        phone = st.text_input("SĐT")

        if st.button("Lưu công ty"):
            if name:
                df = load_data("CongTy", COLUMNS_CTY)

                if mst and mst in df["Mã Số Thuế"].values:
                    st.error("MST đã tồn tại")
                else:
                    new = pd.DataFrame([[
                        name, mst, "", "", phone, "",
                        f"https://zalo.me/{clean_phone(phone)}" if phone else "",
                        datetime.now().strftime("%d/%m/%Y %H:%M")
                    ]], columns=COLUMNS_CTY)

                    save_data(pd.concat([df, new], ignore_index=True), "CongTy")
                    st.success("Đã thêm")
                    st.rerun()

        st.divider()

        st.subheader("Thêm liên hệ")
        pname = st.text_input("Tên")
        if st.button("Lưu liên hệ"):
            if pname:
                df = load_data("LienHeCaNhan", COLUMNS_PERS)

                new = pd.DataFrame([[
                    pname, "", "", "", "", "",
                    datetime.now().strftime("%d/%m/%Y %H:%M")
                ]], columns=COLUMNS_PERS)

                save_data(pd.concat([df, new], ignore_index=True), "LienHeCaNhan")
                st.success("Đã thêm")
                st.rerun()

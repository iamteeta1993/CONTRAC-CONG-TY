import streamlit as st
import pandas as pd
import os
import requests

# --- CẤU HÌNH ---
PASSWORD = "teeta123" 

def get_business_info(keyword):
    """Tìm kiếm thông tin doanh nghiệp theo Tên hoặc MST."""
    try:
        # Sử dụng API tìm kiếm doanh nghiệp
        response = requests.get(f"https://vietqr.io{keyword}")
        if response.status_code == 200:
            data = response.json()
            if data['code'] == "00":
                return data['data']
        return None
    except:
        return None

if "password_correct" not in st.session_state:
    st.set_page_config(page_title="Đăng nhập")
    st.text_input("Vui lòng nhập mật khẩu", type="password", key="pwd_input")
    if st.button("Xác nhận"):
        if st.session_state.pwd_input == PASSWORD:
            st.session_state.password_correct = True
            st.rerun()
        else:
            st.error("Sai mật khẩu!")
    st.stop()

# --- CHƯƠNG TRÌNH CHÍNH ---
EXCEL_FILE = "data_congty.xlsx"
def load_data():
    if os.path.exists(EXCEL_FILE):
        return pd.read_excel(EXCEL_FILE, dtype=str)
    return pd.DataFrame(columns=["Tên Công Ty", "Mã Số Thuế", "Chủ Doanh Nghiệp", "Địa Chỉ", "Liên Hệ", "Zalo"])

st.set_page_config(page_title="Quản Lý Công Ty", layout="wide")
df = load_data()

st.sidebar.title("➕ Thêm Công Ty")
# Ô TÌM KIẾM THÔNG MINH
search_query = st.sidebar.text_input("🔍 Nhập Tên Công Ty hoặc MST để lấy thông tin tự động")

name_val, mst_val, addr_val = "", "", ""

if search_query:
    with st.sidebar.spinner('Đang lấy dữ liệu từ hệ thống...'):
        info = get_business_info(search_query)
        if info:
            name_val = info.get('name', '')
            mst_val = info.get('id', '')
            addr_val = info.get('address', '')
            st.sidebar.success("✅ Tìm thấy dữ liệu!")
        else:
            st.sidebar.warning("❌ Không tìm thấy, bạn hãy tự điền tay nhé.")

with st.sidebar.form("add_form", clear_on_submit=True):
    final_name = st.text_input("Tên Công Ty", value=name_val)
    final_mst = st.text_input("Mã Số Thuế", value=mst_val)
    final_owner = st.text_input("Chủ Doanh Nghiệp")
    final_addr = st.text_input("Địa Chỉ", value=addr_val)
    final_phone = st.text_input("Số Điện Thoại Zalo")
    
    if st.form_submit_button("Lưu Vào Danh Sách"):
        new_row = pd.DataFrame([{
            "Tên Công Ty": final_name, "Mã Số Thuế": final_mst,
            "Chủ Doanh Nghiệp": final_owner, "Địa Chỉ": final_addr,
            "Liên Hệ": final_phone, "Zalo": f"https://zalo.me{final_phone}"
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_excel(EXCEL_FILE, index=False)
        st.success("Đã lưu!")
        st.rerun()

st.title("📂 Danh Sách Công Ty Của Bạn")
search_local = st.text_input("🔎 Tìm nhanh trong danh sách đã lưu...")
display_df = df[df['Tên Công Ty'].str.contains(search_local, case=False, na=False)] if search_local else df

for i, row in display_df.iterrows():
    with st.expander(f"🏢 {row['Tên Công Ty']} - {row['Mã Số Thuế']}"):
        st.write(f"📍 **Địa chỉ:** {row['Địa Chỉ']}")
        st.write(f"👤 **Chủ:** {row['Chủ Doanh Nghiệp']} | 📞 **SĐT:** {row['Liên Hệ']}")
        st.write(f"💬 [Nhắn Zalo ngay]({row['Zalo']})")
        if st.button("🗑️ Xóa", key=f"del_{i}"):
            df.drop(i).to_excel(EXCEL_FILE, index=False)
            st.rerun()

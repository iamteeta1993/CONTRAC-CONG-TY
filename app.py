import streamlit as st
import pandas as pd
import os

# --- CẤU HÌNH MẬT KHẨU ---
PASSWORD = "teeta123" 

def check_password():
    if "password_correct" not in st.session_state:
        st.text_input("Vui lòng nhập mật khẩu để sử dụng App", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Mật khẩu sai, vui lòng nhập lại", type="password", on_change=password_entered, key="password")
        st.error("😕 Sai mật khẩu rồi bạn ơi!")
        return False
    else:
        return True

def password_entered():
    if st.session_state["password"] == PASSWORD:
        st.session_state["password_correct"] = True
        del st.session_state["password"]
    else:
        st.session_state["password_correct"] = False

# --- CHƯƠNG TRÌNH CHÍNH ---
if check_password():
    EXCEL_FILE = "data_congty.xlsx"

    def load_data():
        if os.path.exists(EXCEL_FILE):
            # Đảm bảo MST và SĐT luôn là chuỗi (string) để không mất số 0
            df = pd.read_excel(EXCEL_FILE, dtype={'Mã Số Thuế': str, 'Liên Hệ': str})
            return df
        else:
            return pd.DataFrame(columns=["Tên Công Ty", "Mã Số Thuế", "Chủ Doanh Nghiệp", "Địa Chỉ", "Liên Hệ", "Zalo"])

    st.set_page_config(page_title="Quản Lý Công Ty", layout="wide")
    st.title("📂 Hệ Thống Quản Lý Thông Tin Công Ty")
    
    if st.sidebar.button("Đăng xuất"):
        st.session_state["password_correct"] = False
        st.rerun()

    df = load_data()

    # --- CỘT BÊN TRÁI: THÊM MỚI ---
    st.sidebar.header("➕ Thêm Công Ty Mới")
    with st.sidebar.form("add_form", clear_on_submit=True):
        new_name = st.text_input("Tên Công Ty")
        new_mst = st.text_input("Mã Số Thuế")
        new_owner = st.text_input("Chủ Doanh Nghiệp")
        new_addr = st.text_input("Địa Chỉ")
        new_phone = st.text_input("Số Điện Thoại")
        submit = st.form_submit_button("Lưu Vào Excel")

        if submit:
            if new_name and new_mst:
                new_data = {
                    "Tên Công Ty": [new_name],
                    "Mã Số Thuế": [new_mst],
                    "Chủ Doanh Nghiệp": [new_owner],
                    "Địa Chỉ": [new_addr],
                    "Liên Hệ": [new_phone],
                    "Zalo": [f"https://zalo.me{new_phone}"]
                }
                new_df = pd.DataFrame(new_data)
                df = pd.concat([df, new_df], ignore_index=True)
                df.to_excel(EXCEL_FILE, index=False)
                st.sidebar.success("Đã lưu thành công!")
                st.rerun()
            else:
                st.sidebar.error("Vui lòng nhập ít nhất Tên và MST")

    # --- PHẦN CHÍNH: TÌM KIẾM VÀ HIỂN THỊ ---
    search_term = st.text_input("🔍 Nhập tên hoặc mã số thuế để tìm nhanh...", "")

    if search_term:
        filtered_df = df[
            df['Tên Công Ty'].astype(str).str.contains(search_term, case=False, na=False) |
            df['Mã Số Thuế'].astype(str).str.contains(search_term, case=False, na=False)
        ]
    else:
        filtered_df = df

    if not filtered_df.empty:
        for index, row in filtered_df.iterrows():
            with st.expander(f"🏢 {row['Tên Công Ty']} - MST: {row['Mã Số Thuế']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**👤 Chủ:** {row['Chủ Doanh Nghiệp']}")
                    st.write(f"**📍 Địa chỉ:** {row['Địa Chỉ']}")
                with col2:
                    st.write(f"**📞 SĐT:** {row['Liên Hệ']}")
                    st.write(f"**💬 Zalo:** [Mở chat Zalo]({row['Zalo']})")
                
                # Nút Xóa và Sửa
                c1, c2 = st.columns([1, 5])
                with c1:
                    if st.button("🗑️ Xóa", key=f"del_{index}"):
                        df = df.drop(index)
                        df.to_excel(EXCEL_FILE, index=False)
                        st.success("Đã xóa!")
                        st.rerun()
                with c2:
                    if st.button("📝 Sửa nhanh", key=f"edit_{index}"):
                        st.info("Để sửa, bạn hãy nhập lại thông tin vào cột bên trái với đúng Tên & MST cũ, hệ thống sẽ cập nhật (hoặc bạn có thể sửa trực tiếp trong file Excel rồi upload lại GitHub).")

    else:
        st.info("Chưa có dữ liệu hoặc không tìm thấy.")

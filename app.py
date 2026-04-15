import streamlit as st
import pandas as pd
import os

# --- CẤU HÌNH MẬT KHẨU ---
PASSWORD = "iamteeta"  # <--- BẠN THAY ĐỔI MẬT KHẨU CỦA BẠN Ở ĐÂY

def check_password():
    """Trả về True nếu mật khẩu đúng."""
    if "password_correct" not in st.session_state:
        # Lần đầu tiên mở app
        st.text_input("Vui lòng nhập mật khẩu để sử dụng App", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # Nhập sai mật khẩu
        st.text_input("Mật khẩu sai, vui lòng nhập lại", type="password", on_change=password_entered, key="password")
        st.error("😕 Sai mật khẩu rồi bạn ơi!")
        return False
    else:
        return True

def password_entered():
    """Kiểm tra mật khẩu người dùng vừa nhập."""
    if st.session_state["password"] == PASSWORD:
        st.session_state["password_correct"] = True
        del st.session_state["password"]  # Xóa mật khẩu khỏi state cho bảo mật
    else:
        st.session_state["password_correct"] = False

# --- CHƯƠNG TRÌNH CHÍNH ---
if check_password():
    # Tên file Excel để lưu dữ liệu
    EXCEL_FILE = "data_congty.xlsx"

    def load_data():
        if os.path.exists(EXCEL_FILE):
            return pd.read_excel(EXCEL_FILE)
        else:
            return pd.DataFrame(columns=["Tên Công Ty", "Mã Số Thuế", "Chủ Doanh Nghiệp", "Địa Chỉ", "Liên Hệ", "Zalo"])

    st.set_page_config(page_title="Quản Lý Công Ty", layout="wide")
    st.title("📂 Hệ Thống Quản Lý Thông Tin Công Ty")
    
    # Nút Đăng xuất
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
                st.sidebar.error("Vui lòng nhập Tên và MST")

    # --- PHẦN CHÍNH: TÌM KIẾM VÀ HIỂN THỊ ---
    search_term = st.text_input("🔍 Nhập tên hoặc mã số thuế để tìm nhanh...", "")

    if search_term:
        filtered_df = df[
            df['Tên Công Ty'].astype(str).str.contains(search_term, case=False) |
            df['Mã Số Thuế'].astype(str).str.contains(search_term, case=False)
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
    else:
        st.info("Chưa có dữ liệu hoặc không tìm thấy.")

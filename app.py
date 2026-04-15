import streamlit as st
import pandas as pd

# Cấu hình trang
st.set_page_config(page_title="Quản Lý Công Ty", layout="wide")

st.title("📂 Hệ Thống Quản Lý Thông Tin Công Ty")

# 1. Dữ liệu mẫu (Bạn có thể thay thế bằng file Excel của bạn)
data = [
    {
        "Tên Công Ty": "Công ty TNHH Giải Pháp AI",
        "Mã Số Thuế": "0123456789",
        "Chủ Doanh Nghiệp": "Nguyễn Văn A",
        "Địa Chỉ": "123 Đường ABC, Quận 1, TP.HCM",
        "Liên Hệ": "0901234567",
        "Zalo": "https://zalo.me"
    },
    {
        "Tên Công Ty": "Cơ Khí Chính Xác Fanuc",
        "Mã Số Thuế": "9876543210",
        "Chủ Doanh Nghiệp": "Trần Thị B",
        "Địa Chỉ": "Khu Công Nghiệp VSIP, Bình Dương",
        "Liên Hệ": "0911222333",
        "Zalo": "https://zalo.me"
    }
]

df = pd.DataFrame(data)

# 2. Thanh tìm kiếm
search_term = st.text_input("🔍 Nhập tên công ty hoặc mã số thuế để tìm kiếm...", "")

# 3. Lọc dữ liệu theo tìm kiếm
if search_term:
    filtered_df = df[
        df['Tên Công Ty'].str.contains(search_term, case=False, na=False) |
        df['Mã Số Thuế'].str.contains(search_term, case=False, na=False)
    ]
else:
    filtered_df = df

# 4. Hiển thị giao diện
if not filtered_df.empty:
    for index, row in filtered_df.iterrows():
        with st.expander(f"🏢 {row['Tên Công Ty']} - MST: {row['Mã Số Thuế']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**👤 Chủ doanh nghiệp:** {row['Chủ Doanh Nghiệp']}")
                st.write(f"**📍 Địa chỉ:** {row['Địa Chỉ']}")
            with col2:
                st.write(f"**📞 Liên hệ:** {row['Liên Hệ']}")
                st.write(f"**💬 Zalo:** [Nhấn để nhắn tin]({row['Zalo']})")
            st.button("Chỉnh sửa", key=f"edit_{index}")
else:
    st.warning("Không tìm thấy thông tin công ty này.")

# 5. Nút thêm mới (Giao diện)
st.sidebar.header("Thêm Công Ty Mới")
with st.sidebar.form("add_form"):
    new_name = st.text_input("Tên Công Ty")
    new_mst = st.text_input("Mã Số Thuế")
    new_owner = st.text_input("Chủ Doanh Nghiệp")
    submit = st.form_submit_button("Lưu Thông Tin")


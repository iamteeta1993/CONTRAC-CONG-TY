# --- 4. GIAO DIỆN CHÍNH ---
# CSS tùy chỉnh để làm gọn giao diện expander
st.markdown("""
<style>
    [data-testid="stExpander"] {
        border-radius: 10px;
        border: 1px solid #444;
        margin-bottom: 15px;
    }
    .stButton > button {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<div style='text-align: center; margin-top: -60px;'> <h1 style='color: #FF4B4B; font-family: Arial Black;'>TEETA <span style='color: #31333F;'>CODE</span></h1> </div>", unsafe_allow_html=True)

# LOAD DỮ LIỆU BAN ĐẦU
df = load_data()

# =========================================================
# --- CẤU TRÚC SIDEBAR MỚI (LÀM GỌN) ---
# =========================================================
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
            st.download_button("📥 Xuất Excel", f, file_name="data_teetacode.xlsx", use_container_width=True)

# --- SIDEBAR: GIẢI TRÍ ---
st.sidebar.divider()
st.sidebar.subheader("🎵 Giải Trí")
tab_nct, tab_music, tab_video = st.sidebar.tabs(["NCT", "Spotify", "YouTube"])

# ... (Giữ nguyên code các tab giải trí từ code cũ của bạn ở đây) ...
# Ví dụ:
with tab_nct:
    nct_url = "https://www.nhaccuatui.com/mh/background/L6Wv9X7Z2z3n"
    st.components.v1.html(f'<iframe src="{nct_url}" width="100%" height="150" frameborder="0" allowfullscreen allow="autoplay"></iframe>', height=160)
with tab_music:
    spotify_url = "https://open.spotify.com/embed/playlist/37i9dQZF1DWZeKHAHw4v9G"
    st.components.v1.html(f'<iframe src="{spotify_url}" width="100%" height="152" frameBorder="0" allow="autoplay; encrypted-media; seamless"></iframe>', height=160)
with tab_video:
    yt_id = "jfKfPfyJRdk" 
    st.components.v1.html(f'<iframe width="100%" height="152" src="https://www.youtube.com/embed/{yt_id}" frameborder="0" allowfullscreen></iframe>', height=160)


# =========================================================
# --- KHU VỰC NỘI DUNG TRUNG TÂM MỚI ---
# =========================================================

# Xác định danh sách các Tab dựa trên quyền
if st.session_state["role"] == "admin":
    tabs_main = st.tabs(["🔍 Tra cứu & Quản lý", "➕ Thêm Công Ty Mới"])
else:
    tabs_main = st.tabs(["🔍 Tra cứu dữ liệu"])


# --- TAB 1: TRA CỨU & QUẢN LÝ (Chung cho User/Admin) ---
with tabs_main[0]:
    st.markdown("### 🔎 Tìm kiếm nhanh")
    q = st.text_input("", placeholder="Nhập Tên Công Ty hoặc Mã Số Thuế để tìm kiếm...", label_visibility="collapsed")

    if not df.empty:
        # Lọc dữ liệu
        f_df = df[df['Tên Công Ty'].str.contains(q, case=False, na=False) | 
                  df['Mã Số Thuế'].str.contains(q, case=False, na=False)] if q else df
        
        st.write(f"Tìm thấy **{len(f_df)}** kết quả.")

        # Định nghĩa hàm xóa để dùng trong loop
        def delete_entry(index):
            df_curr = load_data()
            df_curr = df_curr.drop(index)
            df_curr.to_excel(DATA_FILE, index=False)
            st.success("Đã xóa dữ liệu thành công!")
            st.rerun()

        # Hiển thị kết quả dạng Expander
        for i, row in f_df.iterrows():
            with st.expander(f"🏢 {row['Tên Công Ty']} - MST: {row['Mã Số Thuế']}", expanded=(q!="")):
                
                # --- PHẦN HIỂN THỊ CHI TIẾT ---
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**📍 Địa chỉ:** {row['Địa Chỉ']}")
                    maps_q = urllib.parse.quote(str(row['Địa Chỉ']))
                    st.markdown(f"🌍 [Xem bản đồ](https://www.google.com/maps/search/?api=1&query={maps_q})")
                    if st.session_state["role"] in ["admin", "user"]:
                        st.markdown(f"**📋 Ghi chú:** {row['Ghi Chú'] or '...'}")
                
                with c2:
                    st.markdown(f"**👨‍💼 Chủ doanh nghiệp:** {row['Chủ Doanh Nghiệp'] or '...'}")
                    st.markdown(f"**📞 Liên hệ:** `{row['Liên Hệ'] or '...'}`")
                    if row['Liên Hệ']:
                        z_link = f"https://zalo.me/{clean_phone(row['Liên Hệ'])}"
                        st.markdown(f"""<a href="{z_link}" target="_blank" style="text-decoration:none;"><div style="background-color:#0068FF;color:white;padding:5px 10px;border-radius:5px;text-align:center;font-weight:bold;font-size:14px;display:inline-block;">💬 Nhắn Zalo</div></a>""", unsafe_allow_html=True)
                    st.caption(f"Cập nhật: {row['Cập Nhật Cuối']}")

                # --- PHẦN QUẢN LÝ CHO ADMIN (SỬA/XÓA) ---
                if st.session_state["role"] == "admin":
                    st.divider()
                    col_edit, col_del = st.columns([1, 1])
                    
                    with col_del:
                        # Nút xóa yêu cầu xác nhận lần 2 bằng st.popover (tránh bấm nhầm)
                        with st.popover("🗑️ Xóa", use_container_width=True):
                            st.warning(f"Bạn chắc chắn muốn xóa '{row['Tên Công Ty']}'?")
                            if st.button("Xác nhận xóa", key=f"conf_del_{i}", type="primary"):
                                delete_entry(i)

                    with col_edit:
                        # Nút sửa mở ra form ẩn
                        if st.button("📝 Sửa thông tin", key=f"btn_edit_{i}", use_container_width=True):
                            st.session_state[f"editing_{i}"] = not st.session_state.get(f"editing_{i}", False)

                    # Form sửa thông tin (hiển thị khi bấm nút Sửa)
                    if st.session_state.get(f"editing_{i}", False):
                        st.markdown("#### 📝 Cập nhật thông tin")
                        with st.form(key=f"form_edit_{i}"):
                            new_name = st.text_input("Tên Công Ty", value=row['Tên Công Ty'])
                            new_mst = st.text_input("Mã Số Thuế", value=row['Mã Số Thuế'])
                            new_owner = st.text_input("Chủ Doanh Nghiệp", value=row['Chủ Doanh Nghiệp'])
                            new_addr = st.text_input("Địa chỉ", value=row['Địa Chỉ'])
                            new_phone_raw = st.text_input("Số điện thoại", value=row['Liên Hệ'])
                            new_note = st.text_area("Ghi chú", value=row['Ghi Chú'])
                            
                            c_save1, c_save2 = st.columns([1, 1])
                            with c_save1:
                                submit_edit = st.form_submit_button("💾 Lưu thay đổi", type="primary", use_container_width=True)
                            with c_save2:
                                if st.form_submit_button("❌ Hủy", use_container_width=True):
                                    st.session_state[f"editing_{i}"] = False
                                    st.rerun()

                            if submit_edit:
                                df_curr = load_data()
                                now = datetime.now().strftime("%d/%m/%Y %H:%M")
                                new_phone_clean = clean_phone(new_phone_raw)
                                
                                # Cập nhật dòng dữ liệu
                                df_curr.loc[i] = [new_name, new_mst, new_owner, new_addr, new_phone_raw, new_note, f"https://zalo.me/{new_phone_clean}", now]
                                df_curr.to_excel(DATA_FILE, index=False)
                                
                                st.success("Đã cập nhật thành công!")
                                st.session_state[f"editing_{i}"] = False
                                st.rerun()
    else:
        st.info("Hệ thống chưa có dữ liệu. Vui lòng chuyển sang Tab 'Thêm Công Ty Mới' để nhập dữ liệu.")


# --- TAB 2: THÊM CÔNG TY MỚI (Chỉ dành cho Admin) ---
if st.session_state["role"] == "admin":
    with tabs_main[1]:
        st.markdown("### ➕ Nhập liệu thủ công hoặc tra cứu")
        
        # Tra cứu MST nhanh trước khi nhập
        search_mst = st.text_input("🔍 Tra MST nhanh (API VietQR)", placeholder="Nhập MST để tự động điền tên và địa chỉ...")
        n_v, a_v = "", ""
        
        if search_mst:
            with st.spinner("Đang tra cứu dữ liệu..."):
                info = get_business_info(search_mst)
            if info: 
                n_v, a_v = info.get('name', ''), info.get('address', '')
                st.success("Đã tìm thấy dữ liệu! Hãy kiểm tra lại và bổ sung các trường còn thiếu bên dưới.")
            else: 
                st.warning("Không tìm thấy MST này hoặc API bận. Vui lòng nhập thủ công.")
                
        st.divider()
        st.markdown("#### Form nhập thông tin chi tiết")
        
        # Form thêm dữ liệu chính
        with st.form("add_form", clear_on_submit=True):
            f_col1, f_col2 = st.columns(2)
            
            with f_col1:
                fn = st.text_input("Tên Công Ty *", value=n_v, placeholder="Tên đầy đủ của doanh nghiệp")
                fm = st.text_input("Mã Số Thuế *", value=search_mst, placeholder="Ví dụ: 0101234567")
                fo = st.text_input("Chủ Doanh Nghiệp", placeholder="Tên người đại diện")
            
            with f_col2:
                fa = st.text_input("Địa chỉ", value=a_v, placeholder="Số nhà, đường, phường, quận, tỉnh")
                fp = st.text_input("Số điện thoại Liên hệ", placeholder="Ví dụ: 0901234567")
            
            fg = st.text_area("Ghi chú nội bộ", placeholder="Thông tin bổ sung, lịch sử làm việc...")
            
            st.markdown("* : Các trường bắt buộc nhập")
            submit_add = st.form_submit_button("➕ LƯU VÀO HỆ THỐNG", type="primary", use_container_width=True)

            if submit_add:
                if not fn or not fm:
                    st.error("Vui lòng nhập đầy đủ 'Tên Công Ty' và 'Mã Số Thuế'.")
                else:
                    df_curr = load_data()
                    now = datetime.now().strftime("%d/%m/%Y %H:%M")
                    phone_clean = clean_phone(fp)
                    
                    new_row = pd.DataFrame([[fn, fm, fo, fa, fp, fg, f"https://zalo.me/{phone_clean}", now]], columns=COLUMNS)
                    df_new = pd.concat([df_curr, new_row], ignore_index=True)
                    df_new.to_excel(DATA_FILE, index=False)
                    st.success(f"Đã thêm công ty '{fn}' thành công!")
                    st.balloons()
                    st.rerun() # Reload để quay về Tab 1 xem dữ liệu mới

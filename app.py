# --- SIDEBAR: GIẢI TRÍ (SPOTIFY, YOUTUBE & NHACCUATUI) ---
st.sidebar.divider()
st.sidebar.subheader("🎵 Giải Trí")
# Thêm Tab NCT vào đây
tab_music, tab_video, tab_nct = st.sidebar.tabs(["Spotify", "YouTube", "NCT"])

with tab_music:
    # Link Playlist Spotify
    spotify_url = "https://open.spotify.com/embed/playlist/37i9dQZF1DWZeKHA6V9Z1u" # Ví dụ link Focus
    st.components.v1.html(f"""
        <iframe src="{spotify_url}" width="100%" height="152" frameBorder="0" 
        allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" 
        style="border-radius:12px;"></iframe>
    """, height=160)

with tab_video:
    # ID Video YouTube (Lofi Music)
    yt_id = "jfKfPfyJRdk" 
    st.components.v1.html(f"""
        <iframe width="100%" height="152" src="https://www.youtube.com/embed/{yt_id}" 
        frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
        allowfullscreen style="border-radius:12px;"></iframe>
    """, height=160)

with tab_nct:
    # Mã nhúng Nhaccuatui (Thay link src bằng bài hát/playlist bạn thích)
    nct_url = "https://www.nhaccuatui.com/mh/background/L6Wv9X7Z2z3n"
    st.components.v1.html(f"""
        <iframe src="{nct_url}" width="100%" height="150" 
        frameborder="0" allowfullscreen allow="autoplay"></iframe>
    """, height=160)

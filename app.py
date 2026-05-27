import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

st.set_page_config(page_title="SynapseCare Dashboard", layout="wide")

st.title("🧠 SynapseCare - Hệ Thống Tối Ưu Hiệu Suất & Thể Trạng Học Đường")
st.subheader("Trợ lý AI phân tích sinh học và quản lý Stress dành cho Gen Z")
st.markdown("---")

# Múi giờ Việt Nam chuẩn
tz_vietnam = ZoneInfo("Asia/Ho_Chi_Minh")

# Khởi tạo các kho lưu trữ dữ liệu thông minh trong session_state
if 'current_day_records' not in st.session_state:
    st.session_state.current_day_records = []  
if 'daily_summary_history' not in st.session_state:
    st.session_state.daily_summary_history = []  
if 'auto_days_overloaded' not in st.session_state:
    st.session_state.auto_days_overloaded = 0
if 'simulated_date' not in st.session_state:
    st.session_state.simulated_date = datetime.now(tz_vietnam)

# --- 1. KHU VỰC XỬ LÝ THANH SIDEBAR ---
st.sidebar.header("⚙️ Giả lập tín hiệu Vòng đeo tay")
student_name = st.sidebar.text_input("Tên học sinh:", "Nguyễn Văn A")
base_hrv = st.sidebar.slider("Chỉ số HRV nền (Lúc khỏe mạnh):", 40, 100, 65)

st.sidebar.markdown("---")
st.sidebar.write("👉 Chọn trạng thái nhanh dưới đây:")
sim_state = st.sidebar.selectbox("Chọn trạng thái nhanh:", ["Bình thường", "Cày đề quá tải", "Áp lực phòng thi"])

if sim_state == "Bình thường":
    calc_bpm = 75
    calc_hrv = int(base_hrv * 1.0)
elif sim_state == "Cày đề quá tải":
    calc_bpm = 95
    calc_hrv = int(base_hrv * 0.5)
else:
    calc_bpm = 120
    calc_hrv = int(base_hrv * 0.2)

calc_hrv = max(10, min(100, calc_hrv))

bpm = st.sidebar.slider("Nhịp tim thực tế (BPM):", 40, 160, calc_bpm)
hrv = st.sidebar.slider("Biến thiên nhịp tim (HRV):", 10, 100, calc_hrv)

# Khử lỗi toán học ngầm bằng biến chia an toàn
safe_base = float(base_hrv) if base_hrv > 0 else 1.0
mana = int(max(0, min(100, (float(hrv) / safe_base) * 100.0)))

is_panic = bpm > 100 and hrv < 30
is_burnout = mana < 35 and not is_panic
is_overload = 35 <= mana < 65 and not is_panic

# NÚT 1: GHI DỮ LIỆU TRONG NGÀY
if st.sidebar.button("Ghi dữ liệu vào biểu đồ 📊"):
    time_str = datetime.now(tz_vietnam).strftime("%H:%M:%S")
    point_index = len(st.session_state.current_day_records) + 1
    display_axis = f"#{point_index} ({time_str})"
    new_record = {
        "Mốc thời gian": display_axis,
        "

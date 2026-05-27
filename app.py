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

# Khởi tạo các kho lưu trữ dữ liệu thông minh
if 'current_day_records' not in st.session_state:
    st.session_state.current_day_records = []  # Dữ liệu chi tiết của ngày hiện tại
if 'daily_summary_history' not in st.session_state:
    st.session_state.daily_summary_history = []  # Kho lưu trữ các ngày cũ (Bên phải ẩn)
if 'auto_days_overloaded' not in st.session_state:
    st.session_state.auto_days_overloaded = 0
if 'simulated_date' not in st.session_state:
    st.session_state.simulated_date = datetime.now(tz_vietnam)

# --- THANH SIDEBAR ĐIỀU KHIỂN ---
st.sidebar.header("⚙️ Giả lập tín hiệu Vòng đeo tay")
student_name = st.sidebar.text_input("Tên học sinh:", "Nguyễn Văn A")
base_hrv = st.sidebar.slider("Chỉ số HRV nền (Lúc khỏe mạnh):", 40, 100, 65)

st.sidebar.markdown("---")
st.sidebar.write("👉 Chọn trạng thái nhanh dưới đây để tạo dữ liệu trong ngày:")
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

hrv_ratio = hrv / base_hrv
mana = int(max(0, min(100, hrv_ratio * 100)))

is_panic = bpm > 100 and hrv < 30
is_burnout = mana < 35 and not is_panic
is_overload = 35 <= mana < 65 and not is_panic

# NÚT 1: GHI DỮ LIỆU TRONG NGÀY
if st.sidebar.button("Ghi dữ liệu vào biểu đồ 📊"):
    time_str = st.session_state.simulated_date.strftime("%H:%M:%S")
    new_record = {
        "Giờ": time_str,
        "Nhịp tim (BPM)": bpm,
        "Chỉ số HRV (ms)": hrv
    }
    st.session_state.current_day_records.append(new_record)

st.sidebar.markdown("---")
st.sidebar.subheader("📅 Chức năng mô phỏng Chu kỳ Ngày")
date_display = st.session_state.simulated_date.strftime("%d/%m/%Y")
st.sidebar.info("Ngày mô phỏng hiện tại: " + str(date_display))

# NÚT 2: QUA NGÀY MỚI - TỔNG HỢP VÀ RESET BIỂU ĐỒ
if st.sidebar.button("Qua ngày mới ➡️ (Tổng hợp & Reset)"):
    if len(st.session_state.current_day_records) > 0:
        # Tính toán tổng hợp số liệu trung bình của ngày hôm đó
        df_temp = pd.DataFrame(st.session_state.current_day_records)
        avg_bpm = int(df_temp["Nhịp tim (BPM)"].mean())
        avg_hrv = int(df_temp["Chỉ số HRV (ms)"].mean())
        
        # Đánh giá trạng thái tổng thể của cả ngày dựa trên trung bình chỉ số
        day_mana = int((avg_hrv / base_hrv) * 100)
        if avg_bpm > 100 and avg_hrv < 30:
            day_status = "Hoảng loạn cực độ"
            st.session_state.auto_days_overloaded += 1
        elif day_mana < 35:
            day_status = "Kiệt quệ (Burnout)"
            st.session_state.auto_days_overloaded += 1
        elif 35 <= day_mana < 65:
            day_status = "Quá tải"
            st.session_state.auto_days_overloaded += 1
        else:
            day_status = "Khỏe mạnh ổn định"
            st.session_state.auto_days_overloaded = 0
            
        # Lưu vào kho lưu trữ lịch sử ngày cũ
        summary_record = {
            "Ngày": st.session_state.simulated_date.strftime("%d/%m/%Y"),
            "Nhịp tim trung bình": avg_bpm,
            "HRV trung bình": avg_hrv,
            "Trạng thái tổng quan": day_status
        }
        st.session_state.daily_summary_history.append(summary_record)
    else:
        # Nếu ngày hôm đó không bấm nút ghi gì, mặc định là ngày khỏe mạnh an toàn
        summary_record = {
            "Ngày": st.session_state.simulated_date.strftime("%d/%m/%Y"),
            "Nhịp tim trung bình": 75,
            "HRV trung bình": base_hrv,
            "Trạng thái tổng quan": "Khỏe mạnh ổn định"
        }
        st.session_state.daily_summary_history.append(summary_record)
        st.session_state.auto_days_overloaded = 0

    # TIẾN HÀNH RESET: Xóa trắng toàn bộ dữ liệu chi tiết của ngày cũ để sang ngày mới
    st.session_state.current_day_records = []
    # Tăng

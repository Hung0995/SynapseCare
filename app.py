import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

st.set_page_config(page_title="SynapseCare Dashboard", layout="wide")

st.title("🧠 SynapseCare - Hệ Thống Tối Ưu Hiệu Suất & Thể Trạng Học Đường")
st.subheader("Trợ lý AI phân tích sinh học và quản lý Stress dành cho Gen Z")
st.markdown("---")

tz_vietnam = ZoneInfo("Asia/Ho_Chi_Minh")

if 'current_day_records' not in st.session_state:
    st.session_state.current_day_records = []  
if 'daily_summary_history' not in st.session_state:
    st.session_state.daily_summary_history = []  
if 'auto_days_overloaded' not in st.session_state:
    st.session_state.auto_days_overloaded = 0
if 'simulated_date' not in st.session_state:
    st.session_state.simulated_date = datetime.now(tz_vietnam)

# --- 1. SIDEBAR MANAGEMENT ---
st.sidebar.header("⚙️ Giả lập tín hiệu Vòng đeo tay")
student_name = st.sidebar.text_input("Tên học sinh:", "Nguyễn Văn A")
base_hrv = st.sidebar.slider("Chỉ số HRV nền (Lúc khỏe mạnh):", 40, 100, 65)

st.sidebar.markdown("---")
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

safe_base = float(base_hrv) if base_hrv > 0 else 1.0
mana = int(max(0, min(100, (float(hrv) / safe_base) * 100.0)))

is_panic = bpm > 100 and hrv < 30
is_burnout = mana < 35 and not is_panic
is_overload = 35 <= mana < 65 and not is_panic

# NÚT GHI DỮ LIỆU
if st.sidebar.button("Ghi dữ liệu vào biểu đồ"):
    time_str = datetime.now(tz_vietnam).strftime("%H:%M:%S")
    point_idx = len(st.session_state.current_day_records) + 1
    display_axis = f"#{point_idx} ({time_str})"
    new_record = {
        "Mốc thời gian": display_axis,
        "Giờ gốc": time_str,
        "Nhịp tim (BPM)": int(bpm),
        "Chỉ số HRV (ms)": int(hrv)
    }
    st.session_state.current_day_records.append(new_record)

st.sidebar.markdown("---")
current_date_string = st.session_state.simulated_date.strftime("%d/%m/%Y")
st.sidebar.info(f"Ngày mô phỏng hiện tại: {current_date_string}")

# NÚT QUA NGÀY MỚI
if st.sidebar.button("Qua ngày mới"):
    if len(st.session_state.current_day_records) > 0:
        df_temp = pd.DataFrame(st.session_state.current_day_records)
        avg_bpm = int(df_temp["Nhịp tim (BPM)"].mean())
        avg_hrv = int(df_temp["Chỉ số HRV (ms)"].mean())
        day_mana = int((avg_hrv / safe_base) * 100)
        
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
            
        summary_record = {
            "Ngày": st.session_state.simulated_date.strftime("%d/%m/%Y"),
            "Nhịp tim trung bình": avg_bpm,
            "HRV trung bình": avg_hrv,
            "Trạng thái tổng quan": day_status
        }
        st.session_state.daily_summary_history.append(summary_record)
    else:
        summary_record = {
            "Ngày": st.session_state.simulated_date.strftime("%d/%m/%Y"),
            "Nhịp tim trung bình": 75,
            "HRV trung bình": int(base_hrv),
            "Trạng thái tổng quan": "Khỏe mạnh ổn định"
        }
        st.session_state.daily_summary_history.append(summary_record)
        st.session_state.auto_days_overloaded = 0

    st.session_state.current_day_records = []
    st.session_state.simulated_date += timedelta(days=1)
    st.rerun()

# --- 2. METRICS DISPLAY ---
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.metric(label="💓 Nhịp tim hiện tại", value=f"{bpm} BPM")
with col_m2:
    st.metric

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

st.set_page_config(page_title="SynapseCare Dashboard", layout="wide")

st.title("🧠 SynapseCare – Hệ thống theo dõi stress sinh lý học đường")
st.subheader("Giải pháp phân tích dữ liệu sinh học dựa trên chỉ số BPM và HRV dành cho Gen Z")
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

# --- THUẬT TOÁN CHẨN ĐOÁN TOÀN DIỆN MỚI ---
is_critical_tachycardia = bpm >= 140  # Nhịp tim quá cao cực kỳ nguy hiểm
is_bradycardia_exhaustion = (bpm < 60 and mana < 50)  # Nhịp tim thấp + Mana thấp = Suy nhược/Sập nguồn
is_deep_focus = (bpm < 60 and mana >= 50)  # Nhịp tim thấp + Mana cao = Tập trung đỉnh cao/Thiền

is_panic = (bpm > 100 and hrv < 30) and not is_critical_tachycardia
is_high_stress_arousal = (bpm > 100 and hrv >= 30) and not is_critical_tachycardia
is_burnout = (mana < 35) and not is_panic and not is_critical_tachycardia and not is_high_stress_arousal and not is_bradycardia_exhaustion
is_overload = (35 <= mana < 65) and not is_panic and not is_critical_tachycardia and not is_high_stress_arousal and not is_bradycardia_exhaustion

# NÚT GHI DỮ LIỆU
if st.sidebar.button("Ghi dữ liệu vào biểu đồ"):
    time_str = datetime.now(tz_vietnam).strftime("%H:%M:%S")
    point_idx = len(st.session_state.current_day_records) + 1
    display_axis = f"#{point_idx} ({time_str})"
    new_record = {
        "Time": display_axis,
        "RawTime": time_str,
        "BPM": int(bpm),
        "HRV": int(hrv)
    }
    st.session_state.current_day_records.append(new_record)

st.sidebar.markdown("---")
current_date_string = st.session_state.simulated_date.strftime("%d/%m/%Y")
st.sidebar.info(f"Ngày mô phỏng hiện tại: {current_date_string}")

# NÚT QUA NGÀY MỚI
if st.sidebar.button("Qua ngày mới"):
    current_day_df = pd.DataFrame(st.session_state.current_day_records) if len(st.session_state.current_day_records) > 0 else pd.DataFrame()
    
    if not current_day_df.empty:
        avg_bpm = int(current_day_df["BPM"].mean())
        avg_hrv = int(current_day_df["HRV"].mean())
        day_mana = int((avg_hrv / safe_base) * 100)
        
        if avg_bpm >= 140:
            day_status = "Nguy hiểm (Nhịp tim quá cao)"
            st.session_state.auto_days_overloaded += 1
        elif avg_bpm < 60 and day_mana < 50:
            day_status = "Suy nhược sập nguồn"
            st.session_state.auto_days_overloaded += 1
        elif avg_bpm > 100 and avg_hrv < 30:
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
            "Trạng thái tổng quan": day_status,
            "DetailData": current_day_df
        }
        st.session_state.daily_summary_history.append(summary_record)
    else:
        dummy_time = "08:00:00"
        dummy_df = pd.DataFrame([{"Time": f"#1 ({dummy_time})", "RawTime": dummy_time, "BPM": 75, "HRV": int(base_hrv)}])
        summary_record = {
            "Ngày": st.session_state.simulated_date.strftime("%d/%m/%Y"),
            "Nhịp tim trung bình": 75,
            "HRV trung bình": int(base_hrv),
            "Trạng thái tổng quan": "Khỏe mạnh ổn định",
            "DetailData": dummy_df
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
    st.metric(label="📊 Chỉ số HRV (Chống Stress)", value=f"{hrv} ms")
with col_m3:
    st.write("**🎮 Thanh Mana Não Bộ:**")
    st.progress(float(mana / 100.0))
    st.write(f"Mức năng lượng: {mana}%")

st.markdown("---")

# --- 3. MAIN COLUMNS ---
col_left, col_right = st.columns(2)

# ĐỊNH NGHĨA NỘI DUNG HIỂN THỊ THEO THUẬT TOÁN MỚI
if is_critical_tachycardia:
    status = "🚨 BÁO ĐỘNG ĐỎ: NHỊP TIM ĐẠT NGƯỠNG NGUY HIỂM LÂM SÀNG"
    action = "CẢNH BÁO: Nhịp tim vượt mức 140 BPM khi đang ngồi yên! Có nguy cơ sốc phản vệ, ngộ độc chất kích thích (Caffeine quá liều) hoặc hoảng loạn nặng. Yêu cầu dừng mọi hoạt động, thông báo ngay cho y tế trường học!"
elif is_bradycardia_exhaustion:
    status = "❌❌ CẢNH BÁO LÂM SÀNG: CƠ THỂ SUY NHƯỢC, SẬP NGUỒN"
    action = "Nhịp tim tụt dưới 60 BPM đi kèm năng lượng não bộ suy kiệt. Đây là trạng thái sập nguồn sinh học do kiệt sức, thiếu ngủ trầm trọng hoặc hạ đường huyết. Đề xuất: Dừng học ngay lập tức, uống nước ấm/sữa và đi ngủ nghỉ ngơi để bảo vệ tim mạch!"
elif is_deep_focus:
    status = "🧘‍♂️ TRẠNG THÁI FLOW - TẬP TRUNG SÂU ĐỈNH CAO"
    action = "Tuyệt vời! Nhịp tim thấp ổn định đi kèm chỉ số phục hồi HRV cao chứng minh cơ thể học sinh đang cực kỳ bình thản, bước vào trạng thái 'Flow' (Thiền định học đường). Đây là thời điểm vàng để tiếp thu các kiến thức khó nhất!"
elif is_panic:
    status = "🚨 NGUY CƠ HOẢNG LOẠN (Phòng thi/Áp lực cực độ)"
    action = "Kích hoạt chế độ Anti-Choke: Rung thiết bị theo nhịp thở 4-7-8 để điều hòa tim mạch ngay lập tức!"
elif is_high_stress_arousal:
    status = "⚠️ CẢNH BÁO: STRESS KÍCH THÍCH CAO (Tim quá tải)"
    action = "Dù chỉ số HRV phục hồi tốt, nhưng nhịp tim cao (>100 BPM) cho thấy cơ thể đang phải gồng mình chịu áp lực lớn để tập trung. Đề xuất: Uống một ngụm nước, thả lỏng vai và điều hòa lại nhịp độ học tập."
elif is_burnout:
    status

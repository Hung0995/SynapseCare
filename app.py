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
    st.metric(label="📊 Chỉ số HRV (Chống Stress)", value=f"{hrv} ms")
with col_m3:
    st.write("**🎮 Thanh Mana Não Bộ:**")
    st.progress(float(mana / 100.0))
    st.write(f"Mức năng lượng: {mana}%")

st.markdown("---")

# --- 3. MAIN COLUMNS ---
col_left, col_right = st.columns(2)

if is_panic:
    status = "🚨 NGUY CƠ HOẢNG LOẠN (Phòng thi/Áp lực cực độ)"
    action = "Kích hoạt chế độ Anti-Choke: Rung thiết bị theo nhịp thở 4-7-8 để điều hòa tim mạch ngay lập tức!"
elif is_burnout:
    status = "❌ KIỆT QUỆ NĂNG LƯỢNG SINH HỌC (Burnout)"
    action = "Báo động Đỏ! Khóa đồng hồ đếm giờ học. Đề xuất: Đi bộ thả lỏng 15p hoặc nghe nhạc Lo-Fi chữa lành."
elif is_overload:
    status = "⚠️ QUÁ TẢI NHẸ (Mất tập trung)"
    action = "Hiệu suất não bộ giảm 40%. Đề xuất: Nghỉ Pomodoro 5 phút, uống nước hoặc đổi sang vận động nhẹ."
else:
    status = "✅ TRẠNG THÁI VÀNG (Peak Performance)"
    action = "Não bộ đang ở trạng thái tối ưu nhất. Thích hợp để học các môn tư duy cao hoặc cày đề khó!"

# CỘT TRÁI: BIỂU ĐỒ (ĐỘ NHẠY CAO & CẮT GIÂY TRONG NHẬT KÝ)
with col_left:
    st.subheader("📈 Biểu đồ dữ liệu giám sát hôm nay")
    tab_bpm, tab_hrv, tab_data = st.tabs(["💓 Nhịp tim", "📊 Chỉ số HRV", "📋 Nhật ký hôm nay"])
    
    if len(st.session_state.current_day_records) > 0:
        st.write(f"📅 Mốc ngày hiện tại của chu kỳ: **{current_date_string}**")
        df_current = pd.DataFrame(st.session_state.current_day_records)
        
        with tab_bpm:
            st.line_chart(data=df_current, x="Mốc thời gian", y="Nhịp tim (BPM)")
        with tab_hrv:
            st.line_chart(data=df_current, x="Mốc thời gian", y="Chỉ số HRV (ms)")
        with tab_data:
            df_display = df_current.copy()
            df_display["Thời gian"] = df_display["Giờ gốc"].apply(lambda x: str(x)[:-3])
            df_display = df_display[["Thời gian", "Nhịp tim (BPM)", "Chỉ số HRV (ms)"]]
            st.dataframe(df_display, use_container_width=True)
    else:
        empty_msg = "🔄 Chu kỳ ngày mới trống. Hãy bấm nút 'Ghi dữ liệu vào biểu đồ' ở thanh bên để nạp dữ liệu sinh học."
        with tab_bpm: st.info(empty_msg)
        with tab_hrv: st.info(empty_msg)
        with tab_data: st.info(empty_msg)

# CỘT PHẢI: AI DIAGNOSIS
with col_right:
    st.subheader("🤖 Chẩn đoán từ AI")
    st.info(f"Học sinh: {student_name}")
    if is_panic or is_burnout:
        st.error(f"{status}\n\n{action}")
    elif is_overload:
        st.warning(f"{status}\n\n{action}")
    else:
        st.success(f"{status}\n\n{action}")
        
    st.markdown("---")
    with st.expander("🗂️ Bấm để mở Kho lưu trữ dữ liệu tổng hợp các ngày trước"):
        if len(st.session_state.daily_summary_history) > 0:
            df_history = pd.DataFrame(st.session_state.daily_summary_history)
            st.write("📋 **Bảng tổng hợp sức khỏe theo từng ngày:**")
            st.dataframe(df_history, use_container_width=True)
        else:
            st.write("Chưa có lịch sử lưu trữ của ngày cũ. Hãy bấm 'Qua ngày mới' để bắt đầu tích lũy.")

# --- 4. PARENT CORNER ---
st.markdown("---")
st.subheader("👨‍👩‍👧‍👦 Góc dành cho Phụ huynh & Nhà trường (Tính năng Đa năng)")

days_overloaded = st.session_state.auto_days_overloaded
st.metric(label="Tổng số ngày quá tải liên tục tích lũy qua các chu kỳ ngày", value=f"{days_overloaded} Ngày")

val_progress = min(1.0, float(days_overloaded / 4.0)) if days_overloaded > 0 else 0.0
st.progress(val_progress)

if days_overloaded == 0:
    st.info("Trạng thái: An toàn - Chưa ghi nhận ngày quá tải nào.")
elif 1 <= days_overloaded <= 2:
    st.success("Trạng thái: Xanh lá (1-2 ngày) - Áp lực tích tụ mức độ nhẹ.")
elif days_overloaded == 3:
    st.warning("Trạng thái: Vàng (3 ngày) - Ngưỡng báo động cần chú ý giảm tải.")
else:
    st.error("Trạng thái: Đỏ (Từ 4 ngày trở lên) - Nguy hiểm! Cơ thể học sinh kiệt quệ kéo dài qua nhiều ngày.")

if days_overloaded >= 3:
    st.error("📋 BÁO CÁO Y TẾ TỰ ĐỘNG GỬI PHỤ HUYNH")
    st.write(f"- Học sinh: {student_name}")
    st.write("- Phân tích: Thiết bị đeo ghi nhận chỉ số phục hồi sức khỏe liên tục suy sụp qua các ngày.")
    st.write("- Kết luận: Đây là biểu hiện suy nhược cơ thể khách quan dựa trên số liệu y sinh.")
    st.write("- Khuyến nghị: Gia đình cần giảm 30% khối lượng học tập để tránh nguy cơ suy sụp tâm thần.")
else:
    st.success("📋 Tình trạng sức khỏe tuần này: Thể trạng học sinh ở mức ổn định, các chỉ số đạt chuẩn phục hồi.")

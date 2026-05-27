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
    time_str = st.session_state.simulated_date.strftime("%H:%M:%S")
    new_record = {
        "Giờ": time_str,
        "Nhịp tim (BPM)": int(bpm),
        "Chỉ số HRV (ms)": int(hrv)
    }
    st.session_state.current_day_records.append(new_record)

st.sidebar.markdown("---")
st.sidebar.subheader("📅 Chức năng mô phỏng Chu kỳ Ngày")
# Tách biệt hiển thị chuỗi ngày ra khỏi mã xử lý đồ thị để tránh lỗi NameError
current_date_string = st.session_state.simulated_date.strftime("%d/%m/%Y")
st.sidebar.info("Ngày mô phỏng hiện tại: " + str(current_date_string))

# NÚT 2: QUA NGÀY MỚI - TỔNG HỢP VÀ RESET
if st.sidebar.button("Qua ngày mới ➡️ (Tổng hợp & Reset)"):
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

# --- 2. KHU VỰC HIỂN THỊ CÁC CHỈ SỐ Ở GIỮA (Cố định tuyệt đối) ---
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.metric(label="💓 Nhịp tim hiện tại", value=str(bpm) + " BPM")
with col_m2:
    st.metric(label="📊 Chỉ số HRV (Khả năng chống Stress)", value=str(hrv) + " ms")
with col_m3:
    st.write("**🎮 Thanh Mana Não Bộ (Năng lượng Thần kinh):**")
    st.progress(float(mana / 100.0))
    st.write("Mức năng lượng: " + str(mana) + "%")

st.markdown("---")

# --- 3. PHÂN CHIA HAI CỘT TRÁI - PHẢI ---
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

# CỘT BÊN TRÁI: BIỂU ĐỒ CHI TIẾT
with col_left:
    st.subheader("📈 Biểu đồ dữ liệu giám sát hôm nay")
    st.write("Mốc ngày hiện tại hệ thống: " + str(current_date_string))
    tab_bpm, tab_hrv, tab_data = st.tabs(["💓 Nhịp tim", "📊 Chỉ số HRV", "📋 Nhật ký hôm nay"])
    
    if len(st.session_state.current_day_records) > 0:
        df_current = pd.DataFrame(st.session_state.current_day_records)
        with tab_bpm:
            st.line_chart(data=df_current, x="Giờ", y="Nhịp tim (BPM)")
        with tab_hrv:
            st.line_chart(data=df_current, x="Giờ", y="Chỉ số HRV (ms)")
        with tab_data:
            st.dataframe(df_current, use_container_width=True)
    else:
        empty_msg = "Chưa có dữ liệu mới cho ngày hôm nay. Hãy bấm nút 'Ghi dữ liệu' ở sidebar để theo dõi."
        with tab_bpm: st.write(empty_msg)
        with tab_hrv: st.write(empty_msg)
        with tab_data: st.write(empty_msg)

# CỘT BÊN PHẢI: AI CHẨN ĐOÁN & KHO LƯU TRỮ ẨN
with col_right:
    st.subheader("🤖 Chẩn đoán từ AI")
    st.info("Học sinh: " + str(student_name))
    if is_panic or is_burnout:
        st.error(status + "\n\n" + action)
    elif is_overload:
        st.warning(status + "\n\n" + action)
    else:
        st.success(status + "\n\n" + action)
        
    st.markdown("---")
    with st.expander("🗂️ Bấm để mở Kho lưu trữ dữ liệu tổng hợp các ngày trước"):
        if len(st.session_state.daily_summary_history) > 0:
            df_history = pd.DataFrame(st.session_state.daily_summary_history)
            st.write("📋 **Bảng tổng hợp sức khỏe theo từng ngày:**")
            st.dataframe(df_history, use_container_width=True)
        else:
            st.write("Chưa có lịch sử lưu trữ của ngày cũ. Hãy bấm 'Qua ngày mới' để bắt đầu tích lũy.")

# --- 4. GÓC PHỤ HUYNH DƯỚI CÙNG ---
st.markdown("---")
st.subheader("👨‍👩‍👧‍👦 Góc dành cho Phụ huynh & Nhà trường (Tính năng Đa năng)")

days_overloaded = st.session_state.auto_days_overloaded

st.metric(label="Tổng số ngày quá tải liên tục tích lũy qua các chu kỳ ngày", value=str(days_overloaded) + " Ngày")

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
    st.write("- Học sinh: " + str(student_name))
    st.write("- Phân tích: Thiết bị đeo ghi nhận chỉ số phục hồi sức khỏe liên tục suy sụp qua các ngày.")
    st.write("- Kết luận: Đây là biểu hiện suy nhược cơ thể khách quan dựa trên số liệu y sinh.")
    st.write("- Khuyến nghị: Gia đình cần giảm 30% khối lượng học tập để tránh nguy cơ suy sụp tâm thần.")
else:
    st.success("📋 Tình trạng sức khỏe tuần này: Thể trạng học sinh ở mức ổn định, các chỉ số đạt chuẩn phục hồi.")

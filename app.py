import streamlit as st
import pandas as pd

st.set_page_config(page_title="SynapseCare Dashboard", layout="wide")

st.title("🧠 SynapseCare - Hệ Thống Tối Ưu Hiệu Suất & Thể Trạng Học Đường")
st.subheader("Trợ lý AI phân tích sinh học và quản lý Stress dành cho Gen Z")
st.markdown("---")

if 'bpm_history' not in st.session_state:
    st.session_state.bpm_history = []
if 'hrv_history' not in st.session_state:
    st.session_state.hrv_history = []
if 'auto_days_overloaded' not in st.session_state:
    st.session_state.auto_days_overloaded = 0

st.sidebar.header("⚙️ Giả lập tín hiệu Vòng đeo tay")
student_name = st.sidebar.text_input("Tên học sinh:", "Nguyễn Văn A")

# 1. Người dùng chọn HRV nền (Gốc tọa độ thể trạng của học sinh)
base_hrv = st.sidebar.slider("Chỉ số HRV nền (Lúc khỏe mạnh):", 40, 100, 65)

st.sidebar.markdown("---")
st.sidebar.write("👉 Chọn trạng thái nhanh dưới đây (Các chỉ số bên dưới sẽ tự biến đổi theo HRV nền):")
sim_state = st.sidebar.selectbox("Chọn trạng thái nhanh:", ["Bình thường", "Cày đề quá tải", "Áp lực phòng thi"])

# 2. Xử lý logic biến đổi động: Chỉ số thực tế phụ thuộc trực tiếp vào base_hrv
if sim_state == "Bình thường":
    # HRV thực tế đạt mức tối ưu (xấp xỉ bằng hoặc cao hơn HRV nền một chút)
    calc_bpm = 75
    calc_hrv = int(base_hrv * 1.0)
elif sim_state == "Cày đề quá tải":
    # HRV thực tế tụt xuống mức 50% so với thể trạng nền
    calc_bpm = 95
    calc_hrv = int(base_hrv * 0.5)
else:
    # Áp lực phòng thi cực độ: HRV tụt dốc không phanh xuống mức 20% so với nền
    calc_bpm = 120
    calc_hrv = int(base_hrv * 0.2)

# Giới hạn cận trên và dưới của HRV để tránh lỗi toán học
calc_hrv = max(10, min(100, calc_hrv))

# 3. Hiển thị thanh trượt ở chế độ xem kết quả tính toán động
bpm = st.sidebar.slider("Nhịp tim thực tế (BPM):", 40, 160, calc_bpm)
hrv = st.sidebar.slider("Biến thiên nhịp tim (HRV):", 10, 100, calc_hrv)

hrv_ratio = hrv / base_hrv
mana = int(max(0, min(100, hrv_ratio * 100)))

is_panic = bpm > 100 and hrv < 30
is_burnout = mana < 35 and not is_panic
is_overload = 35 <= mana < 65 and not is_panic

if st.sidebar.button("Ghi dữ liệu vào biểu đồ 📊"):
    st.session_state.bpm_history.append(bpm)
    st.session_state.hrv_history.append(hrv)
    if len(st.session_state.bpm_history) > 10:
        st.session_state.bpm_history.pop(0)
        st.session_state.hrv_history.pop(0)
        
    if is_panic or is_burnout or is_overload:
        st.session_state.auto_days_overloaded += 1
    elif bpm <= 80 and hrv >= 60:
        st.session_state.auto_days_overloaded = 0

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

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="💓 Nhịp tim hiện tại", value=str(bpm) + " BPM")
with col2:
    st.metric(label="📊 Chỉ số HRV (Khả năng chống Stress)", value=str(hrv) + " ms")
with col3:
    st.write("**🎮 Thanh Mana Não Bộ (Năng lượng Thần kinh):**")
    st.progress(float(mana / 100.0))
    st.write("Mức năng lượng: " + str(mana) + "%")

st.markdown("---")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📈 Biểu đồ giám sát sức khỏe")
    tab_bpm, tab_hrv = st.tabs(["💓 Nhịp tim (BPM)", "📊 Khả năng chống Stress (HRV)"])
    
    with tab_bpm:
        if len(st.session_state.bpm_history) > 0:
            df_bpm = pd.DataFrame(st.session_state.bpm_history, columns=["Nhịp tim"])
            st.line_chart(df_bpm)
        else:
            st.write("Chưa có dữ liệu. Hãy bấm 'Ghi dữ liệu vào biểu đồ' ở thanh bên cạnh.")
        
    with tab_hrv:
        if len(st.session_state.hrv_history) > 0:
            df_hrv = pd.DataFrame(st.session_state.hrv_history, columns=["Chỉ số HRV"])
            st.line_chart(df_hrv)
        else:
            st.write("Chưa có dữ liệu. Hãy bấm 'Ghi dữ liệu vào biểu đồ' ở thanh bên cạnh.")

with col_right:
    st.subheader("🤖 Chẩn đoán từ AI")
    st.info("Học sinh: " + str(student_name))
    if is_panic or is_burnout:
        st.error(status + "\n\n" + action)
    elif is_overload:
        st.warning(status + "\n\n" + action)
    else:
        st.success(status + "\n\n" + action)

# --- GÓC PHỤ HUYNH CHỐNG LỖI DỊCH THUẬT VÀ TĂNG TIẾN VÔ HẠN ---
st.markdown("---")
st.subheader("👨‍👩‍👧‍👦 Góc dành cho Phụ huynh & Nhà trường (Tính năng Đa năng)")

days_overloaded = st.session_state.auto_days_overloaded

st.metric(label="Tổng số ngày quá tải liên tục ghi nhận từ thiết bị", value=str(days_overloaded) + " Ngày")

val_progress = min(1.0, float(days_overloaded / 4.0)) if days_overloaded > 0 else 0.0
st.progress(val_progress)

if days_overloaded == 0:
    st.info("Trạng thái: An toàn - Chưa ghi nhận ngày quá tải nào.")
elif 1 <= days_overloaded <= 2:
    st.success("Trạng thái: Xanh lá (1-2 ngày) - Áp lực tích tụ mức độ nhẹ.")
elif days_overloaded == 3:
    st.warning("Trạng thái: Vàng (3 ngày) - Ngưỡng báo động cần chú ý giảm tải.")
else:
    st.error("Trạng thái: Đỏ (Từ 4 ngày trở lên) - Nguy hiểm! Cơ thể kiệt quệ kéo dài.")

if days_overloaded >= 3:
    st.error("📋 BÁO CÁO Y TẾ TỰ ĐỘNG GỬI PHỤ HUYNH")
    st.write("- Học sinh: " + str(student_name))
    st.write("- Phân tích: Chỉ số phục hồi thần kinh (HRV) liên tục dưới ngưỡng an toàn nhiều ngày qua.")
    st.write("- Kết luận: Đây là biểu hiện suy nhược cơ thể khách quan dựa trên số liệu y sinh.")
    st.write("- Khuyến nghị: Gia đình cần giảm 30% khối lượng học tập để tránh nguy cơ suy sụp tâm thần.")
else:
    st.success("📋 Tình trạng sức khỏe tuần này: Thể trạng học sinh ở mức ổn định, các chỉ số đạt chuẩn phục hồi.")

import streamlit as st
import plotly.graph_objects as go

# Cấu hình trang web hiển thị
st.set_page_config(page_title="SynapseCare Dashboard", layout="wide")

st.title("🧠 SynapseCare - Hệ Thống Tối Ưu Hiệu Suất & Thể Trạng Học Đường")
st.subheader("Trợ lý AI phân tích sinh học và quản lý Stress dành cho Gen Z")
st.markdown("---")

# Khởi tạo dữ liệu mẫu nếu chưa có
if 'bpm_history' not in st.session_state:
  
    st.session_state.bpm_history = []
if 'hrv_history' not in st.session_state:
   
    st.session_state.hrv_history = []

# --- THANH ĐIỀU KHIỂN BÊN TRÁI (SIDEBAR) ---
st.sidebar.header("⚙️ Giả lập tín hiệu Vòng đeo tay")
student_name = st.sidebar.text_input("Tên học sinh:", "Nguyễn Văn A")
base_hrv = st.sidebar.slider("Chỉ số HRV nền (Lúc khỏe mạnh):", 50, 90, 60)

st.sidebar.markdown("---")
st.sidebar.write("👉 *Kéo các thanh dưới đây để giả lập trạng thái của học sinh trước Ban giám khảo:*")
sim_state = st.sidebar.selectbox("Chọn trạng thái nhanh:", ["Bình thường", "Cày đề quá tải", "Áp lực phòng thi"])

if sim_state == "Bình thường":
    bpm = st.sidebar.slider("Nhịp tim thực tế (BPM):", 60, 100, 75)
    hrv = st.sidebar.slider("Biến thiên nhịp tim (HRV):", 40, 100, 70)
elif sim_state == "Cày đề quá tải":
    bpm = st.sidebar.slider("Nhịp tim thực tế (BPM):", 80, 120, 95)
    hrv = st.sidebar.slider("Biến thiên nhịp tim (HRV):", 20, 60, 35)
else:
    bpm = st.sidebar.slider("Nhịp tim thực tế (BPM):", 90, 160, 120)
    hrv = st.sidebar.slider("Biến thiên nhịp tim (HRV):", 5, 40, 15)

# Cập nhật lịch sử biểu đồ
if st.sidebar.button("Cập nhật dữ liệu thời gian thực 🔄"):
    st.session_state.bpm_history.append(bpm)
    st.session_state.hrv_history.append(hrv)
    if len(st.session_state.bpm_history) > 10:
        st.session_state.bpm_history.pop(0)
        st.session_state.hrv_history.pop(0)

# --- THUẬT TOÁN AI PHÂN TÍCH ---
hrv_ratio = hrv / base_hrv
mana = int(max(0, min(100, hrv_ratio * 100)))

if bpm > 100 and hrv < 30:
    status = "🚨 NGUY CƠ HOẢNG LOẠN (Phòng thi/Áp lực cực độ)"
    action = "Kích hoạt chế độ **'Anti-Choke'**: Rung thiết bị theo nhịp thở 4-7-8 để điều hòa tim mạch ngay lập tức!"
elif mana < 35:
    status = "❌ KIỆT QUỆ NĂNG LƯỢNG SINH HỌC (Burnout)"
    action = "Báo động Đỏ! Khóa đồng hồ đếm giờ học. Đề xuất: Đi bộ thả lỏng 15p hoặc nghe nhạc Lo-Fi chữa lành."
elif 35 <= mana < 65:
    status = "⚠️ QUÁ TẢI NHẸ (Mất tập trung)"
    action = "Hiệu suất não bộ giảm 40%. Đề xuất: Nghỉ Pomodoro 5 phút, uống nước hoặc đổi sang vận động nhẹ."
else:
    status = "✅ TRẠNG THÁI VÀNG (Peak Performance)"
    action = "Não bộ đang ở trạng thái tối ưu nhất. Thích hợp để học các môn tư duy cao hoặc cày đề khó!"

# --- HIỂN THỊ GIAO DIỆN CHÍNH ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="💓 Nhịp tim hiện tại", value=f"{bpm} BPM")
with col2:
    st.metric(label="📊 Chỉ số HRV (Mức độ Stress)", value=f"{hrv} ms")
with col3:
    st.write("**🎮 Thanh Mana Não Bộ (Năng lượng Thần kinh):**")
    st.progress(mana / 100)
    st.write(f"Mức năng lượng: **{mana}%**")

st.markdown("---")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📈 Biểu đồ giám sát sức khỏe thời gian thực")
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=st.session_state.bpm_history, mode='lines+markers', name='Nhịp tim (BPM)', line=dict(color='firebrick', width=3)))
    fig.add_trace(go.Scatter(y=st.session_state.hrv_history, mode='lines+markers', name='Stress (HRV)', line=dict(color='royalblue', width=3)))
    fig.update_layout(title='Xu hướng thể trạng trong phiên học tập', xaxis_title='Lần cập nhật mẫu', yaxis_title='Giá trị chỉ số')
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("🤖 Chẩn đoán từ AI")
    st.info(f"**Học sinh:** {student_name}")
    st.warning(f"**Trạng thái hệ thần kinh:**\n\n{status}")
    st.success(f"**Chỉ định hành động:**\n\n{action}")

st.markdown("---")
st.subheader("👨‍👩‍👧‍👦 Góc dành cho Phụ huynh & Nhà trường (Tính năng Đa năng)")

days_overloaded = st.slider("Giả lập số ngày học sinh bị quá tải liên tục gần đây:", 0, 7, 4)

if days_overloaded >= 3:
    st.error(f"📋 **BÁO CÁO Y TẾ TỰ ĐỘNG GỬI PHỤ HUYNH EM {student_name.upper()}**")
    st.markdown(f"""
    * **Phân tích:** Hệ thống ghi nhận chỉ số phục hồi thần kinh thực vật (HRV) của học sinh liên tục nằm dưới ngưỡng an toàn trong {days_overloaded} ngày qua. Độ ngủ sâu (Deep Sleep) giảm mạnh, cơ thể đang ở trạng thái kiệt quệ sinh học (Physical Burnout).
    * **Kết luận khoa học:** Đây là biểu hiện suy nhược cơ thể khách quan dựa trên số liệu y sinh, **không phải sự lười biếng hay viện cớ**.
    * **Khuyến nghị từ nhà trường:** Gia đình cần chủ động cắt giảm 30% khối lượng học thêm hoặc thời gian cày đêm của em để tránh nguy cơ suy sụp tâm thần đột ngột trước kỳ thi.
    """)
else:
    st.success("📋 **Tình trạng sức khỏe tuần này:** Thể trạng học sinh ở mức ổn định, các chỉ số giấc ngủ và nhịp tim nghỉ ngơi đạt chuẩn.")

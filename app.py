import streamlit as st
import plotly.graph_objects as go

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
base_hrv = st.sidebar.slider("Chỉ số HRV nền (Lúc khỏe mạnh):", 40, 100, 65)

st.sidebar.markdown("---")
st.sidebar.write("👉 *Kéo các thanh dưới đây để giả lập trạng thái của học sinh trước Ban giám khảo:*")
sim_state = st.sidebar.selectbox("Chọn trạng thái nhanh:", ["Bình thường", "Cày đề quá tải", "Áp lực phòng thi"])

if sim_state == "Bình thường":
    bpm = st.sidebar.slider("Nhịp tim thực tế (BPM):", 40, 160, 75)
    hrv = st.sidebar.slider("Biến thiên nhịp tim (HRV):", 10, 100, 70)
elif sim_state == "Cày đề quá tải":
    bpm = st.sidebar.slider("Nhịp tim thực tế (BPM):", 40, 160, 95)
    hrv = st.sidebar.slider("Biến thiên nhịp tim (HRV):", 10, 100, 35)
else:
    bpm = st.sidebar.slider("Nhịp tim thực tế (BPM):", 40, 160, 120)
    hrv = st.sidebar.slider("Biến thiên nhịp tim (HRV):", 10, 100, 15)

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
    action = "Kích hoạt chế độ **'Anti-Choke'**: Rung thiết bị theo nhịp thở 4-7-8 để điều hòa tim mạch ngay lập tức!"
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
    st.metric(label="💓 Nhịp tim hiện tại", value=f"{bpm} BPM")
with col2:
    st.metric(label="📊 Chỉ số HRV (Khả năng chống Stress)", value=f"{hrv} ms")
with col3:
    st.write("**🎮 Thanh Mana Não Bộ (Năng lượng Thần kinh):**")
    st.progress(mana / 100)
    st.write(f"Mức năng lượng: **{mana}%**")

st.markdown("---")

col_left, col_right = st.columns(2)

BPM_MIN =

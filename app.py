import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="SynapseCare Dashboard", layout="wide")

st.title("🧠 SynapseCare - Hệ Thống Tối Ưu Hiệu Suất & Thể Trạng Học Đường")
st.subheader("Trợ lý AI phân tích sinh học và quản lý Stress dành cho Gen Z")
st.markdown("---")

# Khởi tạo dữ liệu mẫu và bộ đếm ngày quá tải tự động
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

# --- THUẬT TOÁN AI PHÂN TÍCH CHẠY THỜI GIAN THỰC THỜI GIAN THỰC ---
hrv_ratio = hrv / base_hrv
mana = int(max(0, min(100, hrv_ratio * 100)))

is_panic = bpm > 100 and hrv < 30
is_burnout = mana < 35 and not is_panic
is_overload = 35 <= mana < 65 and not is_panic

# NÚT BẤM GHI DỮ LIỆU CÓ TÍCH HỢP ĐIỀU KHIỂN TỰ ĐỘNG GÓC PHỤ HUYNH
if st.sidebar.button("Ghi dữ liệu vào biểu đồ 📊"):
    st.session_state.bpm_history.append(bpm)
    st.session_state.hrv_history.append(hrv)
    if len(st.session_state.bpm_history) > 10:
        st.session_state.bpm_history.pop(0)
        st.session_state.hrv_history.pop(0)
        
    # Tự động điều khiển góc phụ huynh dựa trên phán quyết của AI
    if is_panic or is_burnout:
        # Nếu AI báo đỏ, tự động tăng thêm 1 ngày quá tải (tối đa 7 ngày)
        st.session_state.auto_days_overloaded = min(7, st.session_state.auto_days_overloaded + 1)
    elif bpm <= 80 and hrv >= 60:
        # Nếu bé bắt đầu hết stress (Nhịp tim bình thường, HRV cao), tự động reset về 0
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

BPM_MIN = 40
BPM_MAX = 160
HRV_MIN = 10
HRV_MAX = 100

with col_left:
    st.subheader("📈 Biểu đồ giám sát sức khỏe")
    tab_bpm, tab_hrv = st.tabs(["💓 Nhịp tim (BPM)", "📊 Khả năng chống Stress (HRV)"])
    
    with tab_bpm:
        fig_bpm = go.Figure()
        fig_bpm.add_trace(go.Scatter(y=st.session_state.bpm_history, mode='lines+markers', name='Nhịp tim', line=dict(color='firebrick', width=3)))
        fig_bpm.update_layout(title='Xu hướng Nhịp tim', xaxis_title='Mẫu', yaxis_title='BPM', yaxis=dict(range=[BPM_MIN, BPM_MAX]))
        st.plotly_chart(fig_bpm, use_container_width=True)
        
    with tab_hrv:
        fig_hrv = go.Figure()
        fig_hrv.add_trace(go.Scatter(y=st.session_state.hrv_history, mode='lines+markers', name='HRV', line=dict(color='royalblue', width=3)))
        fig_hrv.update_layout(title='Xu hướng HRV', xaxis_title='Mẫu', yaxis_title='ms', yaxis=dict(range=[HRV_MIN, HRV_MAX]))
        st.plotly_chart(fig_hrv, use_container_width=True)

with col_right:
    st.subheader("🤖 Chẩn đoán từ AI")
    st.info(f"**Học sinh:** {student_name}")
    if is_panic or is_burnout:
        st.error(f"**Trạng thái hệ thần kinh:**\n\n{status}\n\n**Chỉ định hành động:**\n\n{action}")
    elif is_overload:
        st.warning(f"**Trạng thái hệ thần kinh:**\n\n{status}\n\n**Chỉ định hành động:**\n\n{action}")
    else:
        st.success(f"**Trạng thái hệ thần kinh:**\n\n{status}\n\n**Chỉ định hành động:**\n\n{action}")

# --- PHẦN PHỤ HUYNH TỰ ĐỘNG HÓA THÔNG MINH ---
st.markdown("---")
st.subheader("👨‍👩‍👧‍👦 Góc dành cho Phụ huynh & Nhà trường (Tính năng Đa năng)")

# Thanh trượt này bây giờ hiển thị tự động dựa trên Bộ nhớ máy, không cho gạt bằng tay nữa để tăng tính khách quan
st.slider(
    "Số ngày học sinh bị quá tải liên tục (Hệ thống tự động chấm theo biểu đồ):", 
    0, 7, 
    value=st.session_state.auto_days_overloaded,
    disabled=True
)

if st.session_state.auto_days_overloaded >= 3:
    st.error(f"📋 BÁO CÁO Y TẾ TỰ ĐỘNG GỬI PHỤ HUYNH EM {student_name.upper()}")
    st.write(f"* **Phân tích:** Chỉ số phục hồi thần kinh (HRV) liên tục dưới ngưỡng an toàn liên tiếp {st.session_state.auto_days_overloaded} ngày qua dựa trên dữ liệu biểu đồ.")
    st.write("* **Kết luận:** Đây là biểu hiện suy nhược cơ thể khách quan dựa trên số liệu y sinh, không phải lười biếng.")
    st.write("* **Khuyến nghị:** Gia đình cần giảm ngay 30% khối lượng học tập để tránh nguy cơ suy sụp tâm thần trước kỳ thi.")
else:
    st.success("📋 Tình trạng sức khỏe tuần này: Thể trạng học sinh ở mức ổn định, các chỉ số đạt chuẩn phục hồi. Học sinh đã giải tỏa hết stress.")

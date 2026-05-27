import streamlit as str_lbl
import plotly.graph_objects as graph_obj

str_lbl.set_page_config(page_title="SynapseCare Dashboard", layout="wide")

str_lbl.title("🧠 SynapseCare - Hệ Thống Tối Ưu Hiệu Suất & Thể Trạng Học Đường")
str_lbl.subheader("Trợ lý AI phân tích sinh học và quản lý Stress dành cho Gen Z")
str_lbl.markdown("---")

if 'bpm_history' not in str_lbl.session_state:
    str_lbl.session_state.bpm_history = []
if 'hrv_history' not in str_lbl.session_state:
    str_lbl.session_state.hrv_history = []
if 'auto_days_overloaded' not in str_lbl.session_state:
    str_lbl.session_state.auto_days_overloaded = 0

str_lbl.sidebar.header("⚙️ Giả lập tín hiệu Vòng đeo tay")
student_name = str_lbl.sidebar.text_input("Tên học sinh:", "Nguyễn Văn A")
base_hrv = str_lbl.sidebar.slider("Chỉ số HRV nền (Lúc khỏe mạnh):", 40, 100, 65)

str_lbl.sidebar.markdown("---")
str_lbl.sidebar.write("👉 Kéo các thanh dưới đây để giả lập trạng thái của học sinh:")
sim_state = str_lbl.sidebar.selectbox("Chọn trạng thái nhanh:", ["Bình thường", "Cày đề quá tải", "Áp lực phòng thi"])

if sim_state == "Bình thường":
    bpm = str_lbl.sidebar.slider("Nhịp tim thực tế (BPM):", 40, 160, 75)
    hrv = str_lbl.sidebar.slider("Biến thiên nhịp tim (HRV):", 10, 100, 70)
elif sim_state == "Cày đề quá tải":
    bpm = str_lbl.sidebar.slider("Nhịp tim thực tế (BPM):", 40, 160, 95)
    hrv = str_lbl.sidebar.slider("Biến thiên nhịp tim (HRV):", 10, 100, 35)
else:
    bpm = str_lbl.sidebar.slider("Nhịp tim thực tế (BPM):", 40, 160, 120)
    hrv = str_lbl.sidebar.slider("Biến thiên nhịp tim (HRV):", 10, 100, 15)

hrv_ratio = hrv / base_hrv
mana = int(max(0, min(100, hrv_ratio * 100)))

is_panic = bpm > 100 and hrv < 30
is_burnout = mana < 35 and not is_panic
is_overload = 35 <= mana < 65 and not is_panic

if str_lbl.sidebar.button("Ghi dữ liệu vào biểu đồ 📊"):
    str_lbl.session_state.bpm_history.append(bpm)
    str_lbl.session_state.hrv_history.append(hrv)
    if len(str_lbl.session_state.bpm_history) > 10:
        str_lbl.session_state.bpm_history.pop(0)
        str_lbl.session_state.hrv_history.pop(0)
        
    if is_panic or is_burnout or is_overload:
        str_lbl.session_state.auto_days_overloaded += 1
    elif bpm <= 80 and hrv >= 60:
        str_lbl.session_state.auto_days_overloaded = 0

if is_panic:
    status = "🚨 NGUY CƠ HOẢNG LOẠN (Phòng thi/Áp lực cực độ)"
    action = "Kích hoạt chế độ Anti-Choke: Rung thiết bị theo nhịp thở 4-7-8 để điều hòa tim mạch ngay lập tức!"
elif is_burnout:
    status = "❌ KIỆT QUỆ NĂNG LƯỢNG SINH HỌC (Burnout)"
    action = "Báo động Đỏ! Khóa đồng hồ đếm giờ học. Đề xuất: Đi bộ thả lỏng 15p hoặc nghe nhạc Lo-Fi chữa lành."

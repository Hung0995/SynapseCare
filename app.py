import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

st.set_page_config(page_title="SynapseCare Dashboard", layout="wide")

st.title("🧠 SynapseCare – Hệ thống theo dõi stress sinh lý học đường dựa trên BPM và HRV")
st.subheader("Giải pháp phân tích dữ liệu sinh học dựa trên chỉ số BPM và HRV dành cho Gen Z")
st.markdown("---")

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
        "Time": display_axis,
        "RawTime": time_str,
        "BPM": int(bpm),
        "HRV": int(hrv)
    }
    st.session_state.current_day_records.append(new_record)

st.sidebar.markdown("---")
current_date_string = st.session_state.simulated_date.strftime("%d/%m/%Y")
st.sidebar.info(f"Ngày mô phỏng hiện tại: {current_date_string}")

# NÚT QUA NGÀY MỚI (Bảo vệ cấu trúc DetailData an toàn)
if st.sidebar.button("Qua ngày mới"):
    current_day_df = pd.DataFrame(st.session_state.current_day_records) if len(st.session_state.current_day_records) > 0 else pd.DataFrame()
    
    if not current_day_df.empty:
        avg_bpm = int(current_day_df["BPM"].mean())
        avg_hrv = int(current_day_df["HRV"].mean())
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
            "Trạng thái tổng quan": day_status,
            "DetailData": current_day_df
        }
        st.session_state.daily_summary_history.append(summary_record)
    else:
        # Tạo dữ liệu nền tượng trưng nếu ngày đó học sinh không ghi điểm nào, tránh lỗi trống biểu đồ lịch sử
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

# CỘT TRÁI: BIỂU ĐỒ & NHẬT KÝ HÔM NAY
with col_left:
    st.subheader("📈 Biểu đồ dữ liệu giám sát hôm nay")
    tab_bpm, tab_hrv, tab_data = st.tabs(["💓 Nhịp tim", "📊 Chỉ số HRV", "📋 Nhật ký hôm nay"])
    
    if len(st.session_state.current_day_records) > 0:
        st.write(f"📅 Mốc ngày hiện tại của chu kỳ: **{current_date_string}**")
        df_current = pd.DataFrame(st.session_state.current_day_records)
        
        with tab_bpm:
            st.line_chart(data=df_current, x="Time", y="BPM")
        with tab_hrv:
            st.line_chart(data=df_current, x="Time", y="HRV")
        with tab_data:
            df_display = df_current.copy()
            df_display["Thời gian (Giờ:Phút)"] = df_display["RawTime"].apply(lambda x: str(x)[:-3])
            df_display = df_display.rename(columns={"BPM": "Nhịp tim (BPM)", "HRV": "Chỉ số HRV (ms)"})
            df_display = df_display[["Thời gian (Giờ:Phút)", "Nhịp tim (BPM)", "Chỉ số HRV (ms)"]]
            st.dataframe(df_display, use_container_width=True)
    else:
        empty_msg = "🔄 Chu kỳ ngày mới trống. Hãy bấm nút 'Ghi dữ liệu vào biểu đồ' ở thanh bên để nạp dữ liệu sinh học."
        with tab_bpm: st.info(empty_msg)
        with tab_hrv: st.info(empty_msg)
        with tab_data: st.info(empty_msg)

# CỘT PHẢI: AI DIAGNOSIS & KHO LƯU TRỮ XEM LẠI BIỂU ĐỒ AN TOÀN
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
    with st.expander("🗂️ Bấm để mở Kho lưu trữ & Xem lại biểu đồ các ngày trước", expanded=True):
        if len(st.session_state.daily_summary_history) > 0:
            df_history = pd.DataFrame(st.session_state.daily_summary_history)
            
            st.write("📋 **Bảng tổng hợp sức khỏe theo từng ngày:**")
            st.dataframe(df_history[["Ngày", "Nhịp tim trung bình", "HRV trung bình", "Trạng thái tổng quan"]], use_container_width=True)
            
            st.markdown("---")
            st.write("🔍 **Chọn một ngày để xem lại biểu đồ chi tiết của ngày đó:**")
            list_days = [item["Ngày"] for item in st.session_state.daily_summary_history]
            selected_day = st.selectbox("Chọn ngày cần xem lịch sử:", list_days)
            
            # Khử hoàn toàn lỗi KeyError bằng cách kiểm tra sự tồn tại của key "DetailData"
            selected_record = next(item for item in st.session_state.daily_summary_history if item["Ngày"] == selected_day)
            
            if "DetailData" in selected_record and isinstance(selected_record["DetailData"], pd.DataFrame):
                df_history_detail = selected_record["DetailData"]
                if not df_history_detail.empty:
                    st.write(f"📊 **Biểu đồ chi tiết ngày {selected_day}:**")
                    sub_tab_bpm, sub_tab_hrv = st.tabs(["💓 Nhịp tim lịch sử", "📊 Chỉ số HRV lịch sử"])
                    with sub_tab_bpm:
                        st.line_chart(data=df_history_detail, x="Time", y="BPM")
                    with sub_tab_hrv:
                        st.line_chart(data=df_history_detail, x="Time", y="HRV")
                else:
                    st.warning("Ngày này không có dữ liệu biểu đồ chi tiết.")
            else:
                st.warning("Dữ liệu chi tiết của ngày được chọn không khả dụng.")
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

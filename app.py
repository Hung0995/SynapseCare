with col_left:
    st.subheader("📈 Biểu đồ giám sát sức khỏe")
    
    # Tạo 2 Tab riêng biệt cho Nhịp tim và HRV
    tab_bpm, tab_hrv = st.tabs(["💓 Nhịp tim (BPM)", "📊 Khả năng chống Stress (HRV)"])
    
    with tab_bpm:
        fig_bpm = go.Figure()
        fig_bpm.add_trace(go.Scatter(
            y=st.session_state.bpm_history, 
            mode='lines+markers', 
            name='Nhịp tim (BPM)', 
            line=dict(color='firebrick', width=3)
        ))
        fig_bpm.update_layout(
            title='Xu hướng Nhịp tim trong phiên học tập', 
            xaxis_title='Lần cập nhật mẫu', 
            yaxis_title='BPM',
            yaxis=dict(range=) # Khóa trục Y theo đúng giới hạn thanh gạt
        )
        st.plotly_chart(fig_bpm, use_container_width=True)
        
    with tab_hrv:
        fig_hrv = go.Figure()
        fig_hrv.add_trace(go.Scatter(
            y=st.session_state.hrv_history, 
            mode='lines+markers', 
            name='Stress (HRV)', 
            line=dict(color='royalblue', width=3)
        ))
        fig_hrv.update_layout(
            title='Xu hướng Biến thiên nhịp tim (HRV)', 
            xaxis_title='Lần cập nhật mẫu', 
            yaxis_title='ms',
            yaxis=dict(range=) # Khóa trục Y theo đúng giới hạn thanh gạt
        )
        st.plotly_chart(fig_hrv, use_container_width=True)

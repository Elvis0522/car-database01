import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# 初始化 session_state
if 'form_data' not in st.session_state:
    st.session_state.form_data = {
        'name': '',
        'plate': '',
        'model': '',
        'year': '',
        'phone': '',
        'email': ''
    }
if 'selected_options' not in st.session_state:
    st.session_state.selected_options = []

# 頁面設定 (與Seed02相同)
# ... [保留原有設定] ...

# 資料載入與品牌篩選 (與Seed02相同)
# ... [保留原有程式碼] ...

# 主畫面
# --- 客戶資料表單 (綁定 session_state) ---
if (
    selected_brand != '所有品牌'
    and selected_model != '所有車型'
    and not df[
        (df['品牌'] == selected_brand) & (df['車型'] == selected_model)
    ].empty
):
    st.markdown("#### 🚩 客戶資料表單")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        form_date = st.date_input("日期", value=date.today(), disabled=True)
    with col2:
        name = st.text_input("姓名", value=st.session_state.form_data['name'])
    with col3:
        title = st.selectbox("稱謂", options=["先生", "小姐"], index=0, disabled=True)
    with col4:
        plate = st.text_input("車牌號碼", value=st.session_state.form_data['plate'])
    col5, col6 = st.columns(2)
    with col5:
        model_input = st.text_input("型號", value=st.session_state.form_data['model'])
    with col6:
        year = st.text_input("年份", value=st.session_state.form_data['year'])
    col7, col8 = st.columns(2)
    with col7:
        phone = st.text_input("電話", value=st.session_state.form_data['phone'])
    with col8:
        email = st.text_input("E-mail", value=st.session_state.form_data['email'])

# --- 新增重置按鈕 ---
if st.button("🔄 重置表單與選配", type='primary', use_container_width=True):
    # 清空客戶資料
    st.session_state.form_data = {
        'name': '',
        'plate': '',
        'model': '',
        'year': '',
        'phone': '',
        'email': ''
    }
    # 清空選配
    st.session_state.selected_options = []
    # 重新執行以更新畫面 (不影響品牌/車型選擇)
    st.experimental_rerun()

# 車輛規格表 (與Seed02相同)
# ... [保留原有程式碼] ...

# 選配系統 (綁定 session_state)
if not filtered_df.empty and selected_model != '所有車型':
    try:
        car_class = filtered_df.iloc[0]['巧思分類']
        st.markdown("---")
        st.markdown(f"### 🛠️ {car_class} 專屬選配")
        if car_class in pricing_df.index:
            class_prices = pricing_df.loc[car_class].dropna()
            
            # 動態生成選配 (支援狀態保留)
            for i in range(1,6):
                col1, col2 = st.columns([2,1])
                with col1:
                    opt = st.selectbox(
                        f"選配項目 {i}",
                        ["(不選購)"] + class_prices.index.tolist(),
                        key=f"opt_{i}",
                        index=0  # 預設選「不選購」
                    )
                # 重置時自動清除數量選擇
                if opt == "(不選購)":
                    st.session_state[f'qty_{i}'] = 1  # 重置數量為1
                
                if opt != "(不選購)":
                    with col2:
                        qty = st.selectbox(
                            "數量",
                            options=list(range(1, 11)),
                            key=f"qty_{i}",
                            index=0  # 預設選1
                        )
                    # 記錄選配
                    if i <= len(st.session_state.selected_options):
                        st.session_state.selected_options[i-1] = (opt, class_prices[opt], qty)
                    else:
                        st.session_state.selected_options.append((opt, class_prices[opt], qty))
                    st.markdown(f"✓ **{opt}** - NT$ {class_prices[opt]:,} × {qty}")
            
            # 顯示總價
            if st.session_state.selected_options:
                total = sum(price*qty for _, price, qty in st.session_state.selected_options)
                st.markdown(f"<div class='total-price'>總計：NT$ {total:,}</div>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"選配系統錯誤: {str(e)}")

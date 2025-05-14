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

# 頁面設定
st.set_page_config(
    page_title="巧思鍍膜管理系統",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# 樣式設定
st.markdown("""
<style>
    .total-price {
        color: #e74c3c !important;
        font-size: 32px;
        font-weight: 800;
        text-align: right;
        padding-right: 3rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    excel_path = Path(__file__).parent / "Qiao-Si-AutoJia-Mu-Biao.xlsx"
    df = pd.read_excel(excel_path, sheet_name="工作表1", engine="openpyxl")
    required_cols = ['品牌', '類型', '車型', '巧思分類', '車長(mm)', '車寬(mm)', '車高(mm)', '總價落點']
    return df[required_cols].dropna(subset=required_cols)

@st.cache_data
def load_pricing():
    excel_path = Path(__file__).parent / "Qiao-Si-AutoJia-Mu-Biao.xlsx"
    df = pd.read_excel(excel_path, sheet_name="工作表1", engine="openpyxl")
    return df[['巧思分類'] + df.columns[10:28].tolist()].drop_duplicates().set_index('巧思分類')

df = load_data()
pricing_df = load_pricing()

# 側邊欄 - 必須放在主畫面邏輯前
with st.sidebar:
    st.markdown("### 🚗 車輛篩選系統")
    
    # 品牌排序
    all_brands = df['品牌'].unique().tolist()
    sorted_brands = ['所有品牌'] + sorted(
        [b for b in all_brands if b != '0-巧思業務用'],
        key=lambda x: x.replace('0-巧思業務用', '')
    )
    if '0-巧思業務用' in all_brands:
        sorted_brands.insert(1, '0-巧思業務用')
    
    selected_brand = st.selectbox(
        "選擇品牌",
        options=sorted_brands,
        index=1 if '0-巧思業務用' in sorted_brands else 0
    )
    
    # 動態車型選項
    if selected_brand == '所有品牌':
        models = ['所有車型'] + sorted(df['車型'].unique().tolist())
    else:
        models = ['所有車型'] + sorted(df[df['品牌'] == selected_brand]['車型'].unique().tolist())
    selected_model = st.selectbox("選擇車型", models)

# 主畫面
try:
    # 安全篩選邏輯
    brand_filter = df['品牌'] == selected_brand if selected_brand != '所有品牌' else df['品牌'].notnull()
    model_filter = df['車型'] == selected_model if selected_model != '所有車型' else df['車型'].notnull()
    filtered_df = df[brand_filter & model_filter].head(5)
    
    # --- 客戶資料表單 ---
    if (
        selected_brand != '所有品牌'
        and selected_model != '所有車型'
        and not filtered_df.empty
    ):
        st.markdown("#### 🚩 客戶資料表單")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            form_date = st.date_input("日期", value=date.today(), disabled=True)
        with col2:
            st.session_state.form_data['name'] = st.text_input("姓名", value=st.session_state.form_data['name'])
        with col3:
            title = st.selectbox("稱謂", options=["先生", "小姐"], index=0, disabled=True)
        with col4:
            st.session_state.form_data['plate'] = st.text_input("車牌號碼", value=st.session_state.form_data['plate'])
        col5, col6 = st.columns(2)
        with col5:
            st.session_state.form_data['model'] = st.text_input("型號", value=st.session_state.form_data['model'])
        with col6:
            st.session_state.form_data['year'] = st.text_input("年份", value=st.session_state.form_data['year'])
        col7, col8 = st.columns(2)
        with col7:
            st.session_state.form_data['phone'] = st.text_input("電話", value=st.session_state.form_data['phone'])
        with col8:
            st.session_state.form_data['email'] = st.text_input("E-mail", value=st.session_state.form_data['email'])
    
    # --- 重置按鈕 ---
    if st.button("🔄 重置表單與選配", type='primary', use_container_width=True):
        st.session_state.form_data = {key: '' for key in st.session_state.form_data}
        st.session_state.selected_options = []
        st.experimental_rerun()
    
    # --- 車輛規格表 ---
    st.markdown("### 📊 車輛規格表")
    if not filtered_df.empty:
        st.dataframe(
            filtered_df[['類型', '車型', '車長(mm)', '車寬(mm)', '車高(mm)', '總價落點']],
            height=300,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("⚠️ 沒有找到符合條件的車輛")

    # --- 選配系統 ---
    if not filtered_df.empty and selected_model != '所有車型':
        car_class = filtered_df.iloc[0]['巧思分類']
        st.markdown("---")
        st.markdown(f"### 🛠️ {car_class} 專屬選配")
        if car_class in pricing_df.index:
            class_prices = pricing_df.loc[car_class].dropna()
            
            # 動態生成選配
            for i in range(1,6):
                col_opt, col_qty = st.columns([3,1])
                with col_opt:
                    opt = st.selectbox(
                        f"選配項目 {i}",
                        ["(不選購)"] + class_prices.index.tolist(),
                        key=f"opt_{i}"
                    )
                if opt != "(不選購)":
                    with col_qty:
                        qty = st.selectbox("數量", options=range(1,11), key=f"qty_{i}")
                    st.markdown(f"✓ **{opt}** × {qty} = NT$ {class_prices[opt]*qty:,}")
            
            # 總價計算
            total = sum(
                class_prices[opt]*qty 
                for i in range(1,6) 
                if (opt := st.session_state.get(f"opt_{i}")) != "(不選購)"
                if (qty := st.session_state.get(f"qty_{i}", 1))
            )
            st.markdown(f"<div class='total-price'>總計：NT$ {total:,}</div>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"系統錯誤: {str(e)}")

import streamlit as st
import pandas as pd
from pathlib import Path

# 頁面設定
st.set_page_config(
    page_title="巧思鍍膜管理系統",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    excel_path = Path(__file__).parent / "Qiao-Si-AutoJia-Mu-Biao.xlsx"
    df = pd.read_excel(excel_path, sheet_name="工作表1", engine="openpyxl")
    required_cols = ['品牌', '車型', '巧思分類', '車長(mm)', '車寬(mm)', '車高(mm)', '總價落點']
    return df[required_cols].dropna(subset=required_cols)

@st.cache_data
def load_pricing():
    excel_path = Path(__file__).parent / "Qiao-Si-AutoJia-Mu-Biao.xlsx"
    df = pd.read_excel(excel_path, sheet_name="工作表1", engine="openpyxl")
    return df[['巧思分類'] + df.columns[10:28].tolist()].drop_duplicates().set_index('巧思分類')

# 初始化資料
df = load_data()
pricing_df = load_pricing()

# 品牌特殊排序處理 (安全版本)
all_brands = df['品牌'].unique().tolist()
sorted_brands = (
    ['所有品牌'] + 
    (['0-巧思業務用'] if '0-巧思業務用' in all_brands else []) + 
    sorted([b for b in all_brands if b != '0-巧思業務用'])
)

# 側邊欄設計 (安全版本)
with st.sidebar:
    st.markdown("### 🚗 車輛篩選系統")
    
    # 品牌選擇 (完全兼容處理)
    selected_brand = st.selectbox(
        "選擇品牌",
        options=sorted_brands,
        index=0  # 預設選中「所有品牌」
    )
    
    # 動態車型選項 (安全過濾)
    if selected_brand == '所有品牌':
        models = ['所有車型'] + sorted(df['車型'].unique().tolist())
    else:
        models = ['所有車型'] + sorted(df[df['品牌'] == selected_brand]['車型'].dropna().unique().tolist())
    
    selected_model = st.selectbox("選擇車型", models)

# 主畫面核心規格表 (安全顯示)
st.markdown("### 📊 車輛規格表")

try:
    brand_filter = df['品牌'] == selected_brand if selected_brand != '所有品牌' else df['品牌'].notnull()
    model_filter = df['車型'] == selected_model if selected_model != '所有車型' else df['車型'].notnull()
    filtered_df = df[brand_filter & model_filter]
    
    if not filtered_df.empty:
        st.dataframe(
            filtered_df[['巧思分類', '車長(mm)', '車寬(mm)', '車高(mm)', '總價落點']],
            height=300,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("⚠️ 沒有找到符合條件的車輛")
except KeyError as e:
    st.error(f"資料欄位錯誤: {str(e)}")

# 選配系統 (安全版本)
if not filtered_df.empty and selected_model != '所有車型':
    try:
        car_class = filtered_df.iloc[0]['巧思分類']
        
        if car_class in pricing_df.index:
            st.markdown("---")
            st.markdown(f"### 🛠️ {car_class} 專屬選配")
            
            class_prices = pricing_df.loc[car_class].dropna()
            
            selected = []
            for i in range(1,6):
                opt = st.selectbox(
                    f"選配項目 {i}",
                    ["(不選購)"] + class_prices.index.tolist(),
                    key=f"opt_{i}"
                )
                if opt != "(不選購)":
                    selected.append(class_prices[opt])
                    st.markdown(f"✓ **{opt}** - NT$ {class_prices[opt]:,}")
            
            if selected:
                st.markdown(f"**總計：NT$ {sum(selected):,}**")
    except Exception as e:
        st.error(f"選配系統錯誤: {str(e)}")

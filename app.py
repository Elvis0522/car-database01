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

# 安全樣式設定 (無HTML)
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
    required_cols = ['品牌', '車型', '巧思分類', '車長(mm)', '車寬(mm)', '車高(mm)', '總價落點']
    return df[required_cols].dropna(subset=required_cols)

@st.cache_data
def load_pricing():
    excel_path = Path(__file__).parent / "Qiao-Si-AutoJia-Mu-Biao.xlsx"
    df = pd.read_excel(excel_path, sheet_name="工作表1", engine="openpyxl")
    return df[['巧思分類'] + df.columns[10:28].tolist()].drop_duplicates().set_index('巧思分類')

df = load_data()
pricing_df = load_pricing()

# 品牌安全排序
all_brands = df['品牌'].unique().tolist()
sorted_brands = ['所有品牌'] + sorted(
    [b for b in all_brands if b != '0-巧思業務用'], 
    key=lambda x: x.replace('0-巧思業務用', '')  # 特殊品牌置頂
)
if '0-巧思業務用' in all_brands:
    sorted_brands.insert(1, '0-巧思業務用')

# 側邊欄設計 (完全兼容)
with st.sidebar:
    st.markdown("### 🚗 車輛篩選系統")
    
    # 品牌選擇 (純文字格式)
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

# 主畫面 (安全顯示)
st.markdown("### 📊 車輛規格表")

try:
    brand_filter = df['品牌'] == selected_brand if selected_brand != '所有品牌' else df['品牌'].notnull()
    model_filter = df['車型'] == selected_model if selected_model != '所有車型' else df['車型'].notnull()
    filtered_df = df[brand_filter & model_filter].head(5)
    
    if not filtered_df.empty:
        # 動態添加🌟標記 (不影響實際數據)
        display_df = filtered_df.copy()
        display_df['品牌'] = display_df['品牌'].apply(
            lambda x: f"🌟 {x}" if x == '0-巧思業務用' else x
        )
        
        st.dataframe(
            display_df[['品牌', '車長(mm)', '車寬(mm)', '車高(mm)', '總價落點']],
            height=300,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("⚠️ 沒有找到符合條件的車輛")
except Exception as e:
    st.error(f"資料顯示錯誤: {str(e)}")

# 選配系統 (安全計算)
if not filtered_df.empty and selected_model != '所有車型':
    try:
        car_class = filtered_df.iloc[0]['巧思分類']
        
        st.markdown("---")
        st.markdown(f"### 🛠️ {car_class} 專屬選配")
        
        if car_class in pricing_df.index:
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
                total = sum(selected)
                st.markdown(f"<div class='total-price'>總計：NT$ {total:,}</div>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"選配系統錯誤: {str(e)}")

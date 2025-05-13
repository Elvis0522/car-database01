import streamlit as st
import pandas as pd
from pathlib import Path

# 頁面設定
st.set_page_config(
    page_title="巧思汽車鍍膜規格系統",
    layout="wide",
    page_icon="✨",
    initial_sidebar_state="expanded"
)

# 自訂CSS樣式
st.markdown("""
<style>
    [data-testid=stSidebar] {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 10px;
        padding: 2rem;
    }
    .stSelectbox > div > div {
        border: 1px solid #4a4a4a;
        border-radius: 5px;
    }
    .stMarkdown h3 {
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.3rem;
    }
    /* 新增價格顯示樣式 */
    .price-total {
        color: #ff0000;
        font-weight: bold;
        text-align: right;
        margin: 1rem 0;
        padding-right: 2rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    excel_path = Path(__file__).parent / "Qiao-Si-AutoJia-Mu-Biao.xlsx"
    df = pd.read_excel(excel_path, sheet_name="工作表1", engine="openpyxl")
    df = df.dropna(subset=['品牌', '車型'])
    return df

df = load_data()

# 選配欄位與價格對照表
@st.cache_data
def get_pricing_data():
    excel_path = Path(__file__).parent / "Qiao-Si-AutoJia-Mu-Biao.xlsx"
    pricing_df = pd.read_excel(excel_path, sheet_name="工作表1", engine="openpyxl")
    option_cols = pricing_df.columns[10:28]
    return option_cols, pricing_df[['巧思分類'] + option_cols.tolist()].drop_duplicates().set_index('巧思分類')

option_cols, pricing_df = get_pricing_data()

# 側邊欄設計
with st.sidebar:
    st.markdown("### 🚗 鍍膜車輛篩選系統")
    
    # 品牌篩選
    selected_brand = st.selectbox(
        "**步驟 1：選擇品牌**",
        options=['全部品牌'] + sorted(df['品牌'].unique().tolist()),
        index=0
    )
    
    # 動態車型篩選
    if selected_brand == '全部品牌':
        model_options = ['全部車型'] + sorted(df['車型'].unique().tolist())
    else:
        model_options = ['全部車型'] + sorted(df[df['品牌'] == selected_brand]['車型'].unique().tolist())
    
    selected_model = st.selectbox(
        "**步驟 2：選擇車型**",
        options=model_options,
        index=0
    )

# 主畫面設計
st.markdown("### 📊 車輛規格查詢結果")

# 篩選邏輯與表格顯示
if selected_brand == '全部品牌':
    brand_filter = df['品牌'].notnull()
else:
    brand_filter = df['品牌'] == selected_brand

if selected_model == '全部車型':
    model_filter = df['車型'].notnull()
else:
    model_filter = df['車型'] == selected_model

filtered_df = df[brand_filter & model_filter]

# 顯示精簡表格（只顯示4列，其他自動隱藏）
if not filtered_df.empty:
    st.dataframe(
        filtered_df[["巧思分類", "車長(mm)", "車寬(mm)", "車高(mm)"]],  # 只顯示4個核心欄位
        column_config={
            "車長(mm)": st.column_config.NumberColumn(format="%d mm"),
            "車寬(mm)": st.column_config.NumberColumn(format="%d mm"),
            "車高(mm)": st.column_config.NumberColumn(format="%d mm")
        },
        use_container_width=True,
        height=300,  # 固定高度觸發滾動條
        hide_index=True
    )
else:
    st.warning("⚠️ 沒有找到符合條件的車輛，請調整篩選條件")

# --- 選配功能模組 ---
if not filtered_df.empty and selected_model != '全部車型':
    st.markdown("---")
    st.markdown("### 🛠️ 鍍膜選配加購系統")
    
    car_classification = filtered_df.iloc[0]['巧思分類']
    
    if car_classification in pricing_df.index:
        class_prices = pricing_df.loc[car_classification].dropna()
        
        selected_options = []
        for i in range(1, 6):
            option = st.selectbox(
                f"選配項目 {i}（可留空）",
                options=["不選購"] + list(class_prices.index),
                key=f"option_{i}"
            )
            if option != "不選購":
                selected_options.append((option, class_prices[option]))
        
        # 顯示價格總計（無背景色，紅色右側顯示）
        if selected_options:
            total = sum(price for _, price in selected_options)
            st.markdown(f"<div class='price-total'>選配總價：NT$ {total:,}</div>", unsafe_allow_html=True)

# 底部說明
st.markdown("---")
st.markdown("""
**操作提示**  
- 表格支援水平滾動查看完整資訊
- 選配價格即時計算，紅色字體顯示於右側
""")

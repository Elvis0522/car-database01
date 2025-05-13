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
    .price-summary {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-top: 1rem;
        border-left: 4px solid #3498db;
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
# 取得所有分類與對應價格
@st.cache_data
def get_pricing_data():
    excel_path = Path(__file__).parent / "Qiao-Si-AutoJia-Mu-Biao.xlsx"
    pricing_df = pd.read_excel(excel_path, sheet_name="工作表1", engine="openpyxl")
    # 選取巧思分類與所有選配欄位 (K-AB列)
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
    
    st.markdown("---")
    st.markdown("ℹ️ **操作說明**\n\n1. 先選擇品牌\n2. 再選擇車型\n3. 結果即時顯示")

# 主畫面設計
st.markdown("### 📊 車輛規格查詢結果")

# 篩選邏輯
if selected_brand == '全部品牌':
    brand_filter = df['品牌'].notnull()
else:
    brand_filter = df['品牌'] == selected_brand

if selected_model == '全部車型':
    model_filter = df['車型'].notnull()
else:
    model_filter = df['車型'] == selected_model

filtered_df = df[brand_filter & model_filter]

# 顯示結果表格
if not filtered_df.empty:
    # 自訂表格樣式
    st.dataframe(
        filtered_df[["巧思分類", "車長(mm)", "車寬(mm)", "車高(mm)", "總價落點"]],
        column_config={
            "總價落點": st.column_config.TextColumn(
                "鍍膜價格方案",
                help="專業級鍍膜服務價格區間（參考值）",
                width="medium"
            )
        },
        use_container_width=True,
        height=400,
        hide_index=True
    )
    
    # 顯示統計卡片
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("符合車輛數", f"{len(filtered_df)} 台")
    with col2:
        avg_length = filtered_df['車長(mm)'].mean()
        st.metric("平均車長", f"{avg_length:.1f} mm")
    with col3:
        max_width = filtered_df['車寬(mm)'].max()
        st.metric("最大車寬", f"{max_width} mm")
else:
    st.warning("⚠️ 沒有找到符合條件的車輛，請調整篩選條件")

# --- 選配功能模組 ---
if not filtered_df.empty and selected_model != '全部車型':
    st.markdown("---")
    st.markdown("### 🛠️ 鍍膜選配加購系統")
    
    # 取得該車型的巧思分類
    car_classification = filtered_df.iloc[0]['巧思分類']
    
    # 確認此分類的價格表
    if car_classification in pricing_df.index:
        # 提取價格數據 
        class_prices = pricing_df.loc[car_classification].dropna()
        
        st.markdown(f"**當前車型分類：{car_classification}**")
        
        # 顯示五個選配下拉選單
        selected_options = []
        
        for i in range(1, 6):
            option = st.selectbox(
                f"選配項目 {i}（可留空）",
                options=["不選購"] + list(class_prices.index),
                key=f"option_{i}"
            )
            
            if option != "不選購":
                price = class_prices[option]
                selected_options.append((option, price))
        
        # 計算選配總價
        total_selected_price = sum(price for _, price in selected_options)
        
        # 顯示選配明細與總價
        if selected_options:
            st.markdown("#### 選購項目明細")
            for option, price in selected_options:
                st.markdown(f"- {option}: NT$ {price:,}")
            
            st.markdown(f"""
            <div class="price-summary">
                <h4>選配總價: NT$ {total_selected_price:,}</h4>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("尚未選擇任何選配項目")
    else:
        st.warning(f"無法找到「{car_classification}」的選配價格資料")

# 底部說明
st.markdown("---")
st.markdown("""
**欄位說明**  
- **巧思分類**：車輛鍍膜難度分級
- **總價落點**：完整鍍膜服務價格參考區間（僅供參考）
- **選配項目**：依車型分類定價，可選擇0-5項
""")

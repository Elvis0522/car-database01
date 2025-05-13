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
    .price-table {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    excel_path = Path(__file__).parent / "Qiao-Si-AutoJia-Mu-Biao.xlsx"
    df = pd.read_excel(excel_path, sheet_name="工作表1", engine="openpyxl")
    df = df.dropna(subset=['品牌', '車型', '巧思分類', '總價落點'])
    return df

@st.cache_data
def load_price_data():
    excel_path = Path(__file__).parent / "Qiao-Si-AutoJia-Mu-Biao.xlsx"
    df = pd.read_excel(excel_path, sheet_name="工作表1", engine="openpyxl")
    
    # 建立價格映射表
    optional_cols = df.columns[10:28].tolist()  # K到AB欄
    price_mapping = df.set_index('巧思分類')[optional_cols].to_dict(orient='index')
    
    # 清理NaN值
    for category in price_mapping:
        price_mapping[category] = {k: v for k, v in price_mapping[category].items() if pd.notna(v)}
    
    return optional_cols, price_mapping

df = load_data()
optional_cols, price_mapping = load_price_data()

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
                help="專業級鍍膜服務價格區間",
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
        st.metric("符合車輛數", f"{len(filtered_df)} 台", help="符合當前篩選條件的車輛總數")
    with col2:
        avg_length = filtered_df['車長(mm)'].mean()
        st.metric("平均車長", f"{avg_length:.1f} mm", help="符合條件車輛的平均長度")
    with col3:
        max_width = filtered_df['車寬(mm)'].max()
        st.metric("最大車寬", f"{max_width} mm", delta_color="off", help="符合條件車輛的最大寬度")
else:
    st.warning("⚠️ 沒有找到符合條件的車輛，請調整篩選條件")

# --- 新增選配功能模組 ---
if not filtered_df.empty:
    st.markdown("---")
    st.markdown("### 🛠️ 鍍膜選配加購系統")
    
    # 取得巧思分類
    selected_classification = filtered_df.iloc[0]['巧思分類']
    
    # 顯示基本價格
    base_price = int(filtered_df.iloc[0]['總價落點'].replace('NT$','').replace(',','').split('-')[0])
    st.markdown(f"#### 基礎鍍膜方案：NT$ {base_price:,}")
    
    # 動態生成選配項目
    selected_options = []
    option_prices = {}
    
    # 顯示可選項目
    if selected_classification in price_mapping:
        available_options = price_mapping[selected_classification]
        
        # 顯示選配項目表格
        st.markdown("##### 可選配項目清單：")
        options_df = pd.DataFrame.from_dict(available_options, orient='index', columns=['價格'])
        st.dataframe(
            options_df,
            column_config={
                "價格": st.column_config.NumberColumn(
                    format="NT$ %d",
                    width="medium"
                )
            },
            use_container_width=True,
            height=200,
            hide_index=False
        )
        
        # 動態選擇
        for i in range(1, 6):
            option = st.selectbox(
                f"選配項目 {i}（可留空）",
                options=["不選購"] + list(available_options.keys()),
                key=f"option_{i}"
            )
            if option != "不選購":
                selected_options.append(option)
                option_prices[option] = available_options[option]
    
    # 計算總價
    total_price = base_price + sum(option_prices.values())
    
    # 顯示價格計算
    st.markdown("### 💰 價格計算")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"""
        <div class="price-table">
            <p>基礎鍍膜：NT$ {base_price:,}</p>
            {''.join([f'<p>+ {opt}：NT$ {price:,}</p>' for opt, price in option_prices.items()])}
            <p><strong>總計：NT$ {total_price:,}</strong></p>
        </div>
        """, unsafe_allow_html=True)

# 底部說明
st.markdown("---")
st.markdown("""
**欄位說明**  
- **巧思分類**：車輛鍍膜難度分級 (A/B/C 級)  
- **總價落點**：完整鍍膜服務價格區間 (含施工工時與材料費)
""")

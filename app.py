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

# 自訂樣式
st.markdown("""
<style>
    .special-brand {color: #2ecc71 !important; font-weight: 600;}
    .price-detail {padding: 0.5rem 1rem; background: #f8f9fa; border-radius: 8px; margin: 0.5rem 0;}
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

# 初始化資料
df = load_data()
pricing_df = load_pricing()

# 特殊品牌排序處理
all_brands = df['品牌'].unique().tolist()
sorted_brands = ['0-巧思業務用'] + sorted([b for b in all_brands if b != '0-巧思業務用'])

# 側邊欄設計
with st.sidebar:
    st.markdown("### 🚗 車輛篩選系統")
    
    # 品牌選擇 (特殊排序)
    selected_brand = st.selectbox(
        "選擇品牌",
        options=['所有品牌'] + sorted_brands,
        format_func=lambda x: f"🌟 {x}" if x == '0-巧思業務用' else x,
        index=0
    )
    
    # 動態車型選項
    if selected_brand == '所有品牌':
        models = ['所有車型'] + sorted(df['車型'].unique().tolist())
    else:
        models = ['所有車型'] + sorted(df[df['品牌'] == selected_brand]['車型'].unique().tolist())
    
    selected_model = st.selectbox("選擇車型", models)

# 主畫面
st.markdown("### 📊 核心規格表")

# 安全篩選邏輯
brand_filter = df['品牌'] == selected_brand if selected_brand != '所有品牌' else df['品牌'].notnull()
model_filter = df['車型'] == selected_model if selected_model != '所有車型' else df['車型'].notnull()
filtered_df = df[brand_filter & model_filter]

# 顯示表格 (含總價落點)
if not filtered_df.empty:
    st.dataframe(
        filtered_df[['巧思分類', '車長(mm)', '車寬(mm)', '車高(mm)', '總價落點']],
        column_config={
            "總價落點": st.column_config.TextColumn("參考價格區間", width="large")
        },
        height=250,
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("無符合條件車輛")

# 選配系統
if not filtered_df.empty and selected_model != '所有車型':
    try:
        car_class = filtered_df.iloc[0]['巧思分類']
        
        st.markdown("---")
        st.markdown(f"### 🛠️ {car_class} 專屬選配系統")
        
        if car_class in pricing_df.index:
            class_prices = pricing_df.loc[car_class].dropna()
            
            # 顯示選配項目價格表
            st.markdown("**可選項目清單：**")
            price_table = pd.DataFrame({
                "項目": class_prices.index,
                "單價": class_prices.values
            })
            st.dataframe(
                price_table,
                column_config={"單價": st.column_config.NumberColumn(format="NT$ %d")},
                hide_index=True,
                use_container_width=True,
                height=200
            )
            
            # 選配選擇
            selected = []
            for i in range(1,6):
                opt = st.selectbox(
                    f"選配項目 {i}",
                    ["(不選購)"] + class_prices.index.tolist(),
                    key=f"opt_{i}"
                )
                if opt != "(不選購)":
                    price = class_prices[opt]
                    selected.append((opt, price))
                    # 顯示單價明細
                    st.markdown(f"""
                    <div class="price-detail">
                        ✔️ 已選 {opt} - 單價 NT$ {price:,}
                    </div>
                    """, unsafe_allow_html=True)
            
            # 總價計算
            if selected:
                total = sum(p for _, p in selected)
                st.markdown(f"""
                <div style="color:#e74c3c;font-size:24px;text-align:right;margin-top:2rem;">
                    🧮 總計：NT$ {total:,}
                </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"系統暫時無法提供選配服務，請稍後再試 ({str(e)})")

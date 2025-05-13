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

# 安全檢查函數
def safe_get(df, column, default=None):
    return df[column] if column in df.columns else default

# 資料讀取強化錯誤處理
@st.cache_data
def load_data():
    try:
        excel_path = Path(__file__).parent / "Qiao-Si-AutoJia-Mu-Biao.xlsx"
        df = pd.read_excel(excel_path, sheet_name="工作表1", engine="openpyxl")
        required_columns = ['品牌', '車型', '巧思分類', '車長(mm)', '車寬(mm)', '車高(mm)']
        return df.dropna(subset=required_columns)[required_columns]
    except Exception as e:
        st.error(f"資料載入失敗: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def load_pricing():
    try:
        excel_path = Path(__file__).parent / "Qiao-Si-AutoJia-Mu-Biao.xlsx"
        pricing_df = pd.read_excel(excel_path, sheet_name="工作表1", engine="openpyxl")
        option_cols = pricing_df.columns[10:28]
        return pricing_df[['巧思分類'] + option_cols.tolist()].drop_duplicates().set_index('巧思分類')
    except Exception as e:
        st.error(f"價格表載入失敗: {str(e)}")
        return pd.DataFrame()

# 初始化資料
df = load_data()
pricing_df = load_pricing()

# 側邊欄設計
with st.sidebar:
    st.markdown("### 🚗 車輛篩選系統")
    
    # 品牌選擇安全檢查
    all_brands = ['所有品牌'] + df['品牌'].unique().tolist()
    selected_brand = st.selectbox("選擇品牌", all_brands)
    
    # 動態車型選項
    if selected_brand == '所有品牌':
        models = ['所有車型'] + df['車型'].unique().tolist()
    else:
        models = ['所有車型'] + df[df['品牌'] == selected_brand]['車型'].unique().tolist()
    selected_model = st.selectbox("選擇車型", models)

# 主畫面
st.markdown("### 📊 核心規格表")

# 安全篩選邏輯
try:
    brand_filter = df['品牌'] == selected_brand if selected_brand != '所有品牌' else pd.Series([True]*len(df))
    model_filter = df['車型'] == selected_model if selected_model != '所有車型' else pd.Series([True]*len(df))
    filtered_df = df[brand_filter & model_filter]
except KeyError as e:
    st.error(f"篩選錯誤: {str(e)}")
    filtered_df = pd.DataFrame()

# 安全顯示表格
if not filtered_df.empty:
    st.dataframe(
        filtered_df[['巧思分類', '車長(mm)', '車寬(mm)', '車高(mm)']],
        height=250,
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("無符合條件車輛")

# --- 安全選配系統 ---
if not filtered_df.empty and selected_model != '所有車型':
    try:
        car_class = filtered_df.iloc[0]['巧思分類']
        
        st.markdown("---")
        st.markdown(f"### 🛠️ {car_class} 專屬選配")
        
        if car_class in pricing_df.index:
            class_prices = pricing_df.loc[car_class].dropna()
            
            # 動態選配
            selected = []
            for i in range(1,6):
                opt = st.selectbox(
                    f"選配項目 {i}",
                    ["(不選購)"] + class_prices.index.tolist(),
                    key=f"opt_{i}"
                )
                if opt != "(不選購)":
                    selected.append(class_prices[opt])
            
            # 安全價格計算
            if selected:
                total = sum(selected)
                st.markdown(f"""
                <div style="color:#e74c3c;font-size:24px;text-align:right;">
                    選配總價：NT$ {total:,}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("此分類無可用選配")
    except KeyError as e:
        st.error(f"選配系統錯誤: {str(e)}")

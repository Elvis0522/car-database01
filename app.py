import streamlit as st
import pandas as pd
import os

# 頁面設定
st.set_page_config(page_title="台灣車型資料庫", layout="wide", page_icon="🚗")

# 資料讀取（有錯誤時提示）
@st.cache_data
def load_data():
    excel_path = os.path.join(os.path.dirname(__file__), "Qiao-Si-AutoJia-Mu-Biao.xlsx")
    try:
        df = pd.read_excel(excel_path, sheet_name="工作表1", engine="openpyxl")
        return df
    except Exception as e:
        st.error(f"讀取 Excel 檔案失敗，請確認檔名與工作表名稱正確。\n錯誤訊息：{e}")
        return pd.DataFrame()  # 傳回空表格

df = load_data()

if df.empty:
    st.warning("目前無法載入資料，請檢查 Excel 檔案與工作表名稱。")
    st.stop()

# 側邊欄篩選器
st.sidebar.header("篩選條件")
brands = df['品牌'].dropna().unique().tolist()
selected_brands = st.sidebar.multiselect("選擇品牌", options=brands, default=brands[:3])

if '總價落點' in df.columns:
    price_options = df['總價落點'].dropna().unique().tolist()
    selected_prices = st.sidebar.multiselect("選擇價格帶", options=price_options, default=price_options)
else:
    selected_prices = []

# 主畫面
st.title("台灣車型規格資料庫")
st.markdown("### 互動式資料表格")

# 動態篩選
filtered_df = df[
    (df['品牌'].isin(selected_brands)) &
    (df['總價落點'].isin(selected_prices) if selected_prices else True)
]

# 統計卡片
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("總車型數", len(filtered_df))
with col2:
    st.metric("平均車長", f"{filtered_df['車長(mm)'].mean():.1f} mm" if not filtered_df.empty else "N/A")
with col3:
    st.metric("最大車寬", f"{filtered_df['車寬(mm)'].max()} mm" if not filtered_df.empty else "N/A")

# 互動式表格
st.dataframe(
    filtered_df,
    hide_index=True,
    use_container_width=True
)

# 視覺化分析
if not filtered_df.empty:
    st.markdown("### 視覺化分析")
    tab1, tab2 = st.tabs(["尺寸分布", "品牌統計"])

    with tab1:
        st.scatter_chart(
            filtered_df,
            x="車長(mm)",
            y="車寬(mm)",
            color="品牌",
            size="車高(mm)"
        )
    with tab2:
        brand_counts = filtered_df['品牌'].value_counts()
        st.bar_chart(brand_counts)
else:
    st.info("請調整篩選條件以顯示資料和圖表。")

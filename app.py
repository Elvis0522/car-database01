import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="台灣車型資料庫", layout="wide", page_icon="🚗")

@st.cache_data
def load_data():
    excel_path = Path(__file__).parent / "Qiao-Si-AutoJia-Mu-Biao.xlsx"
    return pd.read_excel(excel_path, sheet_name="工作表1")

df = load_data()

st.sidebar.header("篩選條件")
selected_brands = st.sidebar.multiselect(
    "選擇品牌",
    options=df['品牌'].dropna().unique(),
    default=list(df['品牌'].dropna().unique())[:3]
)

price_options = df['總價落點'].dropna().unique()
selected_prices = st.sidebar.multiselect(
    "選擇價格帶",
    options=price_options,
    default=price_options
)

st.title("台灣車型規格資料庫")
st.markdown("### 互動式資料表格")

filtered_df = df[
    (df['品牌'].isin(selected_brands)) &
    (df['總價落點'].isin(selected_prices))
]

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("總車型數", len(filtered_df))
with col2:
    st.metric("平均車長", f"{filtered_df['車長(mm)'].mean():.1f} mm")
with col3:
    st.metric("最大車寬", f"{filtered_df['車寬(mm)'].max()} mm")

st.dataframe(
    filtered_df,
    hide_index=True,
    use_container_width=True
)

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

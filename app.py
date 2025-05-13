import streamlit as st
import pandas as pd
from pathlib import Path

# 設定頁面
st.set_page_config(
    page_title="巧思汽車鍍膜規格查詢系統",
    layout="wide",
    page_icon="🚗"
)

# 資料讀取函數
@st.cache_data
def load_data():
    excel_path = Path(__file__).parent / "Qiao-Si-AutoJia-Mu-Biao.xlsx"
    df = pd.read_excel(excel_path, sheet_name="工作表1", engine="openpyxl")
    # 清理缺失值
    df = df.dropna(subset=['品牌', '車型'])
    return df

df = load_data()

# 側邊欄設計
with st.sidebar:
    st.header("鍍膜車輛篩選系統")
    
    # 第一層篩選：品牌
    selected_brand = st.selectbox(
        "選擇品牌",
        options=['全部'] + sorted(df['品牌'].unique().tolist()),
        index=0  # 預設選「全部」
    )
    
    # 第二層篩選：車型（動態根據品牌調整）
    if selected_brand == '全部':
        available_models = df['車型'].unique().tolist()
    else:
        available_models = df[df['品牌'] == selected_brand]['車型'].unique().tolist()
    
    selected_model = st.selectbox(
        "選擇車型",
        options=['全部'] + sorted(available_models),
        index=0
    )

# 主畫面資料篩選邏輯
if selected_brand == '全部' and selected_model == '全部':
    filtered_df = df
elif selected_brand == '全部':
    filtered_df = df[df['車型'] == selected_model]
elif selected_model == '全部':
    filtered_df = df[df['品牌'] == selected_brand]
else:
    filtered_df = df[(df['品牌'] == selected_brand) & (df['車型'] == selected_model)]

# 顯示結果
st.subheader("車輛規格表")
st.dataframe(
    filtered_df[['車長(mm)', '車寬(mm)', '車高(mm)', '巧思分類', '總價落點']],
    column_config={
        "車長(mm)": st.column_config.NumberColumn(format="%d mm"),
        "車寬(mm)": st.column_config.NumberColumn(format="%d mm"),
        "車高(mm)": st.column_config.NumberColumn(format="%d mm"),
        "總價落點": "鍍膜方案價格帶"
    },
    use_container_width=True,
    hide_index=True
)

# 顯示統計資訊
st.markdown(f"**符合條件車輛數：{len(filtered_df)} 台**")

import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="汽車鍍膜中心專用查詢", layout="wide", page_icon="🚗")

@st.cache_data
def load_data():
    excel_path = Path(__file__).parent / "Qiao-Si-AutoJia-Mu-Biao.xlsx"
    df = pd.read_excel(excel_path, sheet_name="工作表1", engine="openpyxl")
    df = df.dropna(subset=["品牌", "車型"])
    return df

df = load_data()

# 1. 品牌下拉選單
brand_list = sorted(df["品牌"].dropna().unique())
selected_brand = st.selectbox("請選擇品牌", brand_list)

# 2. 車型下拉選單（依品牌動態篩選）
model_list = sorted(df[df["品牌"] == selected_brand]["車型"].dropna().unique())
selected_model = st.selectbox("請選擇車型", model_list)

# 3. 篩選資料
filtered = df[(df["品牌"] == selected_brand) & (df["車型"] == selected_model)]

# 4. 顯示資訊（含總價落點粗體）
if not filtered.empty:
    info = filtered.iloc[0]
    st.markdown("### 查詢結果")
    st.markdown(f"""
    | 巧思分類 | 車長(mm) | 車寬(mm) | 車高(mm) | <b>總價落點</b> |
    |:---:|:---:|:---:|:---:|:---:|
    | {info['巧思分類']} | {info['車長(mm)']} | {info['車寬(mm)']} | {info['車高(mm)']} | <b>{info['總價落點']}</b> |
    """, unsafe_allow_html=True)
else:
    st.warning("查無資料，請重新選擇。")

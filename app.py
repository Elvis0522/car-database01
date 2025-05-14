import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# 頁面設定
st.set_page_config(
    page_title="巧思鍍膜管理系統",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# 列印用CSS樣式 (隱藏不需要的元素)
st.markdown("""
<style>
    @media print {
        .no-print, .stSidebar, button {
            display: none !important;
        }
        body {
            width: 210mm !important;
            height: 297mm !important;
        }
    }
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
    required_cols = ['品牌', '類型', '車型', '巧思分類', '車長(mm)', '車寬(mm)', '車高(mm)', '總價落點']
    return df[required_cols].dropna(subset=required_cols)

@st.cache_data
def load_pricing():
    excel_path = Path(__file__).parent / "Qiao-Si-AutoJia-Mu-Biao.xlsx"
    df = pd.read_excel(excel_path, sheet_name="工作表1", engine="openpyxl")
    return df[['巧思分類'] + df.columns[10:28].tolist()].drop_duplicates().set_index('巧思分類')

df = load_data()
pricing_df = load_pricing()

# 品牌排序
all_brands = df['品牌'].unique().tolist()
sorted_brands = ['所有品牌'] + sorted(
    [b for b in all_brands if b != '0-巧思業務用'],
    key=lambda x: x.replace('0-巧思業務用', '')
)
if '0-巧思業務用' in all_brands:
    sorted_brands.insert(1, '0-巧思業務用')

# 側邊欄
with st.sidebar:
    st.markdown("### 🚗 車輛篩選系統")
    selected_brand = st.selectbox(
        "選擇品牌",
        options=sorted_brands,
        index=1 if '0-巧思業務用' in sorted_brands else 0
    )
    if selected_brand == '所有品牌':
        models = ['所有車型'] + sorted(df['車型'].unique().tolist())
    else:
        models = ['所有車型'] + sorted(df[df['品牌'] == selected_brand]['車型'].unique().tolist())
    selected_model = st.selectbox("選擇車型", models)

# 主畫面
# --- 客戶資料表單 ---
form_data = {}
if (
    selected_brand != '所有品牌'
    and selected_model != '所有車型'
    and not df[
        (df['品牌'] == selected_brand) & (df['車型'] == selected_model)
    ].empty
):
    st.markdown("#### 🚩 客戶資料表單")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        form_data['date'] = st.date_input("日期", value=date.today(), disabled=True)
    with col2:
        form_data['name'] = st.text_input("姓名")
    with col3:
        form_data['title'] = st.selectbox("稱謂", options=["先生", "小姐"], index=0, disabled=True)
    with col4:
        form_data['plate'] = st.text_input("車牌號碼")
    col5, col6 = st.columns(2)
    with col5:
        form_data['model'] = st.text_input("型號")
    with col6:
        form_data['year'] = st.text_input("年份")
    col7, col8 = st.columns(2)
    with col7:
        form_data['phone'] = st.text_input("電話")
    with col8:
        form_data['email'] = st.text_input("E-mail")

# --- 車輛規格表與選配系統 (維持Seed02原有程式碼) ---
# ... [保持Seed02原有程式碼不變] ...

# --- 新增：報價單生成條件檢查與按鈕 ---
if (
    selected_brand != '所有品牌'
    and selected_model != '所有車型'
    and all(form_data.values())  # 確認所有表單欄位已填寫
    and 'selected' in locals()   # 確認有選購項目
    and total > 0                # 確認有顯示金額
):
    # 生成PDF的JavaScript代碼
    js_code = f"""
    <script>
        function triggerPrint() {{
            window.print();
        }}
        document.title = "{form_data['name']}_{form_data['plate']}";
        setTimeout(triggerPrint, 500);
    </script>
    """
    st.markdown(js_code, unsafe_allow_html=True)
    st.button("📄 產生報價單", use_container_width=True, type='primary")

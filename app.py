import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# 初始化 session_state
if 'reset' not in st.session_state:
    st.session_state.reset = False

# 頁面設定
st.set_page_config(
    page_title="巧思鍍膜管理系統",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# 列印用CSS樣式
st.markdown("""
<style>
    @media print {
        .no-print, .stSidebar, .stButton {
            display: none !important;
        }
        .stApp {
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
        form_data['date'] = st.date_input("日期", value=date.today(), disabled=True, key='form_date')
    with col2:
        form_data['name'] = st.text_input("姓名", key='form_name', value=st.session_state.get('form_name', ''))
    with col3:
        form_data['title'] = st.selectbox("稱謂", options=["先生", "小姐"], index=0, disabled=True, key='form_title')
    with col4:
        form_data['plate'] = st.text_input("車牌號碼", key='form_plate', value=st.session_state.get('form_plate', ''))
    col5, col6 = st.columns(2)
    with col5:
        form_data['model'] = st.text_input("型號", key='form_model', value=st.session_state.get('form_model', ''))
    with col6:
        form_data['year'] = st.text_input("年份", key='form_year', value=st.session_state.get('form_year', ''))
    col7, col8 = st.columns(2)
    with col7:
        form_data['phone'] = st.text_input("電話", key='form_phone', value=st.session_state.get('form_phone', ''))
    with col8:
        form_data['email'] = st.text_input("E-mail", key='form_email', value=st.session_state.get('form_email', ''))

# --- 新增功能按鈕 ---
col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if st.button("🔄 重置表單", use_container_width=True, type='primary'):
        # 清空 session_state 中的表單數據
        for key in ['form_name', 'form_plate', 'form_model', 'form_year', 'form_phone', 'form_email']:
            st.session_state[key] = ''
        # 清空選配數據
        st.session_state['selected_options'] = []
        st.experimental_rerun()

with col_btn2:
    js_code = f"""
    <script>
        function triggerPrint() {{
            window.print();
        }}
    </script>
    """
    st.markdown(js_code, unsafe_allow_html=True)
    if st.button("📄 產出報價單", use_container_width=True, type='primary'):
        filename = f"{form_data.get('name','未命名')}_{form_data.get('plate','未命名')}".replace(" ", "_")
        st.markdown(f"""
        <script>
            document.title = "{filename}";
            setTimeout(triggerPrint, 500);
        </script>
        """, unsafe_allow_html=True)

# --- 車輛規格表與選配系統 (維持Seed02原有程式碼) ---
# ...（以下維持Seed02原有程式碼，包含車輛規格表與選配系統）...

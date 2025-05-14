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

# 列印用CSS樣式
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

st.markdown("### 📊 車輛規格表")

try:
    brand_filter = df['品牌'] == selected_brand if selected_brand != '所有品牌' else df['品牌'].notnull()
    model_filter = df['車型'] == selected_model if selected_model != '所有車型' else df['車型'].notnull()
    filtered_df = df[brand_filter & model_filter].head(5)
    
    if not filtered_df.empty:
        st.dataframe(
            filtered_df[['類型', '車型', '車長(mm)', '車寬(mm)', '車高(mm)', '總價落點']],
            height=300,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("⚠️ 沒有找到符合條件的車輛")
except Exception as e:
    st.error(f"資料顯示錯誤: {str(e)}")

# 選配系統（含數量選擇）
selected = []
total = 0
if not filtered_df.empty and selected_model != '所有車型':
    try:
        car_class = filtered_df.iloc[0]['巧思分類']
        st.markdown("---")
        st.markdown(f"### 🛠️ {car_class} 專屬選配")
        if car_class in pricing_df.index:
            class_prices = pricing_df.loc[car_class].dropna()
            for i in range(1,6):
                col1, col2 = st.columns([2,1])
                with col1:
                    opt = st.selectbox(
                        f"選配項目 {i}",
                        ["(不選購)"] + class_prices.index.tolist(),
                        key=f"opt_{i}"
                    )
                if opt != "(不選購)":
                    with col2:
                        qty = st.selectbox(
                            "數量",
                            options=list(range(1, 11)),
                            key=f"qty_{i}"
                        )
                    selected.append((opt, class_prices[opt], qty))
                    st.markdown(f"✓ **{opt}** - NT$ {class_prices[opt]:,} × {qty} = NT$ {class_prices[opt]*qty:,}")
            if selected:
                total = sum(price*qty for _, price, qty in selected)
                st.markdown(f"<div class='total-price'>總計：NT$ {total:,}</div>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"選配系統錯誤: {str(e)}")

# --- 報價單按鈕顯示條件 ---
def all_form_filled(form_data):
    # 日期、稱謂預設有值，其餘需填寫
    return all(form_data.get(k, '').strip() for k in ['name','plate','model','year','phone','email'])

if (
    selected_brand != '所有品牌'
    and selected_model != '所有車型'
    and all_form_filled(form_data)
    and selected
    and total > 0
):
    st.markdown("---")
    if st.button("📄 產生報價單", use_container_width=True, type="primary"):
        # 產生PDF的JS
        filename = f"{form_data['name']}_{form_data['plate']}".replace(" ", "")
        js_code = f"""
        <script>
            document.title = "{filename}";
            window.print();
        </script>
        """
        st.markdown(js_code, unsafe_allow_html=True)
    st.caption("點擊後可用瀏覽器另存PDF，檔名自動為「姓名_車牌號碼」")


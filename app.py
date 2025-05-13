import streamlit as st
import pandas as pd
from pathlib import Path

# 页面设定
st.set_page_config(
    page_title="巧思镀膜管理系统",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# 现代简约样式
st.markdown("""
<style>
    [data-testid=stSidebar] {
        background: #ffffff;
        border-right: 1px solid #e0e0e0;
        padding: 2rem;
    }
    .stSelectbox > div > div {
        border: 1px solid #e0e0e0 !important;
        border-radius: 8px;
    }
    h3 {
        color: #2d3436;
        font-family: 'Helvetica Neue';
        border-bottom: 2px solid #0984e3;
        padding-bottom: 0.5rem;
    }
    .price-formula {
        font-family: monospace;
        margin: 1rem 0;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 8px;
    }
    .total-price {
        color: #e74c3c;
        font-size: 24px;
        font-weight: 700;
        text-align: right;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    excel_path = Path(__file__).parent / "Qiao-Si-AutoJia-Mu-Biao.xlsx"
    df = pd.read_excel(excel_path, sheet_name="工作表1", engine="openpyxl")
    return df.dropna(subset=['品牌', '車型'])

@st.cache_data
def get_pricing():
    excel_path = Path(__file__).parent / "Qiao-Si-AutoJia-Mu-Biao.xlsx"
    df = pd.read_excel(excel_path, sheet_name="工作表1", engine="openpyxl")
    return df[['巧思分類'] + df.columns[10:28].tolist()].set_index('巧思分類')

df = load_data()
pricing_df = get_pricing()

# 侧边栏筛选
with st.sidebar:
    st.markdown("### 车辆筛选")
    
    # 品牌选择
    brand = st.selectbox(
        "选择品牌",
        options=['所有品牌'] + sorted(df['品牌'].unique()),
        index=0
    )
    
    # 动态车型选项
    models = ['所有车型'] + sorted(
        df[df['品牌'] == brand]['車型'].unique() if brand != '所有品牌' 
        else df['車型'].unique()
    )
    model = st.selectbox("选择车型", models, index=0)

# 主界面
st.markdown("### 车辆规格")

# 筛选逻辑
filtered = df[
    (df['品牌'] == brand if brand != '所有品牌' else True) &
    (df['車型'] == model if model != '所有车型' else True)
]

# 核心规格显示
if not filtered.empty:
    st.dataframe(
        filtered[['巧思分類', '車長(mm)', '車寬(mm)', '車高(mm)']],
        height=250,  # 固定显示约5行高度
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("无匹配车辆")

# 选配系统
if not filtered.empty and model != '所有车型':
    st.markdown("---")
    st.markdown("### 镀膜选配")
    
    classification = filtered.iloc[0]['巧思分類']
    
    if classification in pricing_df.index:
        options = pricing_df.loc[classification].dropna()
        
        selected = []
        for i in range(1,6):
            choice = st.selectbox(
                f"选配项目 {i}",
                options=["(空)"] + options.index.tolist(),
                key=f"opt_{i}"
            )
            if choice != "(空)":
                selected.append( (choice, options[choice]) )
        
        # 价格公式显示
        if selected:
            formula = " + ".join([f"({price})" for _, price in selected])
            total = sum(price for _, price in selected)
            
            st.markdown("#### 价格计算")
            st.markdown(f"""
            <div class="price-formula">
                {formula} = <span class="total-price">NT$ {total:,}</span>
            </div>
            """, unsafe_allow_html=True)

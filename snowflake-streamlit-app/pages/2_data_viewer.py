import streamlit as st
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="サンプルデータ表示", page_icon="📊", layout="wide")

st.title("📊 サンプルデータ表示 & CSVダウンロード")
st.write("Snowflakeのサンプルデータベース（SNOWFLAKE_SAMPLE_DATA）からデータを取得し、表形式で表示・CSVダウンロードできます。")

session = get_active_session()

TABLES = {
    "顧客 (CUSTOMER)": "SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.CUSTOMER",
    "注文 (ORDERS)": "SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS",
    "商品 (PART)": "SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.PART",
    "国 (NATION)": "SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.NATION",
}

col1, col2 = st.columns([2, 1])
with col1:
    table_label = st.selectbox("テーブルを選択", list(TABLES.keys()))
with col2:
    row_limit = st.number_input("取得件数", min_value=10, max_value=10000, value=100, step=10)

table_name = TABLES[table_label]

if st.button("🔍 データを取得", type="primary"):
    with st.spinner("データ取得中..."):
        df = session.table(table_name).limit(int(row_limit)).to_pandas()
        st.session_state["df_app2"] = df
        st.session_state["table_name_app2"] = table_name

if "df_app2" in st.session_state:
    df = st.session_state["df_app2"]
    st.write(f"取得件数: {len(df)} 件")
    st.dataframe(df, use_container_width=True)

    csv_bytes = df.to_csv(index=False).encode("utf-8-sig")
    file_name = st.session_state["table_name_app2"].split(".")[-1].lower()
    st.download_button(
        label="💾 CSVダウンロード",
        data=csv_bytes,
        file_name=f"{file_name}.csv",
        mime="text/csv",
        use_container_width=True,
    )
else:
    st.info("👆 テーブルと取得件数を選んで「データを取得」を押してください。")

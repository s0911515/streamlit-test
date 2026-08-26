import streamlit as st
import datetime
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="可視化ダッシュボード", page_icon="📈", layout="wide")

st.title("📈 可視化ダッシュボード (TPC-H サンプルデータ)")
st.write("Snowflakeのサンプルデータ（SNOWFLAKE_SAMPLE_DATA）を集計し、期間・国でフィルタしながらグラフで確認できます。")

session = get_active_session()

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("開始日", value=datetime.date(1997, 1, 1))
with col2:
    end_date = st.date_input("終了日", value=datetime.date(1997, 12, 31))


@st.cache_data(ttl=600, show_spinner="集計中...")
def load_sales_by_month_nation(start: datetime.date, end: datetime.date):
    query = """
        SELECT
            DATE_TRUNC('MONTH', o.o_orderdate)::DATE AS ORDER_MONTH,
            n.n_name AS NATION,
            SUM(o.o_totalprice) AS TOTAL_SALES,
            COUNT(*) AS ORDER_COUNT
        FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS o
        JOIN SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.CUSTOMER c ON o.o_custkey = c.c_custkey
        JOIN SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.NATION n ON c.c_nationkey = n.n_nationkey
        WHERE o.o_orderdate BETWEEN ? AND ?
        GROUP BY 1, 2
        ORDER BY 1
    """
    return session.sql(query, params=[start, end]).to_pandas()


if start_date > end_date:
    st.error("開始日は終了日より前にしてください。")
else:
    df = load_sales_by_month_nation(start_date, end_date)

    if df.empty:
        st.warning("該当期間のデータがありません。期間を広げてみてください。")
    else:
        nations = sorted(df["NATION"].unique().tolist())
        selected_nations = st.multiselect("国で絞り込み（未選択の場合は全件）", nations)

        filtered = df[df["NATION"].isin(selected_nations)] if selected_nations else df

        total_sales = filtered["TOTAL_SALES"].sum()
        total_orders = filtered["ORDER_COUNT"].sum()
        avg_order_value = total_sales / total_orders if total_orders else 0

        m1, m2, m3 = st.columns(3)
        m1.metric("合計売上", f"${total_sales:,.0f}")
        m2.metric("注文件数", f"{total_orders:,}")
        m3.metric("平均注文単価", f"${avg_order_value:,.2f}")

        st.subheader("月次売上推移")
        monthly = filtered.groupby("ORDER_MONTH")["TOTAL_SALES"].sum().reset_index()
        st.line_chart(monthly, x="ORDER_MONTH", y="TOTAL_SALES")

        st.subheader("国別 売上合計")
        by_nation = filtered.groupby("NATION")["TOTAL_SALES"].sum().sort_values(ascending=False).reset_index()
        st.bar_chart(by_nation, x="NATION", y="TOTAL_SALES")

        with st.expander("集計データを見る"):
            st.dataframe(filtered, use_container_width=True)

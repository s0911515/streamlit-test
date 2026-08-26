import streamlit as st
import datetime
import plotly.express as px
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


def render_kpi_card(column, icon: str, label: str, value: str, color: str):
    with column:
        st.markdown(
            f"""
            <div style="
                background-color: {color}22;
                border: 1px solid {color}55;
                border-left: 5px solid {color};
                border-radius: 10px;
                padding: 16px 18px;
                margin-bottom: 4px;
            ">
                <div style="font-size: 0.85rem; color: rgba(255,255,255,0.75); margin-bottom: 6px;">
                    {icon} {label}
                </div>
                <div style="font-size: 1.7rem; font-weight: 700; color: {color};">
                    {value}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


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

        monthly = filtered.groupby("ORDER_MONTH")["TOTAL_SALES"].sum().reset_index()
        by_nation = (
            filtered.groupby("NATION")["TOTAL_SALES"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )

        total_sales = filtered["TOTAL_SALES"].sum()
        total_orders = filtered["ORDER_COUNT"].sum()
        avg_order_value = total_sales / total_orders if total_orders else 0
        nation_count = filtered["NATION"].nunique()
        peak_month_row = monthly.loc[monthly["TOTAL_SALES"].idxmax()] if not monthly.empty else None

        st.markdown("#### 📌 サマリー")
        m1, m2, m3, m4 = st.columns(4)
        render_kpi_card(m1, "💰", "合計売上", f"${total_sales:,.0f}", "#3B82F6")
        render_kpi_card(m2, "📦", "注文件数", f"{total_orders:,}", "#22C55E")
        render_kpi_card(m3, "🧾", "平均注文単価", f"${avg_order_value:,.2f}", "#F59E0B")
        render_kpi_card(m4, "🌍", "対象国数", f"{nation_count} か国", "#A855F7")

        st.markdown("---")

        chart_col1, chart_col2 = st.columns([2, 1])
        with chart_col1:
            with st.container(border=True):
                st.markdown("##### 月次売上推移")
                st.line_chart(monthly, x="ORDER_MONTH", y="TOTAL_SALES")
                if peak_month_row is not None:
                    st.caption(
                        f"📈 ピーク月: {peak_month_row['ORDER_MONTH']:%Y-%m} "
                        f"（${peak_month_row['TOTAL_SALES']:,.0f}）"
                    )

        with chart_col2:
            with st.container(border=True):
                st.markdown("##### 国別 売上構成比")
                fig = px.pie(
                    by_nation,
                    names="NATION",
                    values="TOTAL_SALES",
                    hole=0.45,
                )
                fig.update_traces(textposition="inside", textinfo="percent+label")
                fig.update_layout(
                    margin=dict(t=10, b=10, l=10, r=10),
                    showlegend=False,
                    height=320,
                )
                st.plotly_chart(fig, use_container_width=True)

        with st.container(border=True):
            st.markdown("##### 国別 売上合計")
            st.bar_chart(by_nation, x="NATION", y="TOTAL_SALES")

        with st.expander("集計データを見る"):
            st.dataframe(filtered, use_container_width=True)

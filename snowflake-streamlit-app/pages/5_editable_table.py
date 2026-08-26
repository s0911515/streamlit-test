import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="編集可能テーブル", page_icon="📝", layout="wide")

st.title("📝 編集可能テーブル（商品マスタ管理）")
st.write("表を直接編集し、行の追加・削除・変更をした上で「変更を保存」を押すと、Snowflakeのテーブルに反映されます。")

session = get_active_session()

DATABASE = "STREAMLIT_APPS"
SCHEMA = "PUBLIC"
TABLE = "DEMO_PRODUCT_MASTER"
FULL_TABLE_NAME = f"{DATABASE}.{SCHEMA}.{TABLE}"


def ensure_table_exists():
    session.sql(
        f"""
        CREATE TABLE IF NOT EXISTS {FULL_TABLE_NAME} (
            PRODUCT_ID INT,
            PRODUCT_NAME STRING,
            CATEGORY STRING,
            PRICE NUMBER(10, 2),
            IN_STOCK BOOLEAN
        )
        """
    ).collect()

    if session.table(FULL_TABLE_NAME).count() == 0:
        seed_df = pd.DataFrame(
            [
                {"PRODUCT_ID": 1, "PRODUCT_NAME": "ノートPC", "CATEGORY": "電子機器", "PRICE": 120000, "IN_STOCK": True},
                {"PRODUCT_ID": 2, "PRODUCT_NAME": "ワイヤレスマウス", "CATEGORY": "電子機器", "PRICE": 2500, "IN_STOCK": True},
                {"PRODUCT_ID": 3, "PRODUCT_NAME": "オフィスチェア", "CATEGORY": "家具", "PRICE": 18000, "IN_STOCK": False},
                {"PRODUCT_ID": 4, "PRODUCT_NAME": "デスク", "CATEGORY": "家具", "PRICE": 25000, "IN_STOCK": True},
            ]
        )
        session.write_pandas(
            seed_df, TABLE, database=DATABASE, schema=SCHEMA, auto_create_table=False, overwrite=True
        )


ensure_table_exists()

st.write(f"対象テーブル: `{FULL_TABLE_NAME}`")
st.caption("行末の「+」で追加、行を選択して Delete キーで削除できます（num_rows=\"dynamic\"）。")

if "product_editor_data" not in st.session_state:
    st.session_state["product_editor_data"] = session.table(FULL_TABLE_NAME).to_pandas()

col_reset, _ = st.columns([1, 3])
with col_reset:
    if st.button("🔄 DBの最新状態に戻す（未保存の変更は破棄）", use_container_width=True):
        st.session_state["product_editor_data"] = session.table(FULL_TABLE_NAME).to_pandas()
        st.rerun()

edited_df = st.data_editor(
    st.session_state["product_editor_data"],
    num_rows="dynamic",
    use_container_width=True,
    key="product_editor",
)

col1, col2 = st.columns([1, 3])
with col1:
    if st.button("💾 変更を保存", type="primary", use_container_width=True):
        try:
            with st.spinner("保存中..."):
                session.write_pandas(
                    edited_df,
                    TABLE,
                    database=DATABASE,
                    schema=SCHEMA,
                    auto_create_table=False,
                    overwrite=True,
                )
            st.session_state["product_editor_data"] = edited_df
            st.success(f"✅ {len(edited_df)} 行を保存しました。")
        except Exception as e:
            st.error(f"保存に失敗しました: {e}")

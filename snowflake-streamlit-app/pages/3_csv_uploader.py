import streamlit as st
import pandas as pd
import re
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="CSVアップロード & テーブル作成", page_icon="📥", layout="wide")

st.title("📥 CSVアップロード & テーブル作成")
st.write("CSVファイルをアップロードして、その内容をSnowflakeのテーブルとして作成します。")

session = get_active_session()


def sanitize_column_name(name: str) -> str:
    # \w は日本語などのUnicode文字も含むため、スペースや記号だけを置換する
    name = re.sub(r"[^\w]", "_", str(name).strip())
    if re.match(r"^[0-9]", name):
        name = f"COL_{name}"
    return name.upper()


def dedupe_column_names(names: list[str]) -> list[str]:
    seen = {}
    result = []
    for name in names:
        if name not in seen:
            seen[name] = 0
            result.append(name)
        else:
            seen[name] += 1
            result.append(f"{name}_{seen[name]}")
    return result


uploaded_file = st.file_uploader("CSVファイルを選択", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = dedupe_column_names([sanitize_column_name(c) for c in df.columns])

    st.subheader("プレビュー")
    st.write(f"{len(df)} 行 × {len(df.columns)} 列")
    st.dataframe(df.head(100), use_container_width=True)

    st.subheader("テーブル作成設定")
    col1, col2 = st.columns(2)
    with col1:
        target_database = st.text_input("データベース", value=session.get_current_database().strip('"'))
    with col2:
        target_schema = st.text_input("スキーマ", value=session.get_current_schema().strip('"'))

    table_name = st.text_input("テーブル名", value="MY_UPLOADED_TABLE")
    overwrite = st.checkbox("既存のテーブルを上書きする（OVERWRITE）", value=False)

    if st.button("🚀 テーブルを作成", type="primary"):
        full_table_name = f"{target_database}.{target_schema}.{table_name}"
        try:
            with st.spinner("テーブルを作成中..."):
                session.write_pandas(
                    df,
                    table_name,
                    database=target_database,
                    schema=target_schema,
                    auto_create_table=True,
                    overwrite=overwrite,
                )
            st.success(f"✅ テーブル `{full_table_name}` を作成しました（{len(df)} 行）。")
        except Exception as e:
            st.error(f"テーブル作成に失敗しました: {e}")
else:
    st.info("👆 CSVファイルをアップロードしてください。")

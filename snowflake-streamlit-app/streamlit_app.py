import streamlit as st

st.set_page_config(
    page_title="テストアプリ統合ポータル",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 テストアプリ統合ポータル")
st.caption("Snowflake Streamlit (Multi-page Apps) 実証実験環境")

st.markdown("---")

st.subheader("📌 利用可能なテストアプリケーション")

row1_col1, row1_col2 = st.columns(2)
row2_col1, row2_col2 = st.columns(2)

with row1_col1:
    with st.container(border=True):
        st.markdown("### 📄 高度PDF帳票プレビュー")
        st.write("DBアクセス不要。ReportLabで日本語PDFを動的生成し、pypdfium2により高画質画像としてプレビュー表示・ダウンロードが可能です。")
        st.page_link("pages/1_pdf_preview.py", label="このアプリを開く", icon="🚀")

with row1_col2:
    with st.container(border=True):
        st.markdown("### 📊 サンプルデータ表示 & CSVダウンロード")
        st.write("Snowflakeのサンプルデータベース（SNOWFLAKE_SAMPLE_DATA）からデータを取得し、表形式で表示・CSVダウンロードできます。")
        st.page_link("pages/2_data_viewer.py", label="このアプリを開く", icon="🚀")

with row2_col1:
    with st.container(border=True):
        st.markdown("### 📥 CSVアップロード & テーブル作成")
        st.write("CSVファイルをアップロードし、内容をプレビューした上でSnowflakeのテーブルとして作成します。")
        st.page_link("pages/3_csv_uploader.py", label="このアプリを開く", icon="🚀")

with row2_col2:
    with st.container(border=True):
        st.markdown("### 📈 可視化ダッシュボード")
        st.write("Snowflakeのサンプルデータを集計し、期間・国でフィルタしながら売上推移をグラフで確認できます。")
        st.page_link("pages/4_dashboard.py", label="このアプリを開く", icon="🚀")

st.markdown("---")
st.markdown("#### 💡 使い方")
st.markdown("""
1. Snowsight のこのアプリ編集画面でコードを直接編集・保存します。
2. 保存すると、この画面がそのまま最新状態で再実行されます。
""")

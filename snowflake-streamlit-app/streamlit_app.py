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

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("### 📄 高度PDF帳票プレビュー")
        st.write("DBアクセス不要。ReportLabで日本語PDFを動的生成し、pypdfium2により高画質画像としてプレビュー表示・ダウンロードが可能です。")
        st.info("👈 左側のサイドバーメニューから **「1_pdf_preview」** を選択して起動してください。")

with col2:
    with st.container(border=True):
        st.markdown("### 📊 データ分析ダッシュボード（準備中）")
        st.write("Snowflake上のサンプルデータを参照し、動的なグラフ描画や集計を行うコンポーネントのテスト用画面です。")
        st.warning("⚠️ 現在開発中")

st.markdown("---")
st.markdown("#### 💡 使い方")
st.markdown("""
1. VS Code 上でコードを編集し、GitHub リポジトリへ `push` します。
2. Snowflake 画面（または SQL ワークシート）で Git Fetch を実行すると、最新状態が即座に反映されます。
""")

import streamlit as st
import pandas as pd
import numpy as np
import time
from PIL import Image, ImageDraw

st.set_page_config(page_title="UIパーツ総覧", page_icon="🎨", layout="wide")

st.title("🎨 UIパーツ総覧（画面リッチさ検証用）")
st.write("Streamlitで配置できる主要なUI部品を、カテゴリ別タブでまとめて確認できます。")

tabs = st.tabs(
    ["テキスト", "レイアウト", "入力", "データ表示", "メディア", "チャート", "進捗/通知", "チャット", "その他"]
)

# ---------------- テキスト ----------------
with tabs[0]:
    st.header("見出し (st.header)")
    st.subheader("小見出し (st.subheader)")
    st.markdown("**太字** / *斜体* / ~~取り消し線~~ / `インラインコード` / [リンク](https://streamlit.io)")
    st.caption("キャプション文字（st.caption）")
    st.code("def hello():\n    print('Hello, Streamlit!')", language="python")
    st.latex(r"\sum_{i=1}^{n} i = \frac{n(n+1)}{2}")
    st.divider()
    st.text("装飾なしのプレーンテキスト（st.text）")

# ---------------- レイアウト ----------------
with tabs[1]:
    st.write("列レイアウト（st.columns）")
    c1, c2, c3 = st.columns(3)
    c1.info("列1")
    c2.success("列2")
    c3.warning("列3")

    st.write("展開パネル（st.expander）")
    with st.expander("クリックで展開"):
        st.write("展開された中身です。")

    st.write("枠付きコンテナ（st.container(border=True)）")
    with st.container(border=True):
        st.write("枠で囲まれたコンテナ")

    if hasattr(st, "popover"):
        st.write("ポップオーバー（st.popover）")
        with st.popover("クリックでポップオーバー表示"):
            st.write("ポップオーバーの中身です。")
    else:
        st.info("st.popover はこの環境では利用できません。")

# ---------------- 入力 ----------------
with tabs[2]:
    col1, col2 = st.columns(2)
    with col1:
        st.button("ボタン (st.button)")
        st.checkbox("チェックボックス")
        if hasattr(st, "toggle"):
            st.toggle("トグルスイッチ")
        st.radio("ラジオボタン", ["A", "B", "C"])
        st.selectbox("セレクトボックス", ["りんご", "みかん", "ぶどう"])
        st.multiselect("複数選択", ["赤", "青", "緑"], default=["赤"])
        st.slider("スライダー", 0, 100, 50)
        st.select_slider("セレクトスライダー", options=["小", "中", "大"])
    with col2:
        st.text_input("テキスト入力")
        st.text_area("テキストエリア")
        st.number_input("数値入力", value=10)
        st.date_input("日付入力")
        st.time_input("時刻入力")
        st.color_picker("カラーピッカー", "#1E3A8A")
        st.file_uploader("ファイルアップロード")
        st.download_button("ダウンロードボタン", data="サンプルテキスト", file_name="sample.txt")

    st.divider()
    if hasattr(st, "pills"):
        st.pills("ピル選択（st.pills）", ["Option1", "Option2", "Option3"])
    if hasattr(st, "segmented_control"):
        st.segmented_control("セグメントコントロール", ["左", "中", "右"])
    if hasattr(st, "feedback"):
        st.write("フィードバック（st.feedback）")
        st.feedback("thumbs")

# ---------------- データ表示 ----------------
with tabs[3]:
    sample_df = pd.DataFrame({"商品": ["A", "B", "C"], "売上": [1200, 800, 1500]})

    st.write("データフレーム（st.dataframe、ソート・リサイズ可能）")
    st.dataframe(sample_df, use_container_width=True)

    st.write("静的テーブル（st.table）")
    st.table(sample_df)

    st.write("メトリクス（st.metric）")
    m1, m2, m3 = st.columns(3)
    m1.metric("売上", "3,500", "+12%")
    m2.metric("客数", "128", "-3%")
    m3.metric("客単価", "27.3", "+5%")

    st.write("JSON表示（st.json）")
    st.json({"a": 1, "b": [1, 2, 3], "c": {"d": True}})

# ---------------- メディア ----------------
with tabs[4]:
    st.write("画像（st.image、その場で生成）")
    img = Image.new("RGB", (400, 200), color="#1E3A8A")
    draw = ImageDraw.Draw(img)
    draw.ellipse((50, 50, 350, 150), fill="#F59E0B")
    st.image(img, caption="Pillowでその場で生成した画像")

    st.info("st.audio / st.video は再生用のファイルまたはURLが必要なため、ここでは割愛しています。")

# ---------------- チャート ----------------
with tabs[5]:
    chart_df = pd.DataFrame(np.random.randn(20, 3), columns=["系列A", "系列B", "系列C"])

    st.write("折れ線グラフ（st.line_chart）")
    st.line_chart(chart_df)

    st.write("棒グラフ（st.bar_chart）")
    st.bar_chart(chart_df)

    st.write("面グラフ（st.area_chart）")
    st.area_chart(chart_df)

    if hasattr(st, "scatter_chart"):
        st.write("散布図（st.scatter_chart）")
        st.scatter_chart(chart_df, x="系列A", y="系列B")

    st.write("地図（st.map）")
    map_df = pd.DataFrame(
        {
            "lat": 35.6812 + np.random.randn(20) * 0.02,
            "lon": 139.7671 + np.random.randn(20) * 0.02,
        }
    )
    st.map(map_df)

# ---------------- 進捗/通知 ----------------
with tabs[6]:
    if st.button("進捗バーを表示"):
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.005)
            progress_bar.progress(i + 1)
        st.success("完了しました！")

    if st.button("スピナーを表示"):
        with st.spinner("処理中..."):
            time.sleep(1)
        st.write("完了")

    if hasattr(st, "status") and st.button("ステータスログを表示"):
        with st.status("処理を実行中...", expanded=True) as status:
            st.write("ステップ1: データ取得中")
            time.sleep(0.5)
            st.write("ステップ2: 集計中")
            time.sleep(0.5)
            status.update(label="完了しました", state="complete")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🎈 バルーン"):
            st.balloons()
    with col2:
        if st.button("❄️ スノー"):
            st.snow()
    with col3:
        if st.button("🔔 トースト通知"):
            st.toast("これはトースト通知です！", icon="🔔")

# ---------------- チャット ----------------
with tabs[7]:
    st.write("チャットUI（st.chat_message / st.chat_input）")
    with st.chat_message("user"):
        st.write("こんにちは！")
    with st.chat_message("assistant"):
        st.write("こんにちは、何かお手伝いできますか？")

    prompt = st.chat_input("メッセージを入力")
    if prompt:
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant"):
            st.write(f"「{prompt}」ですね、承知しました（デモ応答です）。")

# ---------------- その他 ----------------
with tabs[8]:
    if hasattr(st, "dialog"):

        @st.dialog("サンプルダイアログ")
        def sample_dialog():
            st.write("これはモーダルダイアログの中身です。")
            if st.button("閉じる"):
                st.rerun()

        if st.button("ダイアログを開く"):
            sample_dialog()
    else:
        st.info("st.dialog はこの環境では利用できません。")

    st.write("アラート系（st.error / st.warning / st.info / st.success）")
    st.error("エラーメッセージ")
    st.warning("警告メッセージ")
    st.info("情報メッセージ")
    st.success("成功メッセージ")

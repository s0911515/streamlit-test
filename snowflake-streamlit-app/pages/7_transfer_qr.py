import streamlit as st
import qrcode
import io
import json
import pandas as pd
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="振込QRコード発行", page_icon="🏦", layout="wide")

st.title("🏦 振込QRコード発行（銀行窓口端末 連携シミュレーション）")
st.write(
    "振込先口座と金額を指定すると、その情報を埋め込んだQRコードを発行します。"
    "実際の銀行窓口端末でこのQRコードを読み取ると、振込画面に情報が自動入力される……というイメージのデモです"
    "（読み取り側の端末は実装していない“ふり”です）。"
)

session = get_active_session()

DATABASE = "STREAMLIT_APPS"
SCHEMA = "PUBLIC"
TABLE = "DEMO_BANK_ACCOUNTS"
FULL_TABLE_NAME = f"{DATABASE}.{SCHEMA}.{TABLE}"


def ensure_table_exists():
    session.sql(
        f"""
        CREATE TABLE IF NOT EXISTS {FULL_TABLE_NAME} (
            ACCOUNT_ID INT,
            ACCOUNT_HOLDER_NAME STRING,
            BANK_NAME STRING,
            BRANCH_NAME STRING,
            ACCOUNT_TYPE STRING,
            ACCOUNT_NUMBER STRING
        )
        """
    ).collect()

    if session.table(FULL_TABLE_NAME).count() == 0:
        seed_df = pd.DataFrame(
            [
                {
                    "ACCOUNT_ID": 1,
                    "ACCOUNT_HOLDER_NAME": "ヤマダ タロウ",
                    "BANK_NAME": "みずほ銀行",
                    "BRANCH_NAME": "本店営業部",
                    "ACCOUNT_TYPE": "普通",
                    "ACCOUNT_NUMBER": "1234567",
                },
                {
                    "ACCOUNT_ID": 2,
                    "ACCOUNT_HOLDER_NAME": "スズキ ハナコ",
                    "BANK_NAME": "三井住友銀行",
                    "BRANCH_NAME": "渋谷支店",
                    "ACCOUNT_TYPE": "普通",
                    "ACCOUNT_NUMBER": "7654321",
                },
                {
                    "ACCOUNT_ID": 3,
                    "ACCOUNT_HOLDER_NAME": "カブシキガイシャ サンプル",
                    "BANK_NAME": "三菱UFJ銀行",
                    "BRANCH_NAME": "新宿支店",
                    "ACCOUNT_TYPE": "当座",
                    "ACCOUNT_NUMBER": "9998887",
                },
            ]
        )
        session.write_pandas(
            seed_df, TABLE, database=DATABASE, schema=SCHEMA, auto_create_table=False, overwrite=True
        )


ensure_table_exists()

accounts_df = session.table(FULL_TABLE_NAME).to_pandas()

col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("① 振込先口座を選択（DBから取得）")
    account_labels = [
        f"{row.ACCOUNT_HOLDER_NAME}（{row.BANK_NAME} {row.BRANCH_NAME} {row.ACCOUNT_TYPE} {row.ACCOUNT_NUMBER}）"
        for row in accounts_df.itertuples()
    ]
    selected_label = st.selectbox("口座", account_labels)
    selected_account = accounts_df.iloc[account_labels.index(selected_label)]

    st.subheader("② 振込内容を入力")
    amount = st.number_input("振込金額 (円)", min_value=1, step=1000, value=50000)
    memo = st.text_input("摘要（任意）", value="")

    generate = st.button("📱 QRコードを発行", type="primary", use_container_width=True)

with col2:
    st.subheader("③ 発行されたQRコード")
    if generate:
        payload = {
            "bank_name": selected_account["BANK_NAME"],
            "branch_name": selected_account["BRANCH_NAME"],
            "account_type": selected_account["ACCOUNT_TYPE"],
            "account_number": selected_account["ACCOUNT_NUMBER"],
            "account_holder_name": selected_account["ACCOUNT_HOLDER_NAME"],
            "amount": int(amount),
            "memo": memo,
        }
        payload_str = json.dumps(payload, ensure_ascii=False)

        qr = qrcode.QRCode(border=2, box_size=8)
        qr.add_data(payload_str)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        qr_bytes = buf.getvalue()

        st.image(
            qr_bytes,
            caption="このQRコードを窓口端末で読み取ると、右の内容が振込画面に自動入力される想定です",
        )

        st.markdown("**QRコードに埋め込まれている内容**")
        st.code(payload_str, language="json")

        st.download_button(
            "💾 QRコード画像をダウンロード",
            data=qr_bytes,
            file_name="transfer_qr.png",
            mime="image/png",
            use_container_width=True,
        )
    else:
        st.info("👈 口座と金額を指定して「QRコードを発行」を押してください。")

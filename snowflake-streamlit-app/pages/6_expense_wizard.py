import streamlit as st
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="経費申請ウィザード", page_icon="🧭", layout="wide")

st.title("🧭 経費申請ウィザード")
st.write("複数ステップの入力フォームです。st.session_state を使って「入力 → 確認 → 登録」の画面遷移を管理しています。")

session = get_active_session()

DATABASE = "STREAMLIT_APPS"
SCHEMA = "PUBLIC"
TABLE = "DEMO_EXPENSE_REQUESTS"
FULL_TABLE_NAME = f"{DATABASE}.{SCHEMA}.{TABLE}"

DEPARTMENTS = ["営業部", "開発部", "管理部", "マーケティング部"]
EXPENSE_TYPES = ["交通費", "接待交際費", "消耗品費", "会議費", "その他"]


def ensure_table_exists():
    session.sql(
        f"""
        CREATE TABLE IF NOT EXISTS {FULL_TABLE_NAME} (
            REQUEST_ID INT AUTOINCREMENT,
            APPLICANT_NAME STRING,
            DEPARTMENT STRING,
            EXPENSE_TYPE STRING,
            AMOUNT NUMBER(10, 0),
            DESCRIPTION STRING,
            SUBMITTED_AT TIMESTAMP_NTZ
        )
        """
    ).collect()


ensure_table_exists()

if "wizard_step" not in st.session_state:
    st.session_state.wizard_step = 1
if "wizard_data" not in st.session_state:
    st.session_state.wizard_data = {}

steps = ["① 基本情報入力", "② 内容確認", "③ 登録完了"]
st.progress((st.session_state.wizard_step - 1) / (len(steps) - 1))
st.caption(
    " → ".join(
        f"**{s}**" if i + 1 == st.session_state.wizard_step else s
        for i, s in enumerate(steps)
    )
)
st.markdown("---")

# ---- Step 1: 入力 ----
if st.session_state.wizard_step == 1:
    with st.form("step1_form"):
        applicant_name = st.text_input(
            "申請者名", value=st.session_state.wizard_data.get("applicant_name", "")
        )
        department = st.selectbox(
            "部門",
            DEPARTMENTS,
            index=DEPARTMENTS.index(st.session_state.wizard_data.get("department", DEPARTMENTS[0])),
        )
        expense_type = st.selectbox("経費種別", EXPENSE_TYPES)
        amount = st.number_input(
            "金額 (円)", min_value=0, step=100, value=st.session_state.wizard_data.get("amount", 0)
        )
        description = st.text_area(
            "摘要・備考", value=st.session_state.wizard_data.get("description", "")
        )

        submitted = st.form_submit_button("次へ（確認画面）", type="primary")
        if submitted:
            if not applicant_name.strip():
                st.error("申請者名を入力してください。")
            elif amount <= 0:
                st.error("金額は1円以上で入力してください。")
            else:
                st.session_state.wizard_data = {
                    "applicant_name": applicant_name,
                    "department": department,
                    "expense_type": expense_type,
                    "amount": amount,
                    "description": description,
                }
                st.session_state.wizard_step = 2
                st.rerun()

# ---- Step 2: 確認 ----
elif st.session_state.wizard_step == 2:
    data = st.session_state.wizard_data
    st.subheader("入力内容の確認")
    st.write(f"**申請者名**: {data['applicant_name']}")
    st.write(f"**部門**: {data['department']}")
    st.write(f"**経費種別**: {data['expense_type']}")
    st.write(f"**金額**: ¥{data['amount']:,}")
    st.write(f"**摘要・備考**: {data['description'] or '（なし）'}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← 戻って修正する", use_container_width=True):
            st.session_state.wizard_step = 1
            st.rerun()
    with col2:
        if st.button("✅ この内容で登録する", type="primary", use_container_width=True):
            try:
                session.sql(
                    f"""
                    INSERT INTO {FULL_TABLE_NAME}
                        (APPLICANT_NAME, DEPARTMENT, EXPENSE_TYPE, AMOUNT, DESCRIPTION, SUBMITTED_AT)
                    SELECT ?, ?, ?, ?, ?, CURRENT_TIMESTAMP()
                    """,
                    params=[
                        data["applicant_name"],
                        data["department"],
                        data["expense_type"],
                        data["amount"],
                        data["description"],
                    ],
                ).collect()
                st.session_state.wizard_step = 3
                st.rerun()
            except Exception as e:
                st.error(f"登録に失敗しました: {e}")

# ---- Step 3: 完了 ----
else:
    st.success("✅ 経費申請を登録しました。")
    st.balloons()

    with st.expander("登録済みの申請一覧を見る（直近20件）"):
        df = session.sql(
            f"SELECT * FROM {FULL_TABLE_NAME} ORDER BY SUBMITTED_AT DESC LIMIT 20"
        ).to_pandas()
        st.dataframe(df, use_container_width=True)

    if st.button("➕ 続けて別の申請を入力する"):
        st.session_state.wizard_data = {}
        st.session_state.wizard_step = 1
        st.rerun()

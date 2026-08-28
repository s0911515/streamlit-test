import streamlit as st
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="ログインユーザー/ロール認識", page_icon="🪪", layout="wide")

st.title("🪪 ログインユーザー/ロール認識デモ")
st.write(
    "Streamlit in Snowflakeでは、「アプリを見ている本人」の情報と、"
    "「アプリが実際にSQLを実行するときの権限（実行ロール）」が別物になることがあります。"
    "その両方をこの画面で確認し、実行ロールに応じて表示を出し分けるデモです。"
)

session = get_active_session()

st.subheader("① アプリを見ている本人の情報 (st.user / st.experimental_user)")

user_obj = getattr(st, "user", None) or getattr(st, "experimental_user", None)

if user_obj is None:
    st.info("この環境では st.user / st.experimental_user が利用できませんでした。")
else:
    user_dict = {}
    try:
        user_dict = dict(user_obj)
    except Exception:
        for key in ["user_name", "email", "role_name", "roles", "name"]:
            value = getattr(user_obj, key, None)
            if value is not None:
                user_dict[key] = value

    if user_dict:
        st.json(user_dict)
    else:
        st.info("識別情報を取得できませんでした（取得できる項目は実行環境・設定によって異なります）。")

st.markdown("---")

st.subheader("② SQL実行時の権限（Snowparkセッション）")
current_user = session.get_current_user()
current_role = session.get_current_role()
current_warehouse = session.get_current_warehouse()

col1, col2, col3 = st.columns(3)
col1.metric("実行ユーザー", current_user)
col2.metric("実行ロール", current_role)
col3.metric("ウェアハウス", current_warehouse)

st.caption(
    "Streamlit in Snowflakeのアプリは、既定で「今ログインしている本人の、現在アクティブなロール」"
    "でSQLを実行します（Caller's Rights的な動作）。Snowsight右上（または左下）でロールを切り替えて"
    "このアプリを開き直すと、ここの表示もそのロールに変わります。"
)

st.markdown("---")

st.subheader("③ ロールに応じた表示の出し分け（デモ）")

ADMIN_ROLES = {"ACCOUNTADMIN", "SYSADMIN"}
role_clean = (current_role or "").strip('"').upper()

if role_clean in ADMIN_ROLES:
    st.success(f"✅ 実行ロール（{current_role}）は管理者ロールです。管理者向けパネルを表示します。")
    with st.container(border=True):
        st.markdown("#### 🛠️ 管理者専用パネル")
        st.write(
            "ここに、一般ユーザーには見せたくない機能"
            "（マスタデータの削除、権限変更、他ユーザーの申請一覧の閲覧など）を配置するイメージです。"
        )
else:
    st.warning(f"⚠️ 実行ロール（{current_role}）は管理者ロールではないため、管理者向けパネルは表示されません。")

st.markdown("---")

st.subheader("④ このユーザーに割り当てられているロール一覧")

try:
    grants_df = session.sql(f"SHOW GRANTS TO USER {current_user}").to_pandas()
    grants_df.columns = [c.strip().strip('"').upper() for c in grants_df.columns]

    if "GRANTED_ON" in grants_df.columns and "NAME" in grants_df.columns:
        role_rows = grants_df[grants_df["GRANTED_ON"].astype(str).str.strip().str.upper() == "ROLE"]
        st.dataframe(
            role_rows[["NAME"]].rename(columns={"NAME": "ROLE"}).reset_index(drop=True),
            use_container_width=True,
        )
    else:
        st.dataframe(grants_df, use_container_width=True)
except Exception as e:
    st.error(f"ロール一覧の取得に失敗しました: {e}")

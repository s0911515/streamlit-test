import streamlit as st
import io
import pypdfium2 as pdfium
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

st.set_page_config(page_title="高度PDF帳票プレビュー", page_icon="📄", layout="wide")

st.title("📄 高度PDF帳票プレビュー (DB不要テスト)")
st.write("フォームに入力した内容を元に、メモリ上でPDFを発行してリアルタイムに高画質プレビューします。")

FONT_NAME = "Helvetica"
FONT_PATH = "NotoSansJP-Bold.ttf"

if os.path.exists(FONT_PATH):
    try:
        pdfmetrics.registerFont(TTFont("NotoSans", FONT_PATH))
        FONT_NAME = "NotoSans"
    except Exception as e:
        st.warning(f"フォント読み込みエラー: {e}")

def generate_pdf_bytes(company_name, title_text, amount):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30
    )
    story = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName=FONT_NAME,
        fontSize=20,
        leading=24,
        alignment=1,
        textColor=colors.HexColor("#1E3A8A")
    )

    normal_style = ParagraphStyle(
        'DocNormal',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=10,
        leading=14
    )

    story.append(Paragraph(title_text, title_style))
    story.append(Spacer(1, 20))

    story.append(Paragraph(f"<b>発行先:</b> {company_name} 御中", normal_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"<b>ご請求金額:</b> ￥{amount:,}-", ParagraphStyle('Amount', parent=normal_style, fontSize=14, leading=18, textColor=colors.HexColor("#B91C1C"))))
    story.append(Spacer(1, 15))

    data = [
        ["品名・項目", "数量", "単価", "金額"],
        ["クラウド基盤構築支援サービス", "1", f"￥{amount:,}", f"￥{amount:,}"],
        ["Streamlit アプリケーション開発", "1", "￥0 (サービス)", "￥0"],
    ]

    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F3F4F6")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#1F2937")),
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ])

    t = Table(data, colWidths=[240, 60, 100, 100])
    t.setStyle(table_style)
    story.append(t)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

col_input, col_preview = st.columns([1, 1.2])

with col_input:
    st.subheader("⚙️ 帳票パラメータ入力")
    company_name = st.text_input("宛名（会社名）", value="株式会社サンプル")
    title_text = st.selectbox("帳票種別", ["御請求書", "御見積書", "領収書"])
    amount = st.number_input("請求金額 (円)", value=150000, step=10000)

    btn_generate = st.button("📄 帳票を更新・生成", type="primary", use_container_width=True)

with col_preview:
    st.subheader("🖼️ リアルタイムプレビュー")

    pdf_bytes = generate_pdf_bytes(company_name, title_text, amount)

    try:
        pdf_file = pdfium.PdfDocument(pdf_bytes)
        for page_idx, page in enumerate(pdf_file):
            image = page.render(scale=200 / 72).to_pil()
            st.image(image, caption=f"ページ {page_idx + 1}", use_container_width=True)

        st.download_button(
            label="💾 PDFファイルをダウンロード",
            data=pdf_bytes,
            file_name=f"{title_text}_{company_name}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"プレビュー描画中にエラーが発生しました: {e}")

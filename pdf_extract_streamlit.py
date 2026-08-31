import io
import streamlit as st
import pikepdf


def extract_pages(input_bytes, start_page, end_page):
    """PDFの指定ページ範囲を抽出して、bytesとして返す。"""
    input_buffer = io.BytesIO(input_bytes)
    output_buffer = io.BytesIO()

    with pikepdf.open(input_buffer) as pdf:
        total_pages = len(pdf.pages)

        if start_page < 1 or end_page < 1:
            raise ValueError("ページ番号は1以上を指定してください。")
        if start_page > end_page:
            raise ValueError("開始ページは終了ページ以下にしてください。")
        if end_page > total_pages:
            raise ValueError(
                f"終了ページがPDFの総ページ数 ({total_pages}) を超えています。"
            )

        new_pdf = pikepdf.Pdf.new()

        for i in range(start_page - 1, end_page):
            new_pdf.pages.append(pdf.pages[i])

        new_pdf.save(output_buffer)

    output_buffer.seek(0)
    return output_buffer.getvalue()


st.set_page_config(
    page_title="PDF Page Extractor",
    page_icon="📄",
    layout="centered",
)

st.title("PDF Page Extractor")
st.write("PDFから指定したページ範囲を抽出して、新しいPDFとして保存できます。")

uploaded_file = st.file_uploader("PDFファイルを選択", type=["pdf"])

if uploaded_file is not None:
    pdf_bytes = uploaded_file.getvalue()

    try:
        with pikepdf.open(io.BytesIO(pdf_bytes)) as pdf:
            total_pages = len(pdf.pages)

        st.info(f"総ページ数: {total_pages}")

        col1, col2 = st.columns(2)

        with col1:
            start_page = st.number_input(
                "開始ページ",
                min_value=1,
                max_value=total_pages,
                value=1,
                step=1,
            )

        with col2:
            end_page = st.number_input(
                "終了ページ",
                min_value=1,
                max_value=total_pages,
                value=total_pages,
                step=1,
            )

        default_output_name = f"extracted_{int(start_page)}-{int(end_page)}.pdf"
        output_name = st.text_input("出力ファイル名", value=default_output_name)

        if not output_name.lower().endswith(".pdf"):
            output_name += ".pdf"

        if st.button("PDFを抽出", type="primary"):
            try:
                extracted_pdf = extract_pages(
                    pdf_bytes,
                    int(start_page),
                    int(end_page),
                )

                st.success(
                    f"{int(start_page)} ～ {int(end_page)} ページを抽出しました。"
                )

                st.download_button(
                    label="抽出したPDFをダウンロード",
                    data=extracted_pdf,
                    file_name=output_name,
                    mime="application/pdf",
                )

            except Exception as e:
                st.error(f"PDFの抽出中にエラーが発生しました: {e}")

    except Exception as e:
        st.error(f"PDFを読み込めませんでした: {e}")

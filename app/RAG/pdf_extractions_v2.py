
import fitz
from utils import clean_text_v2


class PdfExtractions_v2:

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.full_text = []

    def extract_text_from_pdf(self, pdf_path=None):
        if pdf_path is None:
            if self.pdf_path is None:
                raise ValueError("PDF path is not provided.")
            pdf_path = self.pdf_path

        doc = fitz.open(pdf_path)
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text()
            """Removes non-printable characters from a string."""
            text = clean_text_v2(text)
            # images = page.get_images(full=True)
            self.full_text.append(text)
        print(f"{page_num} pages extracted {self.full_text}")
        return self.full_text

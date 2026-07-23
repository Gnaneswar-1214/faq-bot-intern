import unittest
import os
import tempfile
from src.extract import extract_text_from_file


class TestExtract(unittest.TestCase):
    def test_extract_txt_file(self):
        with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False) as f:
            f.write("Hello world. This is a test document for text extraction.")
            f_path = f.name

        try:
            result = extract_text_from_file(f_path, "test.txt")
            self.assertIn("Hello world", result)
            self.assertIn("text extraction", result)
        finally:
            if os.path.exists(f_path):
                os.remove(f_path)

    def test_extract_empty_txt(self):
        with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False) as f:
            f.write("   \n  ")
            f_path = f.name

        try:
            with self.assertRaises(ValueError):
                extract_text_from_file(f_path, "empty.txt")
        finally:
            if os.path.exists(f_path):
                os.remove(f_path)

    def test_unsupported_format(self):
        with self.assertRaises(ValueError):
            extract_text_from_file("sample.xlsx", "sample.xlsx")

    def test_extract_docx_file(self):
        try:
            from docx import Document
        except ImportError:
            self.skipTest("python-docx is not installed")

        doc = Document()
        doc.add_paragraph("Hello world. This is a docx test.")
        
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            doc.save(f.name)
            f_path = f.name

        try:
            result = extract_text_from_file(f_path, "test.docx")
            self.assertIn("Hello world", result)
            self.assertIn("docx test", result)
        finally:
            if os.path.exists(f_path):
                os.remove(f_path)

    def test_extract_md_file(self):
        with tempfile.NamedTemporaryFile("w+", suffix=".md", delete=False) as f:
            f.write("# Hello world\n\nThis is a markdown test.")
            f_path = f.name

        try:
            result = extract_text_from_file(f_path, "test.md")
            self.assertIn("Hello world", result)
            self.assertIn("markdown test", result)
        finally:
            if os.path.exists(f_path):
                os.remove(f_path)


if __name__ == "__main__":
    unittest.main()

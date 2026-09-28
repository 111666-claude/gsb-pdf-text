import unittest

from pdftext.extract import PdfError, _decode_text, extract


def build(content, indirect=False):
    length = b"/Length 5 0 R" if indirect else b"/Length %d" % len(content)
    stream = b"<< %s >>\nstream\n" % length + content + b"\nendstream\n"
    return b"%PDF-1.4\n" + stream + b"5 0 obj\n%d\nendobj\n" % len(content)


class DecodeTest(unittest.TestCase):
    def test_plain_text(self):
        self.assertEqual(_decode_text(b"hello"), "hello")

    def test_escaped_parens(self):
        self.assertEqual(_decode_text(b"a\\(b\\)c"), "a(b)c")

    def test_backslash(self):
        self.assertEqual(_decode_text(b"a\\\\b"), "a\\b")


class ExtractTest(unittest.TestCase):
    def test_single_block(self):
        self.assertEqual(extract(build(b"BT 72 720 Td (hello) Tj ET")), ["hello"])

    def test_two_blocks(self):
        self.assertEqual(extract(build(b"BT (one) Tj ET BT (two) Tj ET")), ["one", "two"])

    def test_missing_endstream(self):
        with self.assertRaises(PdfError):
            extract(b"1 0 obj\n<< /Length 1 >>\nstream\nx\n")


if __name__ == "__main__":
    unittest.main()

"""命令行入口：用内置样本演示抽文本。"""

import argparse
import sys
import zlib

from .extract import PdfError, extract


def _build_pdf(content, indirect_length=False):
    """构造一个最小 PDF：对象 3 是内容流，可选间接 /Length。"""
    stream = zlib.compress(content) if indirect_length else content
    length = b"/Length 5 0 R" if indirect_length else b"/Length %d" % len(stream)
    filter_ = b" /Filter /FlateDecode" if indirect_length else b""
    objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [4 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n<< %s%s >>\nstream\n" % (length, filter_) + stream + b"\nendstream\nendobj\n",
        b"4 0 obj\n<< /Type /Page /Parent 2 0 R /Contents 3 0 R >>\nendobj\n",
        b"5 0 obj\n%d\nendobj\n" % len(stream),
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for item in objects:
        offsets.append(len(out))
        out += item
    start = len(out)
    out += b"xref\n0 %d\n" % (len(objects) + 1)
    out += b"0000000000 65535 f \n"
    for offset in offsets:
        out += ("%010d 00000 n \n" % offset).encode()
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objects) + 1, start)
    return bytes(out)


def sample(name):
    """escaped 用八进制转义，flate 用间接 /Length 加 FlateDecode。"""
    if name == "escaped":
        return _build_pdf(b"BT /F1 12 Tf 72 720 Td (Hello \\050world\\051 again) Tj ET")
    if name == "flate":
        return _build_pdf(b"BT /F1 12 Tf 72 720 Td (compressed text) Tj ET", indirect_length=True)
    raise PdfError("不认识的样本：%s" % name)


def build_parser():
    parser = argparse.ArgumentParser(prog="pdf-text", description="抽取 PDF 文本")
    parser.add_argument("--sample", help="escaped / flate")
    parser.add_argument("--file", help="真实 PDF 文件")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if args.file:
            with open(args.file, "rb") as handle:
                data = handle.read()
        elif args.sample:
            data = sample(args.sample)
        else:
            print("错误：需要 --sample 或 --file", file=sys.stderr)
            return 2
        for text in extract(data):
            print("text=%s" % text)
    except (PdfError, OSError, ValueError) as error:
        print("错误：%s" % error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

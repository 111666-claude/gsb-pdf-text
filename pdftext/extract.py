"""从 PDF 里抽文本，只用标准库。

缺陷：只认直接的 /Length（间接写法报错），转义只处理反斜杠、左右括号三种，
八进制转义（\\050 这类）被原样保留。
"""

import re
import zlib


class PdfError(ValueError):
    """PDF 不合法。缺陷：不带偏移。"""

    def __init__(self, message):
        super().__init__(message)
        self.message = message


def _streams(data):
    """切出每个流及其字典。"""
    out = []
    for match in re.finditer(rb"<<(.*?)>>\s*stream\r?\n", data, re.S):
        start = match.end()
        end = data.find(b"endstream", start)
        if end < 0:
            raise PdfError("流没有 endstream")
        out.append((match.group(1), data[start:end].rstrip(b"\r\n")))
    return out


def _stream_length(dictionary):
    """缺陷：只支持 /Length 12 这种直接写法。"""
    match = re.search(rb"/Length\s+(\d+)(?!\s+\d+\s+R)", dictionary)
    if not match:
        raise PdfError("流长度必须是直接整数")
    return int(match.group(1))


def _decode_text(raw):
    """解析括号里的文本。缺陷：只处理反斜杠、左右括号三种转义。"""
    out = []
    index = 0
    while index < len(raw):
        byte = raw[index]
        if byte == 0x5C and index + 1 < len(raw):
            nxt = raw[index + 1]
            if nxt in (0x5C, 0x28, 0x29):
                out.append(nxt)
                index += 2
                continue
            out.append(byte)
            index += 1
            continue
        out.append(byte)
        index += 1
    return bytes(out).decode("latin-1")


def extract(data):
    """抽取所有 BT...ET 块里 (... ) Tj 的文本。"""
    texts = []
    for dictionary, payload in _streams(data):
        if b"FlateDecode" in dictionary:
            size = _stream_length(dictionary)
            try:
                payload = zlib.decompress(payload[:size])
            except zlib.error as error:
                raise PdfError("流解压失败：%s" % error) from error
        for block in re.finditer(rb"BT(.*?)ET", payload, re.S):
            for item in re.finditer(rb"\((.*?)\)\s*Tj", block.group(1), re.S):
                texts.append(_decode_text(item.group(1)))
    return texts

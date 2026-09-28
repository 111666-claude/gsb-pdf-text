# pdf-text

从 PDF 里抽文本的最小实现（对象、内容流、转义、FlateDecode），只用 Python 标准库。

```
python3 -m pdftext.cli --sample escaped
python3 -m pdftext.cli --sample flate
python3 -m unittest discover -s tests -v
```

## 口径（README 为准）

- **八进制转义要解析**：`\050` 是左括号、`\051` 是右括号、`\134` 是反斜杠。
  `--sample escaped` 的内容流是 `(Hello \050world\051 again)`，按口径输出 `Hello (world) again`，
  现在把 `\050` 原样留着，输出 `Hello \050world\051 again`。
- **/Length 支持间接写法**：遇到 `/Length 5 0 R` 要跳去对象 5 取长度（或按对象表解析）。
  `--sample flate` 按口径要解压后输出 `compressed text`，现在直接报「流长度必须是直接整数」。
- 转义还要处理 `\n \r \t \b \f` 与行尾反斜杠续行；字符串里的裸括号要配对计数，嵌套括号不能提前结束。
- 抽取规则：只取 `BT...ET` 块里的 `(...) Tj`（以及 `[...] TJ` 数组里的每段字符串），
  按出现顺序返回；忽略注释与二进制垃圾。
- 不变量：同一份 PDF 重复抽取结果相同；不修改输入；解压失败的流要报错并指出是第几个流。
- 规模：10 MB 的 PDF 单遍扫描，内存 O(内容流大小)；不许把整份 PDF 转成字符串。

## 现在的行为

- `_decode_text` 只处理反斜杠、左括号、右括号三种转义，八进制与 `\n` 都错。
- `_stream_length` 只认 `/Length 12`，间接写法直接报错。
- `_streams` 与 BT/ET 扫描是对的，所以 `--sample escaped` 能跑但文本解错。

## 计划新增的能力

```
--sample 名称    escaped / flate
--file 文件      解析真实 PDF
```

## 输出

```
text=Hello (world) again
```

## 目录

```
pdftext/extract.py   流解析与文本解码
pdftext/cli.py       命令行入口 + 样本
tests/               unittest 用例
```

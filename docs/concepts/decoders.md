# Decoder Compliance Matrix

This matrix documents the capabilities and limitations of the built-in decoders in Contexte v0.1.

| Format | Decoder | Text | Headings | Tables | Spans | Confidence | Notes |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **`.md`** | `MarkdownDecoder` | ✅ | ✅ | ✅ | ✅ | 1.0 | Full structural extraction. |
| **`.txt`** | `TextDecoder` | ✅ | ❌ | ❌ | ✅ | 1.0 | Simple raw text extraction. |
| **`.html`** | `HtmlDecoder` | ✅ | ✅ | ✅ | ❌ | 0.9 | Uses BeautifulSoup4. |
| **`.pdf`** | `PdfDecoder` | ✅ | ⚠️ | ❌ | ❌ | 0.7 | Text extraction only; no OCR. |
| **`.docx`** | `DocxDecoder` | ✅ | ✅ | ✅ | ❌ | 0.8 | Uses python-docx. |
| **`.csv`** | `CsvDecoder` | ✅ | N/A | ✅ | ✅ | 1.0 | Each row is a block. |
| **`.json`** | `JsonDecoder` | ✅ | N/A | N/A | ❌ | 1.0 | Recursive structure mapping. |

## Legend

- ✅: Full support.
- ⚠️: Partial or heuristic support.
- ❌: No support in v0.1.
- N/A: Not applicable to this format.

## Future Plans

- **Docling Integration**: Move complex PDF and Office extraction to an optional Docling plugin for high-fidelity table and heading recovery.
- **Unstructured Integration**: Provide an alternative modular extraction path for diverse data sources.
- **OCR Support**: Add an optional Tesseract/PaddleOCR layer for scanned PDFs and images.

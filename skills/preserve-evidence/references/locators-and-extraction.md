# Locators and extraction

| Evidence | Workbench locator | Meaning / verification |
|---|---|---|
| CSV/JSON parsed records | `row:N` | One-based parsed-record ordinal; not always physical file line |
| PDF text | `page:N` | One-based PDF position, not necessarily printed page label |
| HTML/text extraction | `line:N` | Line in preserved extraction, which may differ from rendered web layout |

Use exact source ID plus locator and short verbatim quote. Quote presence checks text, not identity, context, interpretation, legal meaning or source truth. For an amount in a table, retain its header, units, row label, fund/period and relevant footnotes; a bare matching number is weak evidence.

## CSV/JSON

Preserve strings for identifiers and exact header names. A CSV header is not a data record; multiline quoted fields break line-to-row assumptions. JSON arrays/nested objects retain their record structure; a string occurrence in unrelated nested content is not confirmation of a claimed relationship. Record rejected/unparsed rows rather than silently certifying completeness.

## PDF

The installed path uses Poppler `pdftotext -layout`. Visually inspect decisive tables against the original PDF, especially wrapped headings, minus signs, parentheses, columns and continuation pages. If a footer says page 2 but the file position is 135, report both when helpful. Check the continuation before interpreting a debit/credit total.

A scan with no text is `needs_ocr`; Tesseract is not installed by this project. Do not infer the document is blank. OCR would require approved tooling, retained page images, settings and manual checks for decisive passages. OCR output is a transformation, not the original. Never fabricate a quote from a blurry image.

## HTML

The extractor removes script/style content and preserves text; navigation and repeated labels may remain. Read source context before quoting. A login page returned with HTTP 200 does not establish document access. Page hydration may require authorized browser inspection; browser-visible content still needs a preserved attributable representation for later use.

## Synthetic failure example

A quoted '100' matches a footnote index but the claim says a provider received 100 dollars. The literal quote may pass a software check; the claim is unsupported because unit/row/column context differs. Correct the citation and interpretation, not the text to force a match.

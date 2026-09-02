# Data Ingestion & Content Processing

Converted from the CortexDB Technical Reference, v1, July 2026.
**Read this when the task involves anything other than plain text**: file
uploads, PDFs, Office documents, images, audio, video, sensor data, or archives.

---

## 1. The unifying model

CortexDB is a text-native memory engine. Everything it retrieves against (BM25
keyword index, HNSW vector index, entity and fact extraction, the five memory
layers) operates on text. The entire multi-modal story reduces to one sentence:

> Every non-text object is turned into `derived_text` (a transcript, description,
> or extracted text) by a modality-specific processor. That `derived_text` then
> flows into the exact same pipeline as ordinary text, while the original raw
> bytes are preserved in a blob store and structured metadata (pages, duration,
> dimensions) is captured alongside.

Each processor returns `ProcessingResult { derived_text, metadata }`. Six content
types are recognized:

| ContentType | Examples | Turned into text by |
|---|---|---|
| Text | plain, markdown, CSV, HTML, JSON, XML | direct UTF-8 read (built-in) |
| Document | PDF, DOCX, PPTX, XLSX | document-extraction provider (Tika / Unstructured) |
| Image | PNG, JPEG | multimodal LLM (vision) description |
| Audio | MP3, WAV, FLAC, OGG, AAC, Opus | ASR (speech-to-text) service |
| Video | MP4 | ffmpeg keyframes plus audio transcript |
| Sensor | time-series / telemetry | a summarization pass |

**Two-phase processing.** Each processor exposes `extract_metadata()`, a fast
synchronous path returning metadata at ingest with no LLM or ASR call, and
`process()`, the heavier path producing `derived_text` via the external service.
The derived text is what makes the object searchable.

**Availability note.** The full v1 file-ingestion path is documented as
implemented and validated end-to-end as of an automated harness run on
2026-07-05, shipping in the release following that date. Rich-media processors
remain opt-in per deployment. Text ingestion works on every build. Verify current
status against a live source before relying on rich-media paths.

---

## 2. Already have a transcript? Skip the processor

When you already hold an authoritative transcript or extracted text, supply it
inline rather than paying to re-derive it:

```
POST /v1/experience
{ "scope":"org:acme/dept:support", "modality":"conversation",
  "content": { "kind":"blob_ref", "blob_id":"blob_...",
               "transcript":"...the text you already have..." } }
```

When `transcript` is present, CortexDB indexes that text and does **not** run the
content processor. No re-transcription of audio, no OCR or parse of the PDF. The
original bytes are still retained in the blob store as provenance, linked via a
`source_blob:<id>` label.

If you do not need the file retained at all, just send the text as
`content:{ "text": ... }`.

---

## 3. Where the text goes

Once a processor yields `derived_text`, it is treated identically to a text write:

```
derived_text -> chunk -> Tantivy BM25 (keyword) + embed -> HNSW (vector)
             -> entity extraction -> knowledge graph
             -> (async LLM) facts, beliefs, episodes, concepts
```

A PDF, a call recording, or a video becomes recall-able and answer-able exactly
like a chat message.

### How data physically enters

| Path | How |
|---|---|
| Inline text | `POST /v1/experience` with `content:{ "text": "..." }`. The common case. |
| File / binary | Upload bytes to `POST /v1/blobs` to get a `blob_id`. Reference it from an experience with `content:{ "kind":"blob_ref", "blob_id":"..." }`. The registry routes the blob to the processor for its MIME type. Raw bytes stay in the blob store; `GET /v1/blobs/{id}` to fetch. Text-shaped uploads are ingested directly as text. |

---

## 4. Text and documents

### 4.1 Plain text and text-like formats (built-in, no external service)

| MIME | Treatment |
|---|---|
| `text/plain`, `text/markdown` | Indexed as-is |
| `text/csv` | Stored as text. For column-aware structuring, route via Unstructured |
| `text/html` | Stored as text, tags included unless stripped client-side |
| `application/json`, `application/xml`, `text/xml` | Stored verbatim |

Anything not in this list is rejected by the native provider with a message to
use `tika` or `unstructured`.

### 4.2 PDF

A PDF is a layout container, not a text file. Text may be present as a real text
layer, or only as pixels with no machine-readable text. Tables, columns, and
reading order are visual conventions, not structure.

Three providers, selected by `CORTEX_DOCUMENT_PROVIDER`:

| Provider | What it does with a PDF | Needs |
|---|---|---|
| `native` | Does not parse PDF. Returns an error telling you to use tika/unstructured | none |
| `tika` | PUTs bytes to an Apache Tika server, returns extracted plain text from the text layer. Robust, fast, format-agnostic | Tika server (`CORTEX_DOCUMENT_API_URL`) |
| `unstructured` | Sends to Unstructured.io, returns structured elements (titles, narrative text, list items, tables) and can OCR scanned pages | Unstructured endpoint plus key |

**The critical distinction:**

| PDF kind | tika | unstructured |
|---|---|---|
| Digital, has text layer | clean text extraction | clean text plus structure |
| Scanned, image-only | little or no text | OCR turns page images into text |

Practical rule: digital exports means Tika is the fast cheap default. Scans
(signed contracts, faxed forms) means Unstructured for OCR, or route pages
through the image processor. **Tika alone silently returns sparse text on scans.**
Know the corpus and validate on a real sample.

Tables: Tika returns a flat text stream, so tables linearize (searchable but cell
structure lost). Unstructured returns typed elements and detects tables, so
prefer it when tabular data carries the meaning.

Metadata captured: `page_count`, `word_count`, `doc_title`, `doc_author`,
`language`.

**What CortexDB does not do with PDFs.** No per-word bounding boxes or
coordinates. No interpretation of form fields, digital-signature semantics, or
annotations as structured objects, though their text is extracted if present.
Extraction quality is only as good as the provider plus the PDF itself.

```
# Apache Tika (digital PDFs, Office docs)
CORTEX_DOCUMENT_PROVIDER=tika
CORTEX_DOCUMENT_API_URL=http://tika:9998

# or Unstructured.io (adds OCR plus table/element structure)
CORTEX_DOCUMENT_PROVIDER=unstructured
CORTEX_DOCUMENT_API_URL=https://api.unstructured.io
CORTEX_DOCUMENT_API_KEY=...
```

### 4.3 Office documents

Same document processor.

| Format | What is extracted |
|---|---|
| DOCX | Body text, headings; Unstructured also preserves element structure |
| PPTX | Slide text and, with Tika/Unstructured, speaker notes |
| XLSX | Cell text across sheets, linearized by Tika, more structured via Unstructured |

---

## 5. Audio, video, images, sensor, blobs

Each requires its processor to be configured. Pattern is always the same: raw
bytes to blob store, processor produces `derived_text`, text is indexed.

### 5.1 Audio

Sends audio to an ASR service and stores the transcript as `derived_text`. Call
recordings and voice notes become searchable and answerable.

- Providers: OpenAI Whisper, Google Speech-to-Text, Deepgram
  (`CORTEX_AUDIO_PROVIDER`)
- Metadata: `duration_ms`, `sample_rate`, `channels`, `audio_codec`
- Enable: `CORTEX_AUDIO_PROVIDER=openai-whisper` plus `CORTEX_AUDIO_API_URL` and
  `CORTEX_AUDIO_API_KEY`, optional `CORTEX_AUDIO_LANGUAGE`

### 5.2 Video

The heaviest pipeline. Using ffmpeg on the host, CortexDB extracts keyframes (a
configurable number per minute) and delegates each to the image processor,
extracts the audio track and delegates it to the audio processor, then combines
both into a single `derived_text`.

- Metadata: `fps`, `frame_count`, `video_codec`, `video_resolution`,
  `duration_ms`
- Requires the ffmpeg binary plus a configured image processor and audio processor
- Enable: `CORTEX_FFMPEG_PATH=ffmpeg` plus `CORTEX_VIDEO_KEYFRAMES_PER_MIN=N`

**Cost note.** Video fans out into many vision-LLM calls, one per keyframe, plus
ASR. Set keyframes-per-minute deliberately.

### 5.3 Images

Sends the image to a multimodal LLM with an instruction to describe it
thoroughly, including all visible text. The description, which effectively
includes OCR, becomes `derived_text`.

- Providers: `openai` / `anthropic` / `google` / `ollama`
  (`CORTEX_IMAGE_PROVIDER`, default model `gpt-4o`)
- Metadata: `width`, `height`
- Enable: `CORTEX_IMAGE_PROVIDER=openai` plus `CORTEX_IMAGE_API_URL` and
  `CORTEX_IMAGE_API_KEY`

### 5.4 Sensor / time-series

Summarized into a text description. Metadata: `sensor_type`,
`data_point_count`, `sampling_interval_ms`.

### 5.5 Archives and unknown binaries

ZIP and TAR are recursed by the document processor when one is configured; Tika
unpacks the archive and extracts the text of its contents. Without a document
processor, the archive is stored as an opaque blob only. A truly opaque binary
yields no `derived_text` and will not appear in recall, but raw bytes are always
retained via `GET /v1/blobs/{id}`.

For large archives, recursion can produce a lot of text. If you want per-file
scoping, unpack client-side and ingest each file into its own scope.

### 5.6 The blob store

| Backend | Config |
|---|---|
| Local filesystem (default) | `<data_dir>/blobs`, nothing to configure |
| S3 / GCS / Azure | `CORTEX_BLOB_PROVIDER` plus provider creds (`CORTEX_BLOB_BUCKET`, endpoint, keys, optional SSE/KMS for S3) |

---

## 6. Configuration matrix: built-in vs opt-in

| Modality | Built-in? | External dependency | Enable with |
|---|---|---|---|
| Text / MD / CSV / HTML / JSON / XML | Yes | none | works out of the box |
| PDF / DOCX / PPTX / XLSX | No, opt-in | Tika server or Unstructured.io | `CORTEX_DOCUMENT_PROVIDER` |
| Images | No, opt-in | multimodal LLM API | `CORTEX_IMAGE_PROVIDER` |
| Audio | No, opt-in | ASR service | `CORTEX_AUDIO_PROVIDER` |
| Video | No, opt-in | ffmpeg plus image plus audio | `CORTEX_FFMPEG_PATH` / `CORTEX_VIDEO_PROVIDER` |
| Sensor | No, opt-in | summarizer LLM | sensor config |
| ZIP / TAR archives | Recursed if a doc processor is set | Tika, else stored-only | `CORTEX_DOCUMENT_PROVIDER` |
| Opaque binaries | Stored only | none | n/a |
| Blob store (S3/GCS/Azure) | Local by default | object store | `CORTEX_BLOB_PROVIDER` |

**Design implication, and the thing most likely to surprise you.** A fresh
instance ingests text immediately. To ingest PDFs, audio, video, or images you
must enable the relevant processor. If a processor for a modality is not
configured, **files of that type are stored as blobs but never become searchable
memory.** They upload successfully and then silently do not appear in recall.

**All `CORTEX_*` variables above are server-side.** On the hosted service you do
not set them and cannot set them from application code. If a client needs a
modality that is not enabled, that is a deployment question, not an integration
one. Do not build a client-side extraction workaround without asking first.

---

## 7. Worked example: ingesting and querying a PDF

```bash
# 1) upload the PDF bytes, get a blob id
curl -X POST $BASE/v1/blobs -H "Authorization: Bearer $KEY" \
  --data-binary @contract.pdf          # -> { "blob_id": "blob_..." }

# 2) remember it as an experience (routed by MIME to the document processor)
curl -X POST $BASE/v1/experience -H "Authorization: Bearer $KEY" \
  -H "X-Cortex-Actor: agent:acme" \
  -d '{ "scope":"org:acme/dept:legal/category:contracts", "modality":"document",
        "content":{ "kind":"blob_ref", "blob_id":"blob_..." } }'

# 3) ask across all contracts
curl -X POST $BASE/v1/answer -H "Authorization: Bearer $KEY" \
  -H "X-Cortex-Actor: agent:acme" \
  -d '{ "scope":"org:acme/dept:legal", "view":"descend",
        "question":"Which contracts auto-renew, and on what notice period?" }'
```

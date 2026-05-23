# ReadMemory Product Plan and Technical Roadmap

## 1. Product Positioning

ReadMemory is a verified memory layer for English reading notes.

It is not a reading app, dictionary, course platform, or general AI note-taking tool. The first version should help a user keep reading in their existing EPUB reader while ReadMemory records what was read, links notes back to the original text, and turns those notes into reviewable memory.

Core statement:

> Keep reading in your own tools. ReadMemory remembers the exact traces: progress, words, sentences, thoughts, and reviews.

## 2. V1 Scope

V1 supports English reading only.

Chinese support is deferred and should initially be limited to general reading notes, not language-learning workflows. Other languages are also deferred.

The practical V1 focus is reading notes:

- Reading progress: where the user started and stopped.
- Vocabulary notes: unknown English words found during reading.
- Sentence notes: English sentences worth saving or imitating.
- Thought notes: user reflections linked to an original text location.
- Review queue: lightweight daily review for saved words, sentences, and thoughts.
- Markdown export: daily or per-book notes suitable for Obsidian or any plain Markdown vault.

## 3. Target User

The early user is an English learner who already reads real English books and already has preferred tools, such as an EPUB reader, TTS or pronunciation practice workflow, Obsidian, Anki, or Markdown files.

This user does not need another closed reading environment. They need a reliable external system that can answer:

- Where did I stop reading?
- What did I learn from this section?
- Which words and sentences should I review?
- What thoughts did I have, and which source text caused them?
- Am I making measurable progress?

## 4. Product Principles

- Do not replace the reading experience. The user keeps using their existing EPUB reader.
- Manual input is acceptable in V1. The user can paste a quote or report progress in natural language.
- Use source text anchors instead of page numbers. EPUB page numbers are unstable across readers and layouts.
- Treat the database as the source of truth. AI memory should not be trusted as the primary store.
- Every important answer should be traceable to a record or source anchor.
- Keep daily capture lightweight. If logging feels like filling a form, the product fails.

## 5. Core Workflow

### 5.1 Import A Book

The user uploads an EPUB file.

ReadMemory extracts:

- Metadata: title, author, language, EPUB hash.
- Chapters and sections.
- Paragraphs and sentences.
- Word counts.
- Search index data.
- Stable location anchors.

Output:

- A book record.
- A searchable source-text index.
- Initial reading plan options based on target daily word count.

### 5.2 Record Reading Progress

The user reports a current location by pasting a quote or short paragraph:

```text
I read Animal Farm today and stopped at:
"Man is the only creature that consumes without producing."
```

ReadMemory locates the quote inside the indexed EPUB, stores the start and end anchors, estimates words read, and updates progress.

The answer should be grounded:

```text
Recorded: Animal Farm, Chapter 1.
Stopped at: "Man is the only creature that consumes without producing."
Estimated words read today: 1,320.
Next target: continue from this paragraph and read about 1,000 words.
```

### 5.3 Capture Vocabulary

The user sends unknown words:

```text
Words: ensconce, lantern, knacker
```

ReadMemory stores each word with context:

- Word.
- Lemma if available.
- Source book.
- Chapter or section.
- Original sentence.
- User meaning or AI-suggested contextual meaning.
- Review status.
- Next review date.

The review prompt should be contextual:

```text
In the Animal Farm sentence where "knacker" appears, what kind of person or role does it refer to?
```

### 5.4 Capture Sentences

The user saves a sentence:

```text
Sentence: Man is the only creature that consumes without producing.
```

ReadMemory links it to the book location and optionally creates an expression note:

- Why the sentence is useful.
- Pattern or structure.
- Imitation examples.
- Review schedule.

### 5.5 Capture Thoughts

The user records a thought:

```text
Thought: Old Major's speech feels like political mobilization.
```

By default, ReadMemory links the thought to the latest reading location. If confidence is low, it asks the user to confirm the source location.

Thought notes are the product's main long-term value. They should not become isolated chat messages. They should be attached to:

- Book.
- Chapter or section.
- Anchor quote.
- Nearby context.
- Date.
- Tags.

### 5.6 Generate Markdown Notes

ReadMemory can export daily logs:

```markdown
# English Reading Log - 2026-05-23

## Book
Animal Farm

## Progress
Chapter 1
Stopped at: "Man is the only creature that consumes without producing."

Estimated words read: 1,320

## Vocabulary
- ensconce
- lantern
- knacker

## Sentences
- Man is the only creature that consumes without producing.

## Thoughts
- Old Major's speech feels like political mobilization.

## Review Tomorrow
- Vocabulary: ensconce, lantern, knacker
- Sentence: Man is the only creature that consumes without producing.
```

## 6. MVP Feature List

Must have:

- EPUB upload and parsing.
- Book, chapter, paragraph, and sentence indexing.
- Quote-based location matching.
- Reading progress records.
- Vocabulary records with source sentence.
- Sentence bank records with source anchor.
- Thought notes linked to source anchor.
- Daily Markdown export.
- Simple review queue.

Should have:

- Weekly reading summary.
- Average daily word count.
- Next reading target based on recent pace.
- Basic semantic search over thoughts and sentences.
- Anki-compatible export for vocabulary and sentence cards.

Not in V1:

- Built-in EPUB reader.
- Full dictionary replacement.
- Full pronunciation scoring.
- Social features.
- Course system.
- Automatic monitoring of external readers.
- Chinese and multilingual reading-learning workflows.
- Zep/Graphiti integration as a required dependency.

## 7. Technical Architecture

### 7.1 High-Level Stack

Recommended V1 stack:

```text
Client / CLI / Bot Interface
        |
Application Service
        |
Structured Database
        |
EPUB Parser + Text Index + Anchor Resolver
        |
Markdown / Anki Exporters
        |
Optional AI Layer for parsing, summarization, and review generation
```

V1 can start local-first with SQLite. If the product needs multi-device sync or hosted collaboration later, migrate to Postgres.

### 7.2 Source Of Truth

Use a structured database for facts:

- Books.
- Source text units.
- Reading sessions.
- Vocabulary notes.
- Sentence notes.
- Thought notes.
- Review items.
- Exports.

The AI layer may help parse user input or generate explanations, but it must not be the authoritative memory store.

### 7.3 EPUB Processing

EPUB ingestion should produce normalized source units:

- Book.
- Chapter.
- Paragraph.
- Sentence.
- Token counts.
- Character offsets.
- Content hashes.

Location should rely on multiple anchors:

- EPUB CFI when available.
- Chapter ID.
- Paragraph index.
- Sentence index.
- Anchor quote.
- Before and after quote.
- Paragraph hash.
- Character offset.

This allows ReadMemory to re-locate notes even if exact EPUB layout changes.

### 7.4 Search And Matching

Use layered retrieval:

- Exact quote search for pasted source text.
- Fuzzy text matching for imperfect pasted quotes.
- Metadata filters for book, chapter, and date.
- Full-text search for words, sentences, and notes.
- Optional vector search for semantic thought retrieval.

The first version does not need a complex graph memory. Reliable exact and fuzzy matching matters more.

### 7.5 Review Scheduling

Start with a simple review scheduler:

- New item: review tomorrow.
- Correct: increase interval.
- Wrong or uncertain: reset interval.
- Dormant items: resurface weekly.

Later, adopt FSRS or Anki integration for better scheduling.

### 7.6 Markdown Export

Markdown should be treated as a first-class output format, not a secondary dump.

Useful export types:

- Daily reading log.
- Per-book reading index.
- Vocabulary list.
- Sentence bank.
- Thought notes.
- Weekly review.

The exporter should preserve stable IDs in comments or frontmatter so notes can be updated without duplicating content.

Example frontmatter:

```yaml
---
type: english-reading-log
date: 2026-05-23
book_id: animal_farm
session_id: session_20260523_001
---
```

## 8. Proposed Data Model

### Book

- id
- title
- author
- language
- epub_hash
- total_words
- created_at

### SourceUnit

- id
- book_id
- unit_type: chapter | paragraph | sentence
- chapter_index
- paragraph_index
- sentence_index
- text
- word_count
- char_start
- char_end
- content_hash
- epub_cfi

### Anchor

- id
- book_id
- source_unit_id
- anchor_quote
- before_quote
- after_quote
- char_offset
- confidence

### ReadingSession

- id
- book_id
- date
- start_anchor_id
- end_anchor_id
- words_read
- status: planned | partial | completed
- user_note
- created_at

### VocabularyNote

- id
- book_id
- anchor_id
- word
- lemma
- source_sentence
- user_meaning
- ai_context_meaning
- status: new | learning | familiar | mastered
- next_review_at
- created_at

### SentenceNote

- id
- book_id
- anchor_id
- sentence
- reason_saved
- pattern_note
- imitation_examples
- next_review_at
- created_at

### ThoughtNote

- id
- book_id
- anchor_id
- thought_text
- related_quote
- tags
- created_at

### ReviewItem

- id
- item_type: vocabulary | sentence | thought
- item_id
- due_at
- interval_days
- ease
- last_result: correct | wrong | uncertain

## 9. AI Responsibilities

AI should help with:

- Parsing natural-language check-ins.
- Suggesting contextual word meanings.
- Locating likely source anchors when the quote is incomplete.
- Generating imitation sentences.
- Summarizing daily and weekly reading activity.
- Turning notes into review prompts.
- Searching and summarizing previous thoughts with citations.

AI should not:

- Invent reading progress.
- Store critical facts only in chat memory.
- Answer source-location questions without retrieved records.
- Treat semantic matches as exact evidence.

Hard rule:

> If ReadMemory cannot find a reliable record, it should say so and distinguish inference from fact.

## 10. Technical Roadmap

### Phase 0: Documented Prototype

Goal: validate the workflow with files and scripts before building a full app.

Deliverables:

- Product spec.
- Sample EPUB ingestion script.
- SQLite schema draft.
- Example Markdown outputs.
- Manual test with one public-domain English EPUB.

### Phase 1: Local MVP

Goal: make the reading-note loop usable locally.

Deliverables:

- Local database.
- EPUB upload or import command.
- Quote-based progress logging.
- Vocabulary, sentence, and thought capture.
- Daily Markdown export.
- Basic review queue.

Possible interface:

- CLI.
- Local web UI.
- Hermes command bridge.

### Phase 2: Reliable Note System

Goal: improve traceability and reduce wrong matches.

Deliverables:

- Multi-anchor resolver.
- Confidence score for quote matching.
- Duplicate detection.
- Source citation in every answer.
- Per-book note pages.
- Weekly reading report.

### Phase 3: Review And Export Integrations

Goal: make captured notes useful over time.

Deliverables:

- Anki-compatible export.
- FSRS-style scheduling or Anki sync.
- Obsidian vault folder export.
- Review prompts for words, sentences, and thoughts.
- Reading pace projection.

### Phase 4: Semantic Retrieval

Goal: help users rediscover their thoughts and patterns.

Deliverables:

- Embeddings for thought and sentence notes.
- Hybrid retrieval with metadata filters.
- Query answers with linked source records.
- Topic clustering for recurring ideas.

### Phase 5: Optional Memory Graph

Goal: add relationship memory only after the basic database is useful.

Deliverables:

- Entity and theme extraction.
- Links between books, characters, themes, words, sentences, and thoughts.
- Optional Zep/Graphiti or graph database experiment.
- Temporal changes in learning state.

This should not replace the structured database.

## 11. Success Metrics

Early product metrics:

- Number of active books imported.
- Number of reading sessions logged per week.
- Percentage of notes with verified source anchors.
- Vocabulary review completion rate.
- Sentence review completion rate.
- Average quote-location confidence.
- Weekly reading word count.
- Reduction in missed reading days.

Qualitative success:

- The user can find where a thought came from.
- The user can resume reading without searching manually.
- The user sees progress without leaving their reading workflow.
- The user trusts the system because answers include evidence.

## 12. Key Risks

- Quote matching fails on different EPUB versions.
- Daily logging becomes too much work.
- AI generates plausible but unsupported notes.
- Markdown export creates duplicate or messy files.
- Review queue becomes a dumping ground instead of a habit.
- Scope expands into a full language-learning app too early.

Mitigations:

- Use multiple anchors and confidence scores.
- Keep natural-language input simple.
- Store facts in the database before AI summarization.
- Add stable IDs to exported Markdown.
- Keep daily review small.
- Hold the V1 boundary: English reading notes first.

## 13. Recommended First Build

Build the smallest local loop:

1. Import one English EPUB.
2. Paste a stop quote and record progress.
3. Save words, sentences, and thoughts against the latest anchor.
4. Export one daily Markdown reading log.
5. Generate tomorrow's review list.

If this loop feels useful for two weeks of real reading, then add semantic search and richer integrations.

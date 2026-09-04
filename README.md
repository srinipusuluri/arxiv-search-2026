# ArXiv Semantic Research Radar

A single-file research dashboard for scanning [arXiv](https://arxiv.org) by topic. Pick topics (or type your own phrases), search the live arXiv API, and get ranked papers with relevance scoring, matched terms, abstracts, and direct links to the real PDF on arxiv.org.

![status](https://img.shields.io/badge/dependencies-none-7dffb2) ![status](https://img.shields.io/badge/python-stdlib%20only-22e1ff)

## Quick start

```bash
git clone https://github.com/srinipusuluri/arxiv-search-2026.git
cd arxiv-search-2026
python3 serve.py
```

Then open **http://localhost:8787/arxiv_semantic_research_radar.html** and hit **Search arXiv**.

No `pip install`, no `npm install`, no API key — `serve.py` uses only the Python standard library.

## Why you need `serve.py`

The public arXiv API sends **no `Access-Control-Allow-Origin` header**. That means no browser can call it directly from a web page — the request is blocked by CORS before arXiv ever sees it. This is the single most common reason a hand-rolled arXiv dashboard "just doesn't return anything."

`serve.py` solves it by serving the page *and* relaying the API call from the server side, where CORS does not apply:

```
GET /arxiv?url=<url-encoded arXiv API url>
```

It only forwards `https://export.arxiv.org` — any other host gets a `403`, so it stays a single-purpose relay rather than an open proxy.

You can still open the `.html` file directly from disk. The page detects it isn't being served and falls back to public read-only CORS proxies, retrying each twice. Those proxies are free, heavily rate-limited, and go down without notice, so **search will be intermittent in that mode**. The relay is the dependable path.

Change the port with `PORT=9000 python3 serve.py`.

## Features

- **79 topic chips**, sorted A–Z, spanning two tracks: applied AI (LLMs, RAG, agents, evaluation, AI security
  and governance) and quantum (quantum machine learning, variational circuits, error correction, annealing,
  NISQ, post-quantum cryptography). `LLM`, `RAG` and `MCP` are preselected on load.
- **Phrase-aware search.** Commas separate terms, so `Large Language Models` stays one phrase instead of three unrelated words.
- **Server-side date filtering** via a `submittedDate:[…]` range in the query, rather than over-fetching and discarding client-side.
- **Relevance scoring** that weights a title hit above an abstract hit above a category hit, blended with a freshness curve. Matched terms are shown as chips on each card.
- **Real PDF links.** Every card links to `arxiv.org/abs/…` and `arxiv.org/pdf/…`, using the versioned arXiv id (`2609.01046v1`) that arxiv.org resolves.
- Filter by **category** — including `quant-ph` alongside the `cs.*` categories — and by date window; sort by relevance or date, expand abstracts inline.
- Vibrant glass-and-aurora UI that fully respects `prefers-reduced-motion`.

## How search is built

Terms are OR'd inside a parenthesised group, then the category and date window are AND'd on. The parentheses matter — without them `AND` binds tighter than `OR`, and the category filter would silently apply to the last term only:

```
(all:"agentic RAG" OR all:"prompt injection")
  AND cat:cs.AI
  AND submittedDate:[202506040000 TO 202609042359]
```

Requests are sorted by `submittedDate` when a date window is set, and by `relevance` for all-time searches.

## Files

| File | Purpose |
| --- | --- |
| `arxiv_semantic_research_radar.html` | The entire app — markup, styles and logic in one file, no build step and no external assets. |
| `serve.py` | Static server + CORS relay for the arXiv API. Standard library only. |

## Customising

- **Topics** — edit the `TOPICS` array. It stays grouped by theme for readability; the chips render A–Z regardless.
- **Preselected topics** — edit `PREFILL`. Chips are selected on load, but the search deliberately waits for a click, so a reload never spends a rate-limited proxy request.
- **Routes** — edit `ROUTES` to point at a relay you control. The local relay is tried first whenever the page is served over http.

## Requirements

Python 3.7+ and any modern browser. Nothing else.

## Notes

arXiv asks that automated clients stay under roughly one request every three seconds. Normal interactive use is well inside that.

Paper metadata and PDFs belong to their authors and to arXiv, under arXiv's [Terms of Use](https://arxiv.org/help/api/tou). This tool only searches and links; it stores nothing.

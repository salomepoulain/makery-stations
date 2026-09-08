# Note-Taking System Obsidian Vault

Your personal knowledge vault for organizing learning, capturing thoughts, and maintaining semantic connections across sources.

## Overview

This is a **3-layer note-taking system** designed to:
- Process information from diverse sources without manual linking overhead
- Capture your actual thinking (not busy work)
- Enable AI to understand what you know, what you're fuzzy on, and where ideas connect
- Scale from simple personal notes to complex cross-domain knowledge graphs

**Core philosophy**: You write only when you have genuine thoughts. AI handles the structural work. Semantic clustering (via embeddings, eventual UMAP visualization) discovers connections automatically.

## The 3 Layers

Think of processing any source (book, course, paper, tutorial) through three levels of resolution:

### Layer 1: Raw Sources
**What it is**: The original material in full resolution.
- PDFs, lecture transcripts, video files, full course materials
- Stored verbatim, rarely opened directly
- Serves as ground truth and reference

**Why this layer**: You need the original if you want to verify a claim, find exact formulas, or revisit context. Don't discard it.

**Example**:
```
sources/raw/
├── optimization-course-chapter-5.pdf
├── optimization-lecture-5-transcript.txt
└── optimization-notes-from-professor.md
```

### Layer 2: AI-Generated Summaries
**What it is**: Automated extraction of key concepts from Layer 1.
- Main ideas, formulas, connections to previous/next topics
- Typically 300-500 words per chapter/section
- Searchable and embeddable (later, for vector search)
- Links back up to Layer 1 and down to your thoughts

**Why this layer**: Saves you from writing boring extraction notes. AI does the structural work so you can focus on genuine thinking.

**Who writes it**: AI (via a processing script)

**Example**:
```markdown
<!-- sources/summaries/optimization-chapter-5.md -->
---
type: course-chapter
source: sources/raw/optimization-course-chapter-5.pdf
---

# Chapter 5: Second-Order Methods

## Key Concepts
- Newton's method uses curvature information (Hessian)
- Advantages: fewer iterations, better convergence near optimum
- Disadvantages: computing/storing Hessian is expensive
- Quasi-Newton methods approximate Hessian (BFGS, L-BFGS)

## Formulas
- θ_{t+1} = θ_t - H^{-1} ∇L(θ_t)
- Requires: O(n²) space for Hessian

## Connections
- Builds on: [[gradient-descent]], [[learning-rate-scheduling]]
- Leads to: [[optimization-in-deep-learning]]
```

### Layer 3: Your Thoughts (Atomic Notes)
**What it is**: Your reactions, connections, confusions, and realizations.
- Individual concept notes (like Zettelkasten cards)
- Written by YOU when you have a genuine thought
- Where actual learning happens
- Smallest unit: one idea, reusable, standalone

**Why this layer**: This is your brain. AI doesn't write this. You only write when something clicks, confuses you, or connects unexpectedly.

**Who writes it**: You

**Example**:
```markdown
<!-- notes/atomic/newton-method-is-betting-on-the-terrain.md -->

# Newton's Method Is Betting On The Terrain

Regular gradient descent blindly steps downhill. Each step, you ask "which direction goes down RIGHT HERE" and step that way.

Newton's method says: "what if I LOOK at the shape of the valley itself?"

If the ground curves steeply on the left and gently on the right, you can predict where the bottom actually is and step there directly. That's what the Hessian does — it's a map of how curvy the landscape is.

But there's a cost: making that map of curvature is expensive. You trade off fewer steps (good) vs. expensive computation per step (bad).

## When to use
- Near the optimum (curvature info is accurate)
- When step cost doesn't matter (small problems, offline training)

## When NOT to use
- Large neural networks (Hessian is too big)
- Far from optimum (bad curvature prediction)

## Connection I didn't expect
This feels like the difference between [[binary-search]] (Newton, uses midpoint info) vs. [[linear-search]] (gradient, pure direction). Both valid strategies, different assumptions.

Sources: [[optimization-chapter-5]]
```

---

## Atomic Notes & Maps of Content (MOCs)

### Atomic Notes
Individual concept cards. The output of Layer 3.
- One clear idea per note
- Standalone (readable without context)
- Linked to other notes and source hubs
- Searchable by embedding (future phase)

### Maps of Content (MOCs)
Topic dashboards that organize atomic notes.

An MOC is a single note per major topic that says:
- "Here are my atomic notes about [topic]"
- "These I understand well"
- "These I'm still fuzzy on"
- "Here are the sources they came from"
- "What gaps exist"

**Why MOCs matter**: Later, when you ask Claude a question, Claude reads your MOC and knows your knowledge state. It adjusts explanation depth accordingly.

**Example MOC**:
```markdown
<!-- maps/optimization-knowledge.md -->

# What I Know About Optimization

## Well Understood
- [[gradient-descent-blindfolded]] — intuition is rock solid
- [[learning-rate-scheduling]] — use in projects regularly
- [[momentum-and-acceleration]] — understand the physics

## Partially Understood
- [[newton-method-betting-on-terrain]] — works but expensive
- [[adaptive-methods-adam-vs-adadelta]] — when to use which?

## Still Fuzzy
- Second-order methods in deep learning — never implemented
- Distributed optimization — read one paper, didn't stick

## Sources
- [[optimization-course]] (Chapters 1-8)
- [[num-optimization-textbook]] (Chapters 3, 5, 7)
- Blog post on adaptive methods (need to find link)

## Gaps
- No notes on trust-region methods
- Nothing on bandit optimization
- Sparse optimization barely touched
```

---

## Folder Structure

Your vault lives on external storage. Symlinks point to it from various locations.

```
vault/                                    (root of knowledge)
│
├── sources/                               
│   ├── raw/                              (Layer 1: originals)
│   │   ├── book-chapter.pdf
│   │   ├── lecture-transcript.txt
│   │   └── video-notes.md
│   │
│   └── summaries/                        (Layer 2: AI extracts)
│       ├── book-chapter-summary.md
│       └── lecture-summary.md
│
├── notes/                                 (Layer 3: your thoughts)
│   └── atomic/
│       ├── gradient-descent-blindfolded.md
│       ├── learning-rate-scheduling.md
│       └── ... (individual concept cards)
│
├── maps/                                  (MOCs: topic overviews)
│   ├── optimization-knowledge.md
│   ├── neural-networks-knowledge.md
│   └── math-foundations-knowledge.md
│
└── inbox/                                 (temporary, unprocessed)
    ├── random-thought-from-lecture.md
    └── screenshot-to-process.png

```

**Key principles**:
- `sources/raw/` is write-once, read-rarely (archive)
- `sources/summaries/` is auto-generated, organization mirrors raw/ 
- `notes/atomic/` grows organically as you learn
- `maps/` you create/update manually (or AI helps generate)
- `inbox/` is transient (stuff to process later)

---

## Storage & Access

### Why External Disk
- **Portability**: Plug in, work, unplug. Vault travels with you
- **Single copy**: No sync conflicts, no "which version is current"
- **Backup-friendly**: Back up one external disk, not scattered files
- **Project independence**: Same vault accessible from multiple projects

### Symlink Strategy

Real data lives on external disk:
```
/Volumes/ExternalDisk/knowledge-vault/
```

Your Mac has pointers to it:
```
~/.notes/vault → /Volumes/ExternalDisk/knowledge-vault/
./projects/myproject/.vault → ~/.notes/vault
```

**How it works**: When you access `~/.notes/vault/notes/atomic/`, the system resolves the symlinks and reads from the external disk.

**If disk is unplugged**: Symlinks break (Obsidian says "vault not found"), but data is safe on disk. Plug it back in, everything works again.

**If you delete a project folder**: The symlink goes away, but the actual vault on the external disk is untouched.

---

## Currently Implemented vs. Future

### NOW (Phase 1: Foundation)
- Folder structure defined
- 3-layer workflow documented
- Atomic notes concept ready
- MOCs for topic organization
- External disk + symlink setup

**What you do**: Drop sources in Layer 1, write your Layer 3 thoughts, organize with MOCs.

### FUTURE (Phase 2: Source Integration)
- Zotero integration (academic papers)
- Auto-creation of Layer 2 summaries from papers
- Annotation extraction from Zotero highlights
- Obsidian Zotero plugin for seamless workflow

### FUTURE (Phase 3: Search)
- Ollama embeddings (semantic understanding of notes)
- SQLite vector database (stores embeddings)
- Vector search ("find notes similar to this query")
- Intent classification (focused query vs. multi-topic query vs. comparison)

### FUTURE (Phase 4: Visualization)
- UMAP 3D knowledge map (notes cluster by semantic similarity)
- Monte Carlo UMAP (uncertainty visualization — fuzzy notes are bridge concepts)
- Timeline slider (watch knowledge evolve week by week)
- Interactive query walking (watch AI navigate your knowledge in real-time)

---

## How Claude Uses This System

Claude (in any of your projects) will:

1. **Read your MOCs** to understand what you know well vs. what's fuzzy
2. **Reference atomic notes** as primary context (your language, your connections)
3. **Trace back to Layer 2 summaries** for structured overviews
4. **Access Layer 1 sources** only if deep verification or formulas are needed

This is why structure matters: unstructured notes are hard to search. Organized notes with clear layers let AI find exactly the right level of detail.

Later, when Phase 3 (embeddings) is implemented, Claude will also use **semantic search** to find relevant notes automatically, even if you didn't manually link them.

---

## Quick Reference: File Naming

No strict rules, but a consistent pattern helps:

**Atomic notes**: `kebab-case-describing-the-idea.md`
- `gradient-descent-blindfolded.md`
- `why-batch-norm-works.md`
- `comparing-adam-vs-sgd.md`

**Source summaries**: `source-type-name-identifier.md`
- `book-deep-learning-chapter-3.md`
- `course-stanford-cs231n-lecture-5.md`
- `paper-transformer-attention-2017.md`

**MOCs**: `topic-knowledge.md`
- `optimization-knowledge.md`
- `statistics-knowledge.md`

**Inbox**: anything goes (temporary)

---

## Questions or Gaps?

Refer ask the user to give the original-conversation for the full design discussion and thinking behind each layer.

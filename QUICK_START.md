# Quick Start Guide for Writers

This guide is for **Brad** (the writer) to start using the AI Writers' Room.

## What This System Does

You provide a sketch idea. The AI Writers' Room (10 AI agents) will:
1. Generate multiple pitch variations
2. Let you pick your favorite
3. Build a detailed beat sheet
4. Write a full script draft
5. Revise based on feedback
6. Deliver a polished sketch

You review and approve at 3 checkpoints. The whole process takes about 10-15 minutes.

---

## First-Time Setup (One Time Only)

### 1. Create Your Show

Open Terminal and navigate to this folder, then run:

```bash
./new-show.sh "Your Show Name"
```

Example:
```bash
./new-show.sh "Office Chaos"
```

This creates a folder at `Shows/office_chaos/` with:
- `show_bible.md` - Your show's style guide (edit once)
- `creative_prompt.md` - Where you write sketch ideas (edit for each sketch)
- `write.sh` - The command to run the AI writers
- `output/` - Where finished scripts appear

### 2. Fill Out Your Show Bible

Open `Shows/your_show/show_bible.md` in any text editor.

This defines your show's voice, tone, and boundaries. Fill in:
- What makes your show unique
- Comedy styles you embrace (and avoid)
- Topics that work (and don't)
- Reference sketches you love

**You only need to do this once per show.** The AI will use this for every sketch.

---

## Writing a New Sketch

### Step 1: Write Your Idea

Open `Shows/your_show/creative_prompt.md` and write your sketch idea:
- What's the core concept?
- Any must-have jokes or moments?
- Characters you envision?

Don't worry about being complete - the AI will expand on your idea.

### Step 2: Run the Writers' Room

From your show folder:
```bash
cd Shows/your_show
./write.sh
```

Or from the project root:
```bash
./Shows/your_show/write.sh
```

### Step 3: Review at Checkpoints

The system will pause 3 times for your input:

| Checkpoint | What You Do |
|------------|-------------|
| **1. Pitch Selection** | Read the generated pitches, pick your favorite(s) |
| **2. Beat Sheet** | Review the structure, approve or request changes |
| **3. Final Script** | Review the finished script, approve or request revisions |

At each checkpoint, you'll see the content and be asked to approve or provide notes.

### Step 4: Get Your Script

When complete, your script appears in `Shows/your_show/output/` with:
- `script.txt` - The finished script
- `beat_sheet.txt` - The structural outline
- `qa_report.txt` - Quality notes

---

## Quick Reference

| Task | Command |
|------|---------|
| Create new show | `./new-show.sh "Show Name"` |
| Write a sketch | `cd Shows/your_show && ./write.sh` |
| Test without approvals | `./write.sh --mock-checkpoints` |
| Validate setup | `./write.sh --dry-run` |
| See all options | `./write.sh --help` |

---

## Folder Structure

```
brads_show/
├── Shows/
│   └── your_show/           <- Your show lives here
│       ├── show_bible.md    <- Edit once: show's style guide
│       ├── creative_prompt.md <- Edit each time: sketch idea
│       ├── write.sh         <- Run this to write
│       └── output/          <- Finished scripts appear here
├── new-show.sh              <- Creates new shows
└── QUICK_START.md           <- This file
```

---

## Troubleshooting

### "Template placeholders" warning
You'll see this if `show_bible.md` or `creative_prompt.md` still has `[BRACKETED TEXT]` in it. Edit the file to replace these with your actual content.

### Script errors
Ask Reed. He handles all the technical stuff.

### The AI isn't following my show's style
Make sure your `show_bible.md` is detailed enough. The more specific you are about what you want (and don't want), the better the results.

---

## For Reed: Enabling Observability

To see what the AI agents are doing, enable LangSmith tracing:

1. Get an API key from https://smith.langchain.com
2. Create a `.env` file in the project root (copy from `.env.example`)
3. Set these values:
   ```
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=your-api-key-here
   LANGCHAIN_PROJECT=sketch-comedy-agents
   ```
4. Run any `write.sh` - all LLM calls will appear in the LangSmith dashboard

This shows every agent's prompts, responses, timing, and token usage.

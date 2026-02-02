# How to Create a Skit

This guide walks you through creating a new sketch using our AI writers' room system.

**You provide the creative direction. Reed handles the technical side.**

---

## Quick Overview

Creating a skit follows this pattern:

1. **Reed** creates a new show folder for you (one-time setup per show)
2. **You** fill in your show's style guide
3. **You** write a creative prompt describing your sketch idea
4. **Reed** runs the system
5. **Together** you review pitches and pick your favorite
6. **Together** you review the story structure and approve it
7. **The system** drafts, reviews, and polishes the script
8. **Together** you do a final review and approve the finished script

---

## Step 1: Set Up Your Show Folder (One Time Per Show)

Each show or skit collection gets its own folder. This keeps everything organized.

### Ask Reed to create your show:

Tell Reed the name of your show, and he'll set it up for you. For example:
> "Hey Reed, can you create a new show called 'Office Chaos'?"

### What you'll get:

```
Shows/
└── office_chaos/
    ├── show_bible.md       (your show's style guide - you edit this)
    ├── creative_prompt.md  (your sketch idea - you edit this)
    ├── write.sh            (runs the system - Reed handles this)
    └── output/             (where finished scripts go)
```

You only need to set this up once per show. After that, you'll just edit the files inside your show's folder.

---

## Step 2: Create Your Show Bible (One Time Per Show)

The **Show Bible** defines your show's identity, tone, and rules. You only need to do this once per show—not for every sketch.

### What goes in the Show Bible:

| Section | What to Write |
|---------|---------------|
| **Show Identity** | What's your show about? Who's the audience? What's the vibe? |
| **Tone & Style** | What kinds of comedy do you love? What do you avoid? |
| **Content Guidelines** | Topics you want to explore. Topics that are off-limits. Language/content boundaries. |
| **Reference Points** | Sketches you love that capture your show's spirit. |
| **Character Types** | The kinds of characters that work for your show. |

### How to do it:

1. Open `Shows/your_show_name/show_bible.md`
2. Look for all the `[BRACKETED TEXT]` - these are the parts you fill in
3. Replace each bracketed section with your own content
4. Leave the section headers as they are
5. Save the file

**Tip:** The template includes helpful prompts in each section. Just replace the bracketed text with your answers.

---

## Step 3: Write Your Creative Prompt (For Each New Sketch)

The **Creative Prompt** is where you describe your sketch idea. This is what you'll fill out every time you want to create a new sketch.

### What goes in the Creative Prompt:

| Section | What to Write |
|---------|---------------|
| **Core Idea** | Your sketch concept in 1-3 sentences. What's the situation? What's funny about it? |
| **What Sparked This** | Where did the idea come from? This helps capture your intent. |
| **Must Include** | Specific moments, lines, or elements you definitely want. |
| **Character Types** | Who's in this sketch? What are they like? |
| **Setting** | Where does this take place? |
| **Tone** | Is this more grounded? Absurd from the start? Slow burn? |
| **What to Avoid** | Anything you specifically don't want. |

### How to do it:

1. Open `Shows/your_show_name/creative_prompt.md`
2. Look for the `[BRACKETED TEXT]` sections
3. Fill in **Core Idea** (required) and any other sections that matter to you
4. Delete sections you don't need - it's okay to leave them out
5. Save the file
6. Let Reed know you're ready

**Tip:** You don't have to fill in every section. The only required part is the **Core Idea**. Add more details if you have a clear vision; leave sections blank if you want more creative freedom in the pitches.

---

## Step 4: The Pitch Review (Checkpoint 1)

After Reed runs the system, you'll receive **four different pitch concepts** based on your creative prompt.

### What you'll see:

Each pitch includes:
- A title
- A logline (one-sentence summary)
- The main characters
- The central "game" of the sketch (the repeating funny pattern)
- A brief outline of how it escalates

### What you do:

Review all four pitches with Reed and decide:
- **Pick one** to move forward with
- **Combine elements** from multiple pitches
- **Request new pitches** if none of them hit the mark

Your feedback gets passed back to the system to guide the next stage.

---

## Step 5: The Story Structure Review (Checkpoint 2)

Once a pitch is selected, the system develops a detailed **beat sheet**—a scene-by-scene breakdown of the sketch.

### What you'll see:

- Opening beat (how the sketch starts)
- Each escalation beat (how the funny grows)
- The turn/twist (if any)
- The button (how it ends)
- Key dialogue moments flagged

### What you do:

Review the beat sheet with Reed and provide feedback:
- Does the escalation make sense?
- Is the ending satisfying?
- Are there beats you want to add, remove, or reorder?
- Any specific jokes or moments you want included?

Once you approve (with or without notes), the system moves to drafting.

---

## Step 6: Drafting & Internal Review

This stage happens automatically. The system:

1. **Drafts** the full script based on the approved beat sheet
2. **Reviews** the draft (checking jokes, dialogue, pacing, formatting)
3. **Revises** based on internal feedback (up to 3 revision cycles)
4. **Polishes** the final draft

You don't need to do anything during this stage. Reed will let you know when it's ready for final review.

---

## Step 7: Final Review (Checkpoint 3)

You'll receive the completed script for final approval.

### What you'll see:

- The full formatted script
- A summary of changes made during revision
- Quality notes from the internal review

### What you do:

Read through the script with Reed and decide:
- **Approve** - The script is ready
- **Request changes** - Specific notes for another revision pass
- **Start over** - If it's not working, go back to pitches with a refined prompt

---

## Your Files Summary

| File | When to Edit | Purpose |
|------|--------------|---------|
| `Shows/<your_show>/show_bible.md` | Once per show (update occasionally) | Defines your show's identity and rules |
| `Shows/<your_show>/creative_prompt.md` | Before each new sketch | Describes your sketch idea |

---

## Tips for Great Results

### Write specific creative prompts

**Vague:** "A sketch about a restaurant"

**Specific:** "A sketch about a waiter who treats every table like they're on a cooking competition show, complete with dramatic eliminations and judge commentary"

The more specific your starting point, the better the pitches.

### Include "must haves" when you have a vision

If there's a specific joke, line, or moment you definitely want, put it in the creative prompt. The system will work to include it.

### Don't over-specify if you want surprises

If you only have a loose idea and want to see creative interpretations, keep the prompt short. Let the pitches surprise you.

### Update your show bible as you learn

After creating a few sketches, you'll discover what works for your show. Update the show bible to capture those learnings.

---

## Example Workflow

### Starting a New Show (One Time)

Brad wants to create a sketch comedy show called "Office Chaos."

1. Brad tells Reed: "I want to start a new show called Office Chaos"
2. Reed creates the show folder
3. Brad opens `Shows/office_chaos/show_bible.md` and fills in the show's style guide
4. Show is ready for sketches

### Creating a New Sketch

**Monday:** Brad has an idea about a DMV employee who treats the waiting room like an exclusive nightclub.

1. Brad opens `Shows/office_chaos/creative_prompt.md`
2. Brad writes the core idea and a few must-haves
3. Brad tells Reed: "New sketch ready in office_chaos"
4. Reed runs the system

**Tuesday:** Reed shares four pitches with Brad.

5. Brad and Reed review the pitches together
6. Brad likes pitch #2 but wants the ending from pitch #4
7. Reed enters the feedback

**Wednesday:** Reed shares the beat sheet.

8. Brad and Reed review it together
9. Brad approves with one note: "Make the bouncer character more over-the-top"
10. Reed enters the feedback and starts the draft

**Thursday:** The script is ready.

11. Brad and Reed do final review
12. Brad approves the script
13. Final script saved to `Shows/office_chaos/output/`

---

## Questions?

If anything is unclear or you run into issues, just ask Reed. He handles all the technical stuff so you can focus on being funny.

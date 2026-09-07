---
name: human
description: Write or repair any Hebrew text so it sounds like Ariel Aizenshtat and not like an AI. Use whenever text is being produced for his audience or in his name - Facebook post, comment, WhatsApp message, email, landing page, video script, presentation, client document - and whenever a draft needs to be checked or de-slopped before delivery. Trigger phrases include "תכתוב בקול שלי", "שיישמע כמוני", "תנקה את זה מ-AI", "human", "AI slop". Differentiator - measured voice profile from 123 real posts plus a deterministic checker script, not a tone note.
---

# human

Two jobs: write new text in Ariel's voice, or repair existing text until it passes. Both end at the same gate, `scripts/check.py`.

Never deliver text that has not passed the checker.

## Step 0 - state check

```bash
python3 scripts/check.py --self-test    # confirms the checker runs
```

Corpus and profile live in `references/`. Read them in this order:
- `references/voice-profile.md` - the measured voice (openings, closings, punctuation, modes). **Always read before writing.**
- `references/ai-patterns.md` - the forbidden list. Read when repairing text, or when unsure whether a construction is a tell.
- `references/corpus.md` - 123 real posts. Read when you need a live example of a specific mode, or when writing a long personal post.

## Writing

1. **Pick the mode** from `voice-profile.md` section 6: enthusiastic, annoyed, selling, personal story, comment reply. The mode decides structure, not just tone.
2. **Open like him.** Default: `טוב` alone on a line, then `אז`. Other real openers are listed in the profile. Never open with a summary of what the post will contain.
3. **Write in lines, not paragraphs.** One idea per line, ~8 words, no period at the end. Line break replaces comma and period.
4. **Use the connecting hyphen** `מילה-מילה` with no spaces, 2-4 times, where a comma or colon would go. This is the single strongest marker.
5. **One or three exclamation marks.** Never two.
6. **One real detail** that only he could write: price, hour, tool name, a person's name, a number.
7. **Stretch one letter** in an enthusiastic post (`מטורףףף`).
8. **Close** with a request for opinion, `הקישור בתגובה הראשונה`, or a short sign-off (`תהינו!`, `צ׳או`, `יאללה`). On Friday add `שבת שלום` and sign `אריאל!`.
9. Run the gate.

## Repairing existing text

Works on his drafts, on another agent's output, and on text from any other skill in this repo.

1. Run the gate first to get the finding list:
   ```bash
   python3 scripts/check.py draft.txt
   ```
2. Fix in this order, because each fix changes the next count:
   - delete every forbidden word and phrase (`ai-patterns.md`)
   - break negative parallelisms (`לא רק X אלא גם Y`, `זה לא X, זה Y`) into two plain statements
   - replace em dashes and commas with the connecting hyphen where the sentence allows
   - delete the closing summary paragraph entirely, do not rewrite it
   - split long lines
3. Re-run the gate. Repeat until it passes.
4. If a rule cannot pass without breaking the meaning, say so explicitly in the reply instead of shipping a near-miss.

## The gate

```bash
python3 scripts/check.py post.txt          # file
pbpaste | python3 scripts/check.py -       # stdin
python3 scripts/check.py post.txt --json   # machine readable
```

Exit code 0 passes, 1 fails. Output lists each violation with its line number and the measured voice metrics against target.

The checker catches mechanical tells only. It cannot see a fake anecdote, a borrowed opinion, or a structure copied from a copywriting template. Read the result aloud before delivering; if it is not a sentence he would say, rewrite it even when the checker is green.

## Hard limits

- Never invent a biographical fact, a number, a price, a date, or a client name. Ask instead.
- **Polite refusal has no sample in the corpus.** Do not write one in his name until a real sample exists.
- Long personal posts (childhood, family, autism, bullying) carry real disclosures. Draft, then hand to him for approval before anything is sent or published.
- 2024-era posts in the corpus are marked `ERA-2024`. They are the voice he abandoned. Never imitate them.

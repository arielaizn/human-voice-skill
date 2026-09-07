---
name: human-corpus
description: Collect more of Ariel's real posts from Facebook and update the voice profile that the `human` skill reads. Use when he says "תסרוק עוד פוסטים", "תרענן את הקורפוס", "גל נוסף", or when the voice profile is missing a period or a mode (for example a polite refusal). Differentiator - browser collection procedure with Facebook's rate-limit behaviour documented; it feeds `human`, it does not write copy.
---

# human-corpus

Adds real posts to `../human/references/corpus.md` and updates `../human/references/voice-profile.md`.
Requires the Claude in Chrome extension connected to the browser profile where Facebook is logged in. Never log in on his behalf.

## Coverage so far

Read the coverage table at the end of `../human/references/voice-profile.md` before starting. Collect a period that is still marked as missing; do not re-scan a covered one.

## Procedure

1. **Open his profile** `facebook.com/profile.php?id=61561338582755`. If a login form appears, stop and ask him to log in.
2. **Jump to the target period.** Click `Filters` next to the Posts heading, set `Go to:` year and month, then `Done`. The feed lands on that month and continues backwards in time from there.
3. **Inject the collector** (dedupe against what the corpus already holds, so only new posts come back):
   ```javascript
   window.__c=new Map();
   window.__expand=()=>[...document.querySelectorAll('div[role="button"],span[role="button"]')]
     .filter(b=>/^\s*See more\s*$/.test(b.innerText||'')).forEach(b=>{try{b.click()}catch(e){}});
   window.__harvest=()=>{document.querySelectorAll('[data-ad-rendering-role="story_message"]').forEach(m=>{
     const t=(m.innerText||'').trim(); if(t.length<10) return;
     let e=m,a=''; for(let i=0;i<12&&e;i++){const p=e.querySelector&&e.querySelector('[data-ad-rendering-role="profile_name"]');
       if(p){a=(p.innerText||'').trim();break} e=e.parentElement}
     if(a && a!=='Ariel Ai') return;                    // his posts only
     window.__c.set(t.slice(0,50), t.slice(0,1400));
   }); return window.__c.size};
   ```
4. **Scroll with the real wheel**, `computer scroll` at the feed, 10 ticks, wait 4 seconds, then call `__expand(); __harvest()`. Repeat.
5. **Dump** by replacing the page body with a `<pre>` holding the collected text and calling `get_page_text`. The tool truncates ordinary JS results at ~1.5KB, so this is the only reliable way to extract a batch.
6. **Append** to `corpus.md` with the date of each post, run the numbers again, and update `voice-profile.md`: what strengthened, what is new, what contradicts an earlier wave. Then update the coverage table.

## Failure modes

- **`window.scrollTo` and Page-Down do not trigger Facebook's loader.** Only real wheel events do. If the height stops growing while skeleton cards sit at the bottom, that is the loader, not the end of the timeline.
- **Rate limit after roughly 20 minutes of scraping.** Skeleton cards stop resolving on every surface: the feed, the filtered feed, and the activity log. Waiting inside the session does not help. Stop, tell him, and resume in half an hour to an hour.
- **A stalled month is not an empty month.** Verify with the activity log `facebook.com/61561338582755/allactivity?category_key=STATUSCLUSTER` before concluding a period has no posts.
- **The extension redacts URLs with query strings.** Strip links before returning text or the whole result is blocked.
- Posts by other people appear on his timeline. The author filter in the collector handles it; keep it.

## Alternative without scraping

Facebook's `Download Your Information` with `Posts` in JSON returns everything in one file and skips every limit above. He has to request it from his account; ask before assuming.

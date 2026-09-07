# human

חבילת סקילים שגורמת לכל טקסט להישמע כמו אריאל אייזנשטט ולא כמו AI.

נבנתה מ-123 פוסטים אמיתיים מהפרופיל שלו בפייסבוק, ומהערך `Wikipedia:Signs of AI writing` והמחקרים שהוא מצטט (Reinhart et al., PNAS 2025; Kobak et al.; Juzek & Ward).

## מה יש כאן

| סקיל | מה הוא עושה |
|---|---|
| `human` | כותב טקסט חדש בקול שלו, או מתקן טקסט קיים עד שהוא עובר. כולל בודק דטרמיניסטי. |
| `human-corpus` | אוסף עוד פוסטים אמיתיים מפייסבוק ומעדכן את פרופיל הקול. מזין את `human`. |

## התקנה

```bash
git clone <repo> ~/human-voice-skill
ln -s ~/human-voice-skill/human ~/.claude/skills/human
ln -s ~/human-voice-skill/human-corpus ~/.claude/skills/human-corpus
```

עובד בכל סוכן שתומך בתקן Agent Skills (Claude Code, Codex, Cursor, Gemini CLI ואחרים).

## הבודק

```bash
python3 human/scripts/check.py post.txt      # קובץ
pbpaste | python3 human/scripts/check.py -   # מה-clipboard
python3 human/scripts/check.py --self-test   # בדיקת שפיות
```

יציאה 0 עבר, 1 נפל. בלי תלויות, פייתון 3 בלבד.

**כיול מדוד:** 62 מתוך 63 הפוסטים האמיתיים שלו עוברים. פסקה טיפוסית שנכתבה ב-GPT נופלת על 9 ממצאים.

## שלושת האיסורים שנשברים הכי הרבה

1. תקבולת שלילית: "לא רק X אלא גם Y", "זה לא X, זה Y"
2. מקף ארוך מוקף ברווחים
3. פסקת סיכום בסוף ("לסיכום", "בשורה התחתונה")

## הערה על התוכן

`human/references/corpus.md` מכיל פוסטים אישיים אמיתיים. הריפו נוצר פרטי בכוונה.

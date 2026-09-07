#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gate for Ariel's voice. Reads text, reports AI tells and voice metrics.
Exit 0 = pass, 1 = fail. No dependencies."""
import sys, re, json, argparse

FORBIDDEN_HE = [
    (r'לא רק\b[^\n]{0,40}?\bאלא גם', 'תקבלת שלילית "לא רק X אלא גם Y"'),
    (r'זה לא [^\n]{1,30}?,\s*(זה|אלא)\b', 'תקבולת שלילית "זה לא X, זה Y"'),
    (r'\bהשאלה היא לא\b', 'תקבולת שלילית "השאלה היא לא X אלא Y"'),
    (r'\bפחות [^\n]{1,20}?, יותר\b', 'תקבולת שלילית "פחות X יותר Y"'),
    (r'\bמהווה\b', 'בריחה מאוגד: "מהווה" במקום "הוא"'),
    (r'\bמשמש כ', 'בריחה מאוגד: "משמש כ"'),
    (r'\bמתפקד כ', 'בריחה מאוגד: "מתפקד כ"'),
    (r'\bהינו\b|\bהינה\b', 'עברית מלאכותית: "הינו/הינה"'),
    (r'\bאשר\b', '"אשר" במקום ש־'),
    (r'\bאנו\b', '"אנו" במקום "אנחנו"'),
    (r'\bלצלול\b|\bנצלול\b|\bצוללים\b', 'delve בעברית'),
    (r'\bבעידן הדיגיטלי\b|\bבעולם של היום\b|\bבעולם המהיר\b', 'פתיחה גנרית'),
    (r'(?m)^\s*(חשוב לציין|ראוי לציין)', 'הסתייגות של מודל בפתיחת שורה'),
    (r'\bלסיכום\b|\bלסיום\b|\bבשורה התחתונה\b|\bבסופו של יום\b', 'פסקת סיכום'),
    (r'\bפורץ דרך\b|\bמשנה משחק\b|\bחוויה בלתי נשכחת\b', 'שיווקית גנרית'),
    (r'\bפתרון מושלם\b', 'שיווקית גנרית'),
    (r'\bכאן נכנס לתמונה\b|\bפותח בפניכם\b|\bאנו מזמינים\b|\bהמפתח הוא\b', 'תבנית קופי'),
    (r'\bבין אם אתה\b[^\n]{0,60}?\bובין אם\b', 'כיסוי קהל מלאכותי'),
    (r'\bתנו לזה לשקוע\b|\bזה נשמע מוכר\?|\bעצור את הגלילה\b', 'גימיק קופי'),
    (r'\bמדובר בטכנולוגיה\b|\bטכנולוגיה פורצת דרך\b', 'ניסוח 2024 שנזנח'),
    (r'\bראשית,|\bשנית,|\bלבסוף,', 'מבנה חיבור בית ספר'),
    (r'(?m)^\s*[-•*]\s+\*\*[^*]+\*\*\s*:', 'בולט בפורמט "**כותרת**: הסבר"'),
]
FORBIDDEN_EN = [
    (r'\bdelve\b|\bdeep dive\b', 'delve'),
    (r'\bunderscore(s|d)?\b|\bshowcas(e|es|ing)\b|\bhighlight(s|ing)\b', 'AI vocabulary'),
    (r'\bemphasiz(e|es|ing)\b|\bfoster(s|ing)?\b|\benhanc(e|es|ing)\b', 'AI vocabulary'),
    (r'\bcrucial\b|\bpivotal\b|\bvital\b|\brobust\b|\bmeticulous(ly)?\b', 'AI vocabulary'),
    (r'\bintricate\b|\binterplay\b|\btapestry\b|\btestament\b|\bvibrant\b', 'AI vocabulary'),
    (r'\bboasts\b|\bbolstered\b|\bgarner(ed)?\b|\benduring\b|\balign with\b', 'AI vocabulary'),
    (r'\bseamless\b|\bleverage\b|\bgroundbreaking\b|\bgame-?changer\b', 'AI vocabulary'),
    (r'\bnot only\b[^\n]{0,40}?\bbut also\b', 'negative parallelism'),
    (r"\bit'?s not just\b|\bit is not just\b", 'negative parallelism'),
    (r'\bin conclusion\b|\bin summary\b|\boverall,', 'closing summary'),
    (r'\bserves as a\b|\bstands as a\b', 'copula avoidance'),
]
SOFT_HE = [
    (r'\bמגוון רחב\b', '"מגוון רחב" - הוא כן אומר את זה לפעמים, אבל זה גם ביטוי של מודל'),
    (r'\bיש לציין\b', '"יש לציין" - מותר כהערת אגב באמצע שורה, לא כפתיחה'),
    (r'\bאין ספק ש\b|\bלא בכדי\b|\bהמפתח הוא\b', 'ביטוי שחוק'),
    (r'\bבנוסף\b|\bכמו כן\b|\bיתרה מכך\b|\bזאת ועוד\b', 'חיבור מעבר - אחד לכל היותר בטקסט'),
]

EMOJI = re.compile('[\U0001F300-\U0001FAFF☀-➿️]')
CURLY = re.compile('[“”‘’]')
EMDASH = re.compile('—')
# מקף מחבר סגנוני: שני אסימונים של 2+ אותיות. לא סופר תחיליות כמו "ב-2024" או "ל-AI".
CONNECT = re.compile('[א-ת]{2,}-[א-ת]{2,}|[A-Za-z]{2,}-[א-ת]{2,}|[א-ת]{2,}-[A-Za-z]{2,}')
OPENERS = ['טוב', 'אז', 'לכל מי ש', 'היי חברים', 'בוקר טוב', 'וואי', 'וואלה', 'וואוו',
           'שבוע טוב', 'צהריים טובים', 'חברהה', 'הפתעה', 'אוקיי חברים', 'שלום לכולם', 'מה אומר']
SIGNATURE = ['מלא', 'מטורף', 'יאללה', 'וואלה', 'סופר', 'נטו', 'מגניב', 'כרגיל', 'בגדול',
             'תהינו', 'צ׳או', 'אחלה', 'פסיכ', 'בחייאת', 'חחח', 'יא ', 'דיי', 'מוזמנ']

def words(s):
    return re.findall(r'[\wא-ת״׳\'-]+', s)

def analyse(text):
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    wc = len(words(text))
    fails, warns = [], []

    for pats, tag in ((FORBIDDEN_HE, ''), (FORBIDDEN_EN, '')):
        for pat, label in pats:
            for m in re.finditer(pat, text, re.IGNORECASE if pats is FORBIDDEN_EN else 0):
                ln = text[:m.start()].count('\n') + 1
                fails.append({'line': ln, 'rule': label, 'match': m.group(0)[:40]})

    for m in EMDASH.finditer(text):
        fails.append({'line': text[:m.start()].count('\n') + 1, 'rule': 'מקף ארוך —', 'match': '—'})
    n_emoji = len(EMOJI.findall(text))
    if n_emoji > 1:
        fails.append({'line': 0, 'rule': f'יותר מאימוג׳י אחד ({n_emoji})', 'match': ''})
    for pat, label in SOFT_HE:
        for m in re.finditer(pat, text):
            warns.append({'line': text[:m.start()].count('\n') + 1, 'rule': label, 'match': m.group(0)[:40]})

    for m in CURLY.finditer(text):
        warns.append({'line': text[:m.start()].count('\n') + 1, 'rule': 'גרשיים מסולסלים', 'match': m.group(0)})

    if lines:
        tail = ' '.join(lines[-2:])
        if re.search(r'\b(לסיכום|לסיום|בסך הכל|בשורה התחתונה|בסופו של דבר)\b', tail):
            fails.append({'line': len(lines), 'rule': 'הפסקה האחרונה היא סיכום', 'match': tail[:40]})

    avg_line = sum(len(words(l)) for l in lines) / len(lines) if lines else 0
    n_conn = len(CONNECT.findall(text))
    rate_conn = n_conn * 1000 / wc if wc else 0
    n_bang3 = len(re.findall(r'!{3,}', text))
    n_bang2 = len(re.findall(r'(?<!!)!!(?!!)', text))

    if avg_line > 14:
        warns.append({'line': 0, 'rule': f'שורות ארוכות מדי (ממוצע {avg_line:.1f} מילים, יעד עד 14)', 'match': ''})
    if wc >= 40 and n_conn < 2:
        warns.append({'line': 0, 'rule': f'חסר מקף מחבר (נמצאו {n_conn}, היעד 2-4 בפוסט)', 'match': ''})
    if n_bang2:
        warns.append({'line': 0, 'rule': f'סימני קריאה כפולים ({n_bang2}) - אצלו זה אחד או שלושה', 'match': ''})
    if lines and not any(lines[0].startswith(o) for o in OPENERS):
        warns.append({'line': 1, 'rule': f'פתיחה לא מהרשימה שלו: "{lines[0][:30]}"', 'match': ''})
    if not any(s in text for s in SIGNATURE):
        warns.append({'line': 0, 'rule': 'אין אף מילת חתימה שלו', 'match': ''})
    if wc >= 40 and not re.search(r'\d', text):
        warns.append({'line': 0, 'rule': 'אין אף פרט קונקרטי (מספר/מחיר/שעה/תאריך)', 'match': ''})

    return {'ok': not fails, 'fails': fails, 'warns': warns,
            'metrics': {'words': wc, 'lines': len(lines), 'avg_words_per_line': round(avg_line, 1),
                        'connect_hyphens': n_conn, 'per_1000w': round(rate_conn, 1),
                        'triple_bang': n_bang3, 'emoji': n_emoji}}

def report(r):
    m = r['metrics']
    print(f"מדדים: {m['words']} מילים · {m['lines']} שורות · {m['avg_words_per_line']} מילים לשורה · "
          f"מקף מחבר {m['connect_hyphens']} ({m['per_1000w']}/1000) · !!! {m['triple_bang']} · אימוג׳י {m['emoji']}")
    print(f"יעד:   8-14 מילים לשורה · מקף מחבר 20-50/1000 · אימוג׳י 0-1 · מקף ארוך 0")
    if r['fails']:
        print(f"\nנפילות ({len(r['fails'])}):")
        for f in r['fails']:
            loc = f"שורה {f['line']}" if f['line'] else "כללי"
            print(f"  ✗ {loc}: {f['rule']}" + (f"  ← \"{f['match']}\"" if f['match'] else ''))
    if r['warns']:
        print(f"\nאזהרות ({len(r['warns'])}):")
        for w in r['warns']:
            loc = f"שורה {w['line']}" if w['line'] else "כללי"
            print(f"  ! {loc}: {w['rule']}" + (f"  ← \"{w['match']}\"" if w['match'] else ''))
    print("\nעבר" if r['ok'] else "\nנפל - לתקן ולהריץ שוב")

GOOD = """טוב
אז אחרי שבועיים של ניסויים-סוף סוף סגרתי את הפייפליין
הכל רץ בקלוד קוד מ-א׳ ועד ת׳
לקח לי 6 שעות
מוזמנים להגיד לי מה דעתכם!"""
BAD = """בעולם של היום, בינה מלאכותית מהווה כלי אשר משנה את כללי המשחק — לא רק עבור חברות גדולות אלא גם עבור עסקים קטנים.
חשוב לציין כי הטכנולוגיה פורצת הדרך הזו מאפשרת לכם לצלול לעומק הנתונים ולהפיק תובנות בעלות ערך.
לסיכום, אין ספק שמדובר בפתרון מושלם עבור כל ארגון."""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('path', nargs='?', help="קובץ טקסט, או - לקריאה מ-stdin")
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--self-test', action='store_true')
    a = ap.parse_args()
    if a.self_test:
        g, b = analyse(GOOD), analyse(BAD)
        ok = g['ok'] and not b['ok']
        print(f"טקסט אמיתי שלו: {'עבר' if g['ok'] else 'נפל (באג)'} | טקסט AI: "
              f"{'נפל כצפוי' if not b['ok'] else 'עבר (באג)'} ({len(b['fails'])} נפילות)")
        print("הבודק תקין" if ok else "הבודק שבור")
        sys.exit(0 if ok else 1)
    if not a.path:
        ap.error("צריך נתיב לקובץ או -")
    text = sys.stdin.read() if a.path == '-' else open(a.path, encoding='utf-8').read()
    r = analyse(text)
    print(json.dumps(r, ensure_ascii=False, indent=1) if a.json else '', end='')
    if not a.json:
        report(r)
    sys.exit(0 if r['ok'] else 1)

if __name__ == '__main__':
    main()

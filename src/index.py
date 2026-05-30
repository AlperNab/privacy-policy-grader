#!/usr/bin/env python3
"""
privacy-policy-grader — any privacy policy URL or text → letter grade A-F
Scores on: data collection, third-party sharing, user rights, data retention,
security practices, GDPR/CCPA compliance signals, clarity of language
"""
import anthropic, json, re, sys, urllib.request

SYSTEM = """You are a privacy rights expert and data protection specialist.
Analyze this privacy policy and grade it from A to F.

Grading rubric:
A = Minimal data collection, clear user rights, no selling, easy deletion
B = Reasonable collection, good transparency, some sharing but disclosed
C = Average — collects broadly, shares with partners, limited user control
D = Excessive collection, vague sharing, hard to opt out, poor transparency
F = Sells data, no user rights, tracks everything, deceptive language

Return ONLY valid JSON — no markdown, no explanation.

{
  "url": "string or null",
  "company": "company name if detectable",
  "overall_grade": "A|B|C|D|F",
  "overall_score": number_0_to_100,
  "grade_summary": "one sentence explaining the grade",
  "last_updated": "date string or null",
  "scores": {
    "data_minimization": number_0_to_10,
    "transparency": number_0_to_10,
    "user_rights": number_0_to_10,
    "third_party_sharing": number_0_to_10,
    "data_retention": number_0_to_10,
    "security_practices": number_0_to_10,
    "language_clarity": number_0_to_10,
    "compliance_signals": number_0_to_10
  },
  "data_collected": {
    "personal": ["name","email","phone","..."],
    "behavioral": ["browsing history","clicks","..."],
    "device": ["IP address","device ID","..."],
    "location": ["precise GPS","country-level","none"],
    "financial": ["payment card","bank details","none"],
    "biometric": ["face ID","fingerprint","none"],
    "children": true_or_false
  },
  "data_sharing": {
    "sells_data": true_or_false,
    "shares_with_advertisers": true_or_false,
    "shares_with_data_brokers": true_or_false,
    "shares_with_law_enforcement": "with warrant|proactively|never|unclear",
    "third_parties_listed": ["list of named third parties or categories"],
    "cross_context_behavioral_advertising": true_or_false
  },
  "user_rights": {
    "access_your_data": true_or_false,
    "delete_your_data": true_or_false,
    "opt_out_of_sale": true_or_false,
    "data_portability": true_or_false,
    "correct_your_data": true_or_false,
    "opt_out_targeted_ads": true_or_false,
    "how_to_exercise": "description of how to submit requests"
  },
  "retention": {
    "specifies_retention_period": true_or_false,
    "retention_period": "string or null",
    "deletion_on_request": true_or_false,
    "backups_retained": true_or_false
  },
  "red_flags": [
    {
      "issue": "description",
      "severity": "critical|high|medium",
      "quote": "relevant text under 40 words or null"
    }
  ],
  "green_flags": ["positive practices noted"],
  "jurisdiction_compliance": {
    "gdpr_signals": true_or_false,
    "ccpa_signals": true_or_false,
    "coppa_signals": true_or_false
  },
  "readability_grade": "elementary|middle_school|high_school|college|lawyer_only",
  "word_count": number_or_null,
  "plain_english_summary": "3-4 sentence summary a 10-year-old could understand",
  "confidence": 0.0
}"""

def fetch_url(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 privacy-grader/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        html = r.read().decode("utf-8", errors="replace")
    text = re.sub(r'<script[^>]*>[\s\S]*?</script>','',html,flags=re.IGNORECASE)
    text = re.sub(r'<style[^>]*>[\s\S]*?</style>','',text,flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>',' ',text)
    text = re.sub(r'\s+',' ',text).strip()
    return text[:40000]

def grade(source: str) -> dict:
    client = anthropic.Anthropic()
    if source.startswith("http"):
        text = fetch_url(source)
        prompt = f"Grade this privacy policy from {source}:\n\n{text}"
    else:
        prompt = f"Grade this privacy policy:\n\n{source[:40000]}"
    resp = client.messages.create(
        model="claude-sonnet-4-20250514", max_tokens=3000, system=SYSTEM,
        messages=[{"role":"user","content":prompt}]
    )
    raw = re.sub(r'^```(?:json)?\s*','',resp.content[0].text.strip(),flags=re.MULTILINE)
    raw = re.sub(r'\s*```$','',raw,flags=re.MULTILINE)
    result = json.loads(raw)
    if source.startswith("http"): result["url"] = source
    return result

GRADE_COLOR = {"A":"\033[92m","B":"\033[92m","C":"\033[93m","D":"\033[91m","F":"\033[91m"}
RESET = "\033[0m"
SEV_ICON = {"critical":"🚨","high":"🔴","medium":"🟠"}

def print_report(r: dict):
    g = r.get("overall_grade","?")
    color = GRADE_COLOR.get(g,"")
    print(f"\n{'═'*60}")
    print(f"  PRIVACY POLICY GRADE: {color}{g}{RESET} ({r.get('overall_score',0)}/100)")
    print(f"  {r.get('company','Unknown Company')}")
    if r.get('url'): print(f"  {r['url']}")
    print(f"{'═'*60}")
    print(f"\n  {r.get('grade_summary','')}")
    print(f"\n  Plain English: {r.get('plain_english_summary','')}")

    scores = r.get("scores",{})
    if scores:
        print(f"\n  Scores:")
        for k,v in scores.items():
            bar = "█"*v + "░"*(10-v)
            print(f"    {k:<30} {bar} {v}/10")

    ds = r.get("data_sharing",{})
    print(f"\n  Sells your data:          {'❌ YES' if ds.get('sells_data') else '✅ No'}")
    print(f"  Shares with advertisers:  {'⚠ YES' if ds.get('shares_with_advertisers') else '✅ No'}")
    print(f"  Behavioral advertising:   {'⚠ YES' if ds.get('cross_context_behavioral_advertising') else '✅ No'}")

    ur = r.get("user_rights",{})
    print(f"\n  Your rights:")
    rights = [("Access your data","access_your_data"),("Delete your data","delete_your_data"),
              ("Opt out of sale","opt_out_of_sale"),("Data portability","data_portability")]
    for label,key in rights:
        print(f"    {'✅' if ur.get(key) else '❌'} {label}")

    flags = r.get("red_flags",[])
    if flags:
        print(f"\n  🚩 Red flags ({len(flags)}):")
        for f in flags:
            print(f"  {SEV_ICON.get(f.get('severity','medium'),'')} {f.get('issue','')}")
            if f.get('quote'): print(f"     \"{f['quote'][:80]}\"")

    green = r.get("green_flags",[])
    if green:
        print(f"\n  ✅ Green flags:")
        for g2 in green[:4]: print(f"  + {g2}")

    print(f"\n  Readability: {r.get('readability_grade','?')}")
    comp = r.get("jurisdiction_compliance",{})
    sigs = [k.upper().replace("_SIGNALS","") for k,v in comp.items() if v]
    if sigs: print(f"  Compliance signals: {', '.join(sigs)}")
    print(f"  Confidence: {int(r.get('confidence',0)*100)}%")
    print(f"{'═'*60}\n")

if __name__ == "__main__":
    if len(sys.argv)<2: print("Usage: python -m privacy_policy_grader <url-or-text> [--json]"); sys.exit(0)
    src = sys.argv[1] if sys.argv[1]!="-" else sys.stdin.read()
    r = grade(src)
    if "--json" in sys.argv: print(json.dumps(r,indent=2,ensure_ascii=False))
    else: print_report(r)

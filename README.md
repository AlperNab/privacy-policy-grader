# privacy-policy-grader

> **Any privacy policy URL → letter grade A–F.** Scores on data collection, third-party sharing, user rights, retention, GDPR/CCPA signals. Flags every red flag with direct quotes.

[![PyPI](https://img.shields.io/pypi/v/privacy-policy-grader?style=flat)](https://pypi.org/project/privacy-policy-grader/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Quickstart

```bash
pip install privacy-policy-grader
python -m privacy_policy_grader https://example.com/privacy
python -m privacy_policy_grader https://example.com/privacy --json
```

## Grades and what they mean

| Grade | Meaning |
|-------|---------|
| A | Minimal collection, clear rights, no selling, easy deletion |
| B | Reasonable collection, good transparency, disclosed sharing |
| C | Broad collection, partner sharing, limited user control |
| D | Excessive collection, vague sharing, hard to opt out |
| F | Sells data, no user rights, tracks everything |

## What it detects

Sells your data · Behavioral advertising · Law enforcement disclosure · 
Data retention period · Your deletion rights · Portability · Access rights · 
GDPR/CCPA compliance signals · Readability grade · All red flags with quotes

## License
MIT © [Alper Nabil Gabra Zakher](https://github.com/AlperNab)

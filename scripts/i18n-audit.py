#!/usr/bin/env python3
"""i18n audit: scan .vue files for hardcoded English UI strings that are not wrapped in $t()/t().

Heuristics:
- static (non-bound) label/title/hint/placeholder/message attrs with >=2 English words
- static text nodes with common UI words (Save/Cancel/Delete/...)
Usage: python3 scripts/i18n-audit.py [--min-words 2]
Exit code 0 always; prints per-file findings sorted by count.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ROOTS = [
    REPO / 'packages/frontend/src',
    REPO / 'packages/nuxt-base-layer/src',
]

ATTR_RE = re.compile(
    r'(?<![:\w-])(label|title|hint|placeholder|prepend-inner-icon|append-icon|content)\s*=\s*"([^"{}]+)"'
)
# Common UI words worth flagging inside text nodes
UI_WORDS = re.compile(
    r'>\s*([A-Z][a-zA-Z]+(?:\s+(?:[a-zA-Z]+)){1,6})\s*<'
)

SKIP_PARTS = {'node_modules', '.nuxt', 'dist', 'locales', '.playground'}
SKIP_TEXT_NODE = re.compile(r'^(v-|mdi-|data-|https?:|/[a-z]|#|[A-Z]{2,})')

def english_words(s: str) -> int:
    return len(re.findall(r"[A-Za-z]{2,}", s))

def audit(min_words: int) -> dict[str, list[str]]:
    findings: dict[str, list[str]] = {}
    for root in ROOTS:
        if not root.exists():
            continue
        for f in root.rglob('*.vue'):
            if any(part in SKIP_PARTS for part in f.parts):
                continue
            hits = []
            text = f.read_text(encoding='utf-8', errors='replace')
            # Only inspect <template> part
            tpl = text.split('</template>')[0]
            for m in ATTR_RE.finditer(tpl):
                attr, val = m.group(1), m.group(2).strip()
                if attr.endswith('-icon') or val.startswith('mdi-'):
                    continue
                if english_words(val) >= min_words and re.match(r'^[A-Z]', val):
                    hits.append(f'{attr}="{val}"')
            for m in UI_WORDS.finditer(tpl):
                val = m.group(1).strip()
                if SKIP_TEXT_NODE.match(val):
                    continue
                if english_words(val) >= 2:
                    hits.append(f'text: {val}')
            if hits:
                findings[str(f.relative_to(REPO))] = sorted(set(hits))
    return findings

if __name__ == '__main__':
    min_words = 2
    if '--min-words' in sys.argv:
        min_words = int(sys.argv[sys.argv.index('--min-words') + 1])
    findings = audit(min_words)
    total = sum(len(v) for v in findings.values())
    for f, hits in sorted(findings.items(), key=lambda kv: -len(kv[1])):
        print(f'{f} ({len(hits)}):')
        for h in hits:
            print(f'  - {h}')
    print(f'\n== {total} potential untranslated strings in {len(findings)} files ==')

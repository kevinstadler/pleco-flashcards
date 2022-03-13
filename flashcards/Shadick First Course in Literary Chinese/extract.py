#!/usr/bin/env python3
import re

t = open('shadick.txt').read().replace('\f', '')

# split cleanly to delete Wortreferenz until chapter headers
sections = re.split(r'^\f?((?:Übung )?)Lektion ', t, flags=re.MULTILINE)[1:]
contents = [ s.split('\n', 1) for s in sections[1::2] ]
headers = [ '// Shadick/' + prefix + content[0] for prefix, content in zip(sections[0::2], contents) ]
# cut down content
contents = [ c[1].split('Wortreferenz', 1)[0] for c in contents ]

# add main categories

import unidecode
# 2nd and 4th tone: https://www.unicode.org/charts/PDF/U0080.pdf
# 1st and 3rd tone: https://www.unicode.org/charts/PDF/U0100.pdf
tonechars = "āáăàēéĕèīíĭìōóŏòūúŭùǜ"
# ǒ ŏ

wadegiles = r"[A-Za-zü\'1-5\.]+[1-5]"
# pinyin = r'[!\w]*[a-z' + tonechars + '\.]+' # disallow upper case endings
pinyinendings = tonechars + 'aeiougnr'
pinyin = f'\w*[{pinyinendings}]' # disallow upper case endings or ending in …
hanzi = r'\u4e00-\u9fff'

def removespaces(match):
  return match.group(0).replace(' ', '')
# change accents (AFTER vowels) into tone numbers

def tonenumber(match):
  tone = 1 + tonechars.find(match.group(1)) % 4
  return unidecode.unidecode(match.group(1)) + match.group(2) + str(tone)

def processcategory(categoryheader, t):
    # if header is Lektion remove first 3 lines (bogus hanzi)
    if not 'Ü' in categoryheader:
      for i in range(3):
        t = t[t.find('\n')+1:]

    # remove single spaces from personal name pinyins
    # t = re.sub('([A-Z]\w*[' + tonechars + ']\w*( \w+)+)', removespaces, t)

    # hanzi[/ or ...]/\n[. or hanzi]
    t = re.sub(f'([{hanzi}](?:\.\.\.|/))\n([{hanzi}\.])', r'\1\2', t)
    # hanzi\nhanzi to space
    t = re.sub(f'([{hanzi}])\n([{hanzi}])', r'\1 \2', t)
    # traditional and simplified
    t = re.sub(f'^(\d* ?)([{hanzi}][\w/]*) ([{hanzi}]\w*)\n[ ]*{wadegiles}\s+({pinyin})', r'\1\3[\2]\t\4\t', t, flags=re.MULTILINE)
    # traditional only
    t = re.sub(f'^(\d* ?[{hanzi}](?:/ |\w)*)\n[ ]*(?:{wadegiles}\s+)?({pinyin})', r'\1\t\2\t', t, flags=re.MULTILINE)

    # replace tone accents with numbers
    t = re.sub(f'([{tonechars}])([aeiou]?(:?r|ng?)?)', tonenumber, t)
    # add sentence subgroups
    t = re.sub(f'^(\d+) ?([{hanzi}])', categoryheader + r'/\1\n\2', t, flags=re.MULTILINE)

    # merge definitions onto previous line (remove preceding newline + space(s)
    t = re.sub(f'\n(?!/|[{hanzi}\[\]]+\t)', r' ', t, flags=re.MULTILINE)
    return '\n'.join([categoryheader, t])

sections = [ processcategory(title, content) for title, content in zip(headers, contents) ]
t = '\n'.join(sections)

open('shadick.tsv', 'w').write(t)


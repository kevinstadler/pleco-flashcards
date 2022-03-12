#!/usr/bin/env python3
import re

t = open('shadick.txt').read()

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
tonechars = "āáăàēéĕèīíĭìōóŏòūúŭù   ǜ"
# ǒ ŏ

wadegiles = r"[a-zü'1-5\.]+[1-5]"
# pinyin = r'[!\w]*[a-z' + tonechars + '\.]+' # disallow upper case endings
pinyin = r'[!\w]*[' + tonechars + ']\w*' # disallow upper case endings …
hanzi = r'\u4e00-\u9fff'

def removespaces(match):
  return match.group(0).replace(' ', '')
# change accents (AFTER vowels) into tone numbers

def tonenumber(match):
  tone = 1 + tonechars.find(match.group(1)) % 4
  return unidecode.unidecode(match.group(1)) + match.group(2) + str(tone)

def processcategory(categoryheader, t):

    # remove single spaces from personal name pinyins
    t = re.sub('([A-Z]\w*[' + tonechars + ']\w*( \w+)+)', removespaces, t)

    # switch left-column hanzi from second to first line
    # t = re.sub(f'^\s*(   {wadegiles}\s+{pinyin}.*)\n(\d* ?[{hanzi}].*?)(\s{5}.*)?', r'\2\n\1 \3', t, flags=re.MULTILINE)
    # one more time for lines that don't have wade-giles
    # t = re.sub(f'^\s*(   {pinyin}\s*.*)\n(\d* ?[{hanzi}]\S*)(\s{5}.*)?', r'\2\n   dummy1 \1 \3', t, flags=re.MULTILINE)

    # put hanzi at start of line, remove wade giles
    t = re.sub(f'^(\d* ?[{hanzi}]\S*[{hanzi} ]*)\n[ ]*{wadegiles}\s+({pinyin})', r'\1\t\t\2\t\t', t, flags=re.MULTILINE)
    # TODO also match 2nd hanzi (which is after 3+ spaces)

    # replace tone accents with numbers
    t = re.sub(f'([{tonechars}])([eiou]?(:?r|ng?)?)', tonenumber, t)
    # add sentence subgroups
    t = re.sub(f'^(\d+) ?([{hanzi}])', categoryheader + r'/\1\n\2', t, flags=re.MULTILINE)

    # merge definitions onto previous line (remove preceding newline + space(s)
    t = re.sub(r'\n[\f ]+(.*)', r' \1', t)
    return '\n'.join([categoryheader, t])

sections = [ processcategory(title, content) for title, content in zip(headers, contents) ]
t = '\n'.join(sections)

open('shadick.tsv', 'w').write(t)


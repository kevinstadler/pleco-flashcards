#!/usr/bin/env python3
import re
from os import rename
from subprocess import run, PIPE

t = open('shadick.txt').read().replace('\f', '')
# replace breves with carons (which is what pleco wants)
t = t.replace('ă', 'ǎ')	
t = t.replace('ĕ', 'ě')	
t = t.replace('ĭ', 'ǐ')
t = t.replace('ŏ', 'ǒ')
t = t.replace('ŭ', 'ǔ')
t = t.replace('ìè', 'iè')

# split cleanly to delete Wortreferenz until chapter headers
sections = re.split(r'^\f?((?:(?:Zusammenfassende )?Übung )?)Lektion(?:en)? ', t, flags=re.MULTILINE)[1:]
contents = [ s.split('\n', 1) for s in sections[1::2] ]
headers = [ '// Shadick/' + prefix + content[0] for prefix, content in zip(sections[0::2], contents) ]
# cut down content
contents = [ c[1].split('Wortreferenz', 1)[0] for c in contents ]

# add main categories

import unidecode
# 2nd and 4th tone: https://www.unicode.org/charts/PDF/U0080.pdf
# 1st and 3rd tone: https://www.unicode.org/charts/PDF/U0100.pdf
# 3rd tone should use *breve*, not caron!
tonechars = "āáǎàēéěèīíǐìōóǒòūúǔù@@ǚǜ"

wadegiles = r"[A-Za-zü\'’1-5\.\-ìǔ]+[h1-5]"
# pinyin = r'[!\w]*[a-z' + tonechars + '\.]+' # disallow upper case endings
pinyinendings = tonechars + 'aeiougnr'
pinyin = f'\S*[{pinyinendings}\.…]' # disallow upper case endings or ending in …
tonecoda = f'[{tonechars}][aeiou]?(?:r|ng?)?'
tonepinyin = f'[A-Za-z]*{tonecoda}'
hanzi = r'\u4e00-\u9fff'

def removespaces(match):
  return match.group(0).replace(' ', '')
# change accents (AFTER vowels) into tone numbers

# def tonenumber(match):
#   # replace with re.sub(f'([{tonechars}])([aeiou]?(:?r|ng?)?)', tonenumber, t)
#   tone = 1 + tonechars.find(match.group(1)) % 4
#   # FIXME don't remove umlauts
#   return unidecode.unidecode(match.group(1)) + match.group(2) + str(tone)

def processcategory(categoryheader, t):
    # if header is Lektion remove first 3 lines (bogus hanzi)
    if not 'Ü' in categoryheader:
      for i in range(3):
        t = t[t.find('\n')+1:]

    # remove hyphenated line breaks (especially bad for WG)
    t = t.replace('-\n', '')
    t = t.replace(',\n', ', ')
    t = t.replace('\n...\n', '...')
    # merge hanzi. with above line
    t = re.sub(f'\n([{hanzi}]\.\n)', r' \1', t)
    t = re.sub(f'([{hanzi}])=([{hanzi}])', r'\1/\2', t)
    # remove post-... line breaks (unless they're before a hanzi)
    # t = re.sub(f'\.\.\.\n(?![{hanzi}])', '...', t)
    # merge single non-Hanzi character lines with above
    t = re.sub('\n([a-z,]\n)', r'\1', t)
    # TODO merge split pinyin lines (not working)
    t = re.sub(f'^({tonepinyin})\n({tonepinyin})$', r'\1\2', t, flags=re.MULTILINE)

    # ^(num)\nhanzi to (num)hanzi
    t = re.sub(f'^(\(\d+\))\n([{hanzi}])', r'\1\2', t, flags=re.MULTILINE)
    # remove newline from hanzi[/ or ...]/\n[. or hanzi]
    t = re.sub(f'([{hanzi}](?:\.\.\.|/))\n([{hanzi}\.])', r'\1\2', t)
    # [hanzi-line with at least one space]\nhanzi to nowt
    t = re.sub(f'^([hanzi]+ [{hanzi}\. ]+)\n([{hanzi}])', r'\1\2', t, flags=re.MULTILINE)
    # TODO remove newline before every hanzi if the hanzi (sequence) isn't followed by wade-giles or pinyin

    # remove single spaces from personal name pinyins
    t = re.sub('(?<=\s)( *\w*' + tonecoda + ')+', removespaces, t)
    # t = re.sub('([A-Z]' + pinyin + '(?: \w*' + tonecoda + ')+)', removespaces, t)

    # traditional and simplified
    t = re.sub(f'^\(?(\d*)\)? ?([{hanzi}][\S]*) ([{hanzi}][\w\.…]*)\n? *{wadegiles}\s+({pinyin}) ?!?\s+', r'\1\3[\2]\t\4\t', t, flags=re.MULTILINE)
    # traditional only -- accept "hanzi / hanzi", optional wade-giles, and delete post-pinyin exclamation marks
    t = re.sub(f'^\(?(\d*)\)? ?([{hanzi}](?:/ |[\S])*)\n? *(?:{wadegiles}\s+)?({pinyin}) ?!?\s+', r'\1\2\t\3\t', t, flags=re.MULTILINE)

    # remove pinyin from "pinyin hanzi" sequences in the definition bodies
    # t = re.sub(f'(\w*{tonecoda}) (?=[hanzi])', r'\1', t)
    # replace tone accents with numbers
    # t = re.sub(f'([{tonechars}])([aeiou]?(:?r(?!é)|ng?)?)', tonenumber, t)
    # add sentence subgroups
    t = re.sub(f'^(\d+) ?([{hanzi}])', categoryheader + r'/\1\n\2', t, flags=re.MULTILINE)

    # merge definitions onto previous line (remove preceding newline + space(s)
    t = re.sub(f'\n(?!/|[{hanzi}\/\.…\[\]]+\t)', r' ', t, flags=re.MULTILINE)

    # TODO https://www.plecoforums.com/threads/multiple-new-lines-in-user-defined-flashcards.5916/#post-44863
    # \ueab2 \ueab3 for bold, 4 and 5 for italic
    repls = ['I', 'II', 'III', 'IV', 'V', 'VI']
    for i, repl in enumerate(repls):
      t = re.sub(f'(?<=[ \t]){repl}\. ?', ('' if i == 0 else '\ueab1') + f'\ueab2{i+1}\ueab3 ', t)

    # make POS cursive
    t = re.sub('(?<=[ \t])([a-z]+\.? Konj\.|Ad[jv]\.?|N|Pron\.?|[CHIPST]V|Zahlwort) ', '\ueab4\\1\ueab5 ', t, flags=re.IGNORECASE)
    t = re.sub('\*([a-z]+\.? Konj\.?|Ad[jv]\.?|N|Pron\.?|[CHIPST]V|Zahlwort) ', ' \ueab4\\1\ueab5 ', t, flags=re.IGNORECASE)

    return '\n'.join([categoryheader, t])

sections = [ processcategory(title, content) for title, content in zip(headers, contents) ]
t = '\n'.join(sections)

rename('shadick-flashcards.txt', 'shadick-flashcards.txt.bu')
open('shadick-flashcards.txt', 'w').write(t)
print(run(['diff', 'shadick-flashcards.txt.bu', 'shadick-flashcards.txt'], stdout=PIPE, text=True).stdout)


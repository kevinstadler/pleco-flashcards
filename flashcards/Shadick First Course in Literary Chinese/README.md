## German flashcards for Shadick's *A First Course in Literary Chinese*

The flashcards were not created by myself, I merely extracted the content of an unattributed German language PDF titled *Klassik Shadick-Vokabeln Chinesisch-Deutsch* that's floating around the web.

If you want the flashcards to test you on the German definitions (and avoid them being merged with already existing dictionary-definition based flashcards) you should do `flashcards > Import/Export > Import Cards` with the following settings:

```
* Definition source: File Only
* Duplicate entries: Allow
```

```
pdftotext -raw shadick.pdf

# diff shadick.txt{.orig,} > shadick-corrections.diff
patch shadick.txt < shadick-corrections.diff

pip3 install unidecode
./extract.py
```

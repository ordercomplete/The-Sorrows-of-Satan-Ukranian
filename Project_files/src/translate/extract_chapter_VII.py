# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

from pypdf import PdfReader
import os

pdf = PdfReader(r'D:\GEN\The-Sorrows-of-Satan-Ukranian\Text-origin\The Sorrows of Satan, by Marie Corelli—A Project Gutenberg eBook.pdf')
text = ' '.join([p.extract_text() for p in pdf.pages])
lines = text.split('\n')

# Chapter VII starts at line 1840, ends before line 2193 (Chapter VIII)
chapter_start = 1840
chapter_end = 2193

chapter_lines = lines[chapter_start:chapter_end]
chapter_text = '\n'.join(chapter_lines)

# Save to file
os.makedirs(r'D:\GEN\The-Sorrows-of-Satan-Ukranian\Text-origin\chapters', exist_ok=True)
output_path = r'D:\GEN\The-Sorrows-of-Satan-Ukranian\Text-origin\chapters\chapter_VII.txt'

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(chapter_text)

print(f'Saved {len(chapter_text)} chars to {output_path}')
print(f'\nFirst 500 chars:')
print(chapter_text[:500])

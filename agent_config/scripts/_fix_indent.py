#!/usr/bin/env python3
"""Tymчасовий скрипт для виправлення відступів у sync-agent.py"""
import os

path = os.path.join(os.path.dirname(__file__), 'sync-agent.py')
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix line 713 (0-indexed 712): should be 4 spaces, not 12
lines[712] = '    print(f"\\n   Removed: {len(removed)} files" + (" (permanent, no trash)" if purge else " (via trash)"))\n'

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"Fixed line 713: {repr(lines[712])}")
#!/usr/bin/env python3
"""
BVM — Build verse database from SGSS Bible text files.
Downloads 66 book files, extracts 5 popular verses per book, outputs verses.json.
"""

import re
import json
import os
import urllib.request

BASE_URL = "https://raw.githubusercontent.com/Walusimbi-Leon1/sgss-bible/main/sgss"

# 66 books with their canonical names
BOOKS = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
    "Joshua", "Judges", "Ruth", "1Samuel", "2Samuel",
    "1Kings", "2Kings", "1Chronicles", "2Chronicles", "Ezra",
    "Nehemiah", "Esther", "Job", "Psalms", "Proverbs",
    "Ecclesiastes", "SongOfSolomon", "Isaiah", "Jeremiah", "Lamentations",
    "Ezekiel", "Daniel", "Hosea", "Joel", "Amos",
    "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk",
    "Zephaniah", "Haggai", "Zechariah", "Malachi",
    "Matthew", "Mark", "Luke", "John", "Acts",
    "Romans", "1Corinthians", "2Corinthians", "Galatians", "Ephesians",
    "Philippians", "Colossians", "1Thessalonians", "2Thessalonians",
    "1Timothy", "2Timothy", "Titus", "Philemon",
    "Hebrews", "James", "1Peter", "2Peter", "1John", "2John", "3John",
    "Jude", "Revelation"
]

# Short book names for display
BOOK_SHORT = [
    "Gen", "Ex", "Lev", "Num", "Deut",
    "Josh", "Judg", "Ruth", "1Sam", "2Sam",
    "1Kgs", "2Kgs", "1Chr", "2Chr", "Ezra",
    "Neh", "Esth", "Job", "Ps", "Prov",
    "Eccl", "Song", "Isa", "Jer", "Lam",
    "Ezek", "Dan", "Hos", "Joel", "Amos",
    "Obad", "Jon", "Mic", "Nah", "Hab",
    "Zeph", "Hag", "Zech", "Mal",
    "Matt", "Mark", "Luke", "John", "Acts",
    "Rom", "1Cor", "2Cor", "Gal", "Eph",
    "Phil", "Col", "1Thess", "2Thess",
    "1Tim", "2Tim", "Titus", "Phm",
    "Heb", "James", "1Pet", "2Pet", "1John", "2John", "3John",
    "Jude", "Rev"
]

# 5 popular/strong verses per book (book_index, chapter:verse)
VERSE_REFS = [
    # Genesis
    [(1, 1), (1, 26), (3, 15), (12, 2), (50, 20)],
    # Exodus
    [(3, 14), (14, 14), (20, 3), (20, 12), (34, 6)],
    # Leviticus
    [(19, 18), (19, 2), (20, 7), (25, 10), (26, 12)],
    # Numbers
    [(6, 24), (6, 25), (6, 26), (14, 18), (23, 19)],
    # Deuteronomy
    [(6, 4), (6, 5), (7, 9), (30, 19), (31, 6)],
    # Joshua
    [(1, 8), (1, 9), (24, 15), (22, 5), (4, 24)],
    # Judges
    [(5, 31), (6, 12), (17, 6), (21, 25), (2, 18)],
    # Ruth
    [(1, 16), (1, 17), (2, 12), (3, 11), (4, 17)],
    # 1 Samuel
    [(3, 10), (16, 7), (15, 22), (12, 24), (17, 47)],
    # 2 Samuel
    [(7, 18), (22, 31), (22, 32), (12, 13), (24, 14)],
    # 1 Kings
    [(3, 5), (3, 9), (8, 27), (18, 21), (8, 61)],
    # 2 Kings
    [(6, 16), (6, 17), (19, 15), (23, 25), (5, 10)],
    # 1 Chronicles
    [(4, 10), (16, 11), (16, 34), (28, 9), (16, 23)],
    # 2 Chronicles
    [(7, 14), (16, 9), (20, 15), (19, 7), (5, 13)],
    # Ezra
    [(1, 3), (3, 11), (7, 10), (8, 22), (10, 4)],
    # Nehemiah
    [(8, 10), (9, 6), (1, 5), (4, 14), (12, 43)],
    # Esther
    [(4, 14), (4, 16), (2, 17), (8, 17), (9, 22)],
    # Job
    [(1, 21), (19, 25), (19, 26), (42, 2), (42, 5)],
    # Psalms
    [(23, 1), (23, 4), (19, 1), (119, 105), (51, 10)],
    # Proverbs
    [(3, 5), (3, 6), (1, 7), (22, 6), (9, 10)],
    # Ecclesiastes
    [(3, 1), (12, 13), (1, 2), (4, 12), (11, 5)],
    # Song of Solomon
    [(2, 4), (8, 6), (8, 7), (4, 7), (1, 2)],
    # Isaiah
    [(9, 6), (53, 5), (40, 31), (55, 8), (6, 8)],
    # Jeremiah
    [(29, 11), (1, 5), (33, 3), (15, 16), (17, 7)],
    # Lamentations
    [(3, 22), (3, 23), (3, 24), (3, 26), (3, 31)],
    # Ezekiel
    [(18, 20), (36, 26), (37, 3), (37, 4), (47, 9)],
    # Daniel
    [(3, 17), (3, 18), (6, 22), (2, 20), (12, 3)],
    # Hosea
    [(4, 6), (6, 6), (14, 1), (11, 8), (14, 4)],
    # Joel
    [(2, 28), (2, 32), (2, 13), (3, 18), (2, 12)],
    # Amos
    [(3, 3), (5, 14), (5, 24), (8, 11), (4, 12)],
    # Obadiah
    [(1, 3), (1, 15), (1, 17), (1, 21), (1, 4)],
    # Jonah
    [(1, 3), (2, 1), (2, 2), (4, 2), (3, 10)],
    # Micah
    [(6, 8), (5, 2), (7, 18), (6, 6), (6, 7)],
    # Nahum
    [(1, 3), (1, 7), (3, 5), (1, 15), (3, 11)],
    # Habakkuk
    [(2, 20), (2, 4), (3, 17), (3, 18), (2, 14)],
    # Zephaniah
    [(3, 17), (1, 12), (2, 3), (3, 20), (3, 9)],
    # Haggai
    [(2, 9), (1, 8), (2, 7), (1, 5), (2, 4)],
    # Zechariah
    [(9, 9), (4, 6), (2, 8), (8, 16), (12, 10)],
    # Malachi
    [(3, 10), (3, 6), (4, 5), (4, 6), (3, 16)],
    # Matthew
    [(5, 14), (28, 19), (11, 28), (6, 33), (22, 37)],
    # Mark
    [(11, 24), (16, 15), (12, 30), (10, 27), (10, 45)],
    # Luke
    [(2, 10), (2, 11), (6, 31), (10, 27), (19, 10)],
    # John
    [(3, 16), (14, 6), (1, 1), (15, 13), (5, 24)],
    # Acts
    [(1, 8), (2, 38), (16, 31), (4, 12), (20, 24)],
    # Romans
    [(3, 23), (6, 23), (8, 28), (10, 9), (8, 1)],
    # 1 Corinthians
    [(13, 4), (13, 8), (15, 10), (10, 13), (16, 14)],
    # 2 Corinthians
    [(5, 17), (9, 7), (12, 9), (4, 16), (5, 7)],
    # Galatians
    [(5, 22), (5, 23), (6, 7), (2, 20), (5, 16)],
    # Ephesians
    [(2, 8), (2, 9), (6, 10), (6, 11), (4, 32)],
    # Philippians
    [(4, 13), (4, 6), (4, 7), (4, 8), (1, 21)],
    # Colossians
    [(3, 2), (3, 23), (3, 16), (1, 16), (3, 12)],
    # 1 Thessalonians
    [(5, 16), (5, 17), (5, 18), (4, 16), (4, 17)],
    # 2 Thessalonians
    [(3, 3), (2, 15), (3, 5), (1, 7), (1, 8)],
    # 1 Timothy
    [(2, 5), (3, 16), (6, 10), (4, 12), (1, 15)],
    # 2 Timothy
    [(1, 7), (3, 16), (3, 17), (4, 7), (4, 8)],
    # Titus
    [(2, 11), (3, 5), (2, 13), (3, 4), (1, 2)],
    # Philemon
    [(1, 6), (1, 9), (1, 18), (1, 19), (1, 4)],
    # Hebrews
    [(11, 1), (4, 12), (13, 5), (12, 1), (12, 2)],
    # James
    [(1, 2), (1, 3), (1, 17), (2, 26), (4, 7)],
    # 1 Peter
    [(5, 7), (2, 24), (3, 15), (2, 9), (5, 8)],
    # 2 Peter
    [(3, 9), (1, 5), (1, 6), (1, 7), (3, 18)],
    # 1 John
    [(4, 8), (4, 18), (1, 9), (1, 7), (4, 19)],
    # 2 John
    [(1, 6), (1, 8), (1, 9), (1, 12), (1, 5)],
    # 3 John
    [(1, 4), (1, 2), (1, 11), (1, 8), (1, 7)],
    # Jude
    [(1, 3), (1, 24), (1, 22), (1, 23), (1, 21)],
    # Revelation
    [(3, 20), (1, 8), (21, 4), (22, 20), (1, 18)]
]

def download_file(filename):
    """Download an SGSS text file."""
    url = f"{BASE_URL}/{filename}"
    try:
        with urllib.request.urlopen(url) as resp:
            return resp.read().decode('utf-8')
    except Exception as e:
        print(f"  ERROR downloading {filename}: {e}")
        return None

def parse_verses(text):
    """
    Parse SGSS text file into a dict: {chapter: {verse: text}}
    """
    verses = {}
    current_chapter = 0
    
    for line in text.split('\n'):
        line = line.strip()
        
        # Skip empty lines and book title
        if not line:
            continue
        
        # Check for chapter header
        ch_match = re.match(r'^Chapter\s+(\d+)$', line)
        if ch_match:
            current_chapter = int(ch_match.group(1))
            if current_chapter not in verses:
                verses[current_chapter] = {}
            continue
        
        # Check for verse number
        v_match = re.match(r'^(\d+)\s+(.*)', line)
        if v_match and current_chapter > 0:
            verse_num = int(v_match.group(1))
            verse_text = v_match.group(2).strip()
            if current_chapter not in verses:
                verses[current_chapter] = {}
            if verse_num not in verses[current_chapter]:
                verses[current_chapter][verse_num] = verse_text
            else:
                # This shouldn't happen for well-formed files
                verses[current_chapter][verse_num] += " " + verse_text
    
    return verses

def extract_verse_text(verses, chapter, verse_num):
    """Get the text for a specific verse reference."""
    chapter_data = verses.get(chapter, {})
    text = chapter_data.get(verse_num, "")
    return text

def main():
    output_dir = os.path.dirname(os.path.abspath(__file__))
    
    all_verses = []
    total_books = len(BOOKS)
    
    for bi in range(total_books):
        book_name = BOOKS[bi]
        short_name = BOOK_SHORT[bi]
        filename = f"{bi+1:02d}-{book_name}.txt"
        refs = VERSE_REFS[bi]
        
        print(f"[{bi+1}/{total_books}] {book_name}...", end=" ")
        
        text = download_file(filename)
        if text is None:
            print("FAILED")
            continue
        
        verses = parse_verses(text)
        book_entries = []
        
        for (chapter, verse_num) in refs:
            verse_text = extract_verse_text(verses, chapter, verse_num)
            if verse_text:
                book_entries.append({
                    "book": book_name,
                    "short": short_name,
                    "chapter": chapter,
                    "verse": verse_num,
                    "text": verse_text,
                    "ref": f"{book_name} {chapter}:{verse_num}",
                    "shortRef": f"{short_name} {chapter}:{verse_num}"
                })
            else:
                print(f"\n  WARNING: {book_name} {chapter}:{verse_num} not found", end=" ")
        
        all_verses.append({
            "book": book_name,
            "index": bi,
            "verses": book_entries
        })
        
        print(f"{len(book_entries)} verses")
    
    # Flatten to ordered list
    flat = []
    for book_data in all_verses:
        flat.extend(book_data["verses"])
    
    output = {
        "meta": {
            "title": "SGSS Bible Verse Memorization (BVM)",
            "description": "5 popular verses from each book of the SGSS Bible",
            "totalVerses": len(flat),
            "totalBooks": total_books,
            "refreshMinutes": 5,
            "version": "SGSS"
        },
        "verses": flat
    }
    
    out_path = os.path.join(output_dir, "verses.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Done! {len(flat)} verses saved to {out_path}")

if __name__ == "__main__":
    main()

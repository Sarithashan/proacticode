def analyze_text(text):
    stats = {}
    words = text.split()
    stats["words"] = len(words)
    vowels = 0
    consonants = 0
    digits = 0
    spaces = 0
    punctuation = 0
    upper = 0
    lower = 0
    for ch in text:
        if ch.isalpha():
            if ch.lower() in "aeiou":
                vowels += 1
            else:
                consonants += 1
            if ch.isupper():
                upper += 1
            else:
                lower += 1
        elif ch.isdigit():
            digits += 1
        elif ch.isspace():
            spaces += 1
        else:
            punctuation += 1
    stats["vowels"] = vowels
    stats["consonants"] = consonants
    stats["digits"] = digits
    stats["spaces"] = spaces
    stats["punctuation"] = punctuation
    stats["upper"] = upper
    stats["lower"] = lower
    longest = ""
    for w in words:
        if len(w) > len(longest):
            longest = w
    stats["longest"] = longest
    if len(words) > 0:
        stats["avg_len"] = round(sum(len(w) for w in words) / len(words), 2)
    else:
        stats["avg_len"] = 0
    if len(words) > 0:
        stats["shortest"] = min(words, key=len)
    else:
        stats["shortest"] = ""
    return stats

import re

with open('frontend/app.js', 'r') as f:
    text = f.read()

# Fix the regex replace statements
text = text.replace(r"replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&')", r"replace(/[.*+?^${}()|[\]\\]/g, '\\$&')")

# Fix the RegExp constructors
text = text.replace(r"new RegExp(`\\\\b${safeAdmin}\\\\b`, 'i')", r"new RegExp(`\\b${safeAdmin}\\b`, 'i')")
text = text.replace(r"new RegExp(`\\\\b${safeSearchLoc}\\\\b`, 'i')", r"new RegExp(`\\b${safeSearchLoc}\\b`, 'i')")

with open('frontend/app.js', 'w') as f:
    f.write(text)

print("Fixed")

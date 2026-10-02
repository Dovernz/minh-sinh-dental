import re

with open('/app/src/components/Odontogram.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Increase width
content = re.sub(r'return 48; // molars.*?', r'return 64; // molars (enlarged 2x)', content)
content = re.sub(r'return 30; // incisors.*?', r'return 40; // incisors / canines (enlarged 2x)', content)
content = re.sub(r'return 36; // premolars.*?', r'return 48; // premolars (enlarged 2x)', content)

# Increase height of ToothSvg
content = re.sub(r'height=\{54\}', r'height=\{76\}', content)

# Increase SurfaceCircle size
content = re.sub(r'width=\{32\} height=\{32\}', r'width=\{48\} height=\{48\}', content)

# Increase midline divider
content = re.sub(r'h-28 mx-2', r'h-40 mx-4', content)

with open('/app/src/components/Odontogram.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

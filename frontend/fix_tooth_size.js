const fs = require('fs');
let content = fs.readFileSync('/app/src/components/Odontogram.tsx', 'utf8');

content = content.replace('return 48; // molars (enlarged ~1.5x)', 'return 64; // molars (enlarged 2x)');
content = content.replace('return 30; // incisors / canines (enlarged 1.5x)', 'return 40; // incisors / canines (enlarged 2x)');
content = content.replace('return 36; // premolars (enlarged 1.5x)', 'return 48; // premolars (enlarged 2x)');
content = content.replace('height={54}', 'height={80}');
content = content.replace('width={32} height={32}', 'width={48} height={48}');
content = content.replace('h-28 mx-2', 'h-40 mx-4');

fs.writeFileSync('/app/src/components/Odontogram.tsx', content, 'utf8');

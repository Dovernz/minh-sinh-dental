const fs = require('fs');
let content = fs.readFileSync('/app/src/components/Odontogram.tsx', 'utf8');

content = content.replace(/width=" 32\\n
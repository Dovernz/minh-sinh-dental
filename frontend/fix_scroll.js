const fs = require('fs');
let content = fs.readFileSync('/app/src/components/Odontogram.tsx', 'utf8');

content = content.replace('<div className=" flex flex-row bg-white w-full overflow-hidden text-gray-800 h-full\>',
import io

file_path = 'frontend/src/app/page.tsx'
with io.open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# The user explicitly said:
# "Nếu )} là dư thừa, hãy xóa nó đi."
# Let's remove the )} entirely! Wait, no. The error said "Unexpected token. Did you mean {'}'} or &rbrace;?"
# If we remove )}, it might just be fine! But wait, {currentStep === 3 && ( MUST be closed with )}.
# If <div> count is 30 and </div> count is 29, we just need ONE more </div>.
# Let's append </div> right before )}.

parts = content.rsplit(')}', 1)
if len(parts) == 2:
    new_content = parts[0] + '</div>\n        )}' + parts[1]
    with io.open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

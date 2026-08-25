import io

file_path = "frontend/src/app/page.tsx"
with io.open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('shadow-sm">
                <div', 'shadow-sm">\n                <div')
content = content.replace('</div>
              </div>

              {/* N?t', '</div>\n              </div>\n\n              {/* N?t')

old_wrapper = '<div className="max-h-[500px] overflow-y-auto border border-gray-200 rounded-lg shadow-sm">'
new_wrapper = '<div className="max-h-[400px] overflow-y-auto border border-gray-200 rounded-md relative shadow-sm">'
content = content.replace(old_wrapper, new_wrapper)

old_header = '<div className="flex bg-gray-50 border-b border-gray-200">'
new_header = '<div className="flex bg-white border-b border-gray-200 sticky top-0 z-10 shadow-sm">'
content = content.replace(old_header, new_header)

with io.open(file_path, "w", encoding="utf-8", newline='') as f:
    f.write(content)
print("Fixed")

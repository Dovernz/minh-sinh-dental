import os

file_path = "core/settings.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace 'DIRS': [], or 'DIRS': [] with 'DIRS': [os.path.join(BASE_DIR, 'templates')]
if "'DIRS': []," in content:
    content = content.replace("'DIRS': [],", "'DIRS': [os.path.join(BASE_DIR, 'templates')],")
elif "'DIRS': []" in content:
    content = content.replace("'DIRS': []", "'DIRS': [os.path.join(BASE_DIR, 'templates')]")
else:
    # Just in case they are already set or something else
    print("DIRS might already be set or format is different.")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated settings.py")

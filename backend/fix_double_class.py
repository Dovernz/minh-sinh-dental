files = [
    "operations/templates/admin/operations/dailyschedule/change_list.html",
    "operations/templates/admin/operations/weeklyschedule/change_list.html"
]
for file_path in files:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    content = content.replace('class="schedule-filter-form" class="flex gap-5 items-center flex-wrap"', 'class="schedule-filter-form flex gap-5 items-center flex-wrap"')
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

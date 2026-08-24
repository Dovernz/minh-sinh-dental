files = [
    "operations/templates/admin/operations/dailyschedule/change_list.html",
    "operations/templates/admin/operations/weeklyschedule/change_list.html"
]
for file_path in files:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    content = content.replace('class="p-4 mb-5 rounded-lg border border-gray-200 bg-white dark:bg-gray-800 dark:border-gray-700 dark:text-gray-200"', 'class="schedule-filter-wrapper p-4 mb-5 rounded-lg border border-gray-200 bg-white dark:bg-gray-800 dark:border-gray-700 dark:text-gray-200"')
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

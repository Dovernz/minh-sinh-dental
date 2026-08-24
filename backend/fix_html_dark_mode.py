import os

def replace_styles(content, replacements):
    for old, new in replacements:
        content = content.replace(old, new)
    # Add styling to h2 if not present
    if "<h2>" in content:
        content = content.replace("<h2>", '<h2 class="text-xl font-semibold mb-4 dark:text-gray-200">')
    return content

replacements_daily = [
    ('style="background: white; padding: 15px; margin-bottom: 20px; border-radius: 8px; border: 1px solid #ddd;"', 'class="p-4 mb-5 rounded-lg border border-gray-200 bg-white dark:bg-gray-800 dark:border-gray-700 dark:text-gray-200"'),
    ('style="display: flex; gap: 20px; align-items: center;"', 'class="flex gap-5 items-center flex-wrap"'),
    ('style="display: flex; align-items: center; gap: 8px;"', 'class="flex items-center gap-2"'),
    ('style="font-weight: bold; margin: 0;"', 'class="font-bold m-0 dark:text-gray-200"'),
    ('style="padding: 6px 12px; border: 1px solid #ccc; border-radius: 4px;"', 'class="px-3 py-1.5 border border-gray-300 rounded-md dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200"'),
    ('style="display: none; padding: 8px 16px; background-color: #417690; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;"', 'class="hidden px-4 py-2 bg-blue-600 text-white rounded-md font-bold cursor-pointer dark:bg-blue-500"'),
    ('style="width: 100%; border-collapse: collapse; text-align: center;"', 'class="w-full text-center border-collapse text-sm dark:text-gray-300"'),
    ('style="border: 1px solid #ccc; padding: 10px; background: #f8f8f8;"', 'class="border border-gray-300 p-2.5 bg-gray-50 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-200"'),
    ('style="border: 1px solid #ccc; padding: 10px; font-weight: bold; background: #f8f8f8;"', 'class="border border-gray-300 p-2.5 font-bold bg-gray-50 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-200"'),
    ('style="border: 1px solid #ccc; padding: 10px; vertical-align: top;"', 'class="border border-gray-300 p-2.5 align-top dark:border-gray-700"'),
    ('style="background: #e1f5fe; padding: 5px; border-radius: 4px; text-align: left; font-size: 13px;"', 'class="p-1.5 rounded-md text-left text-xs bg-blue-50 dark:bg-blue-900/50 dark:text-blue-100"'),
    ('style="color: #ccc;"', 'class="text-gray-400 dark:text-gray-600"'),
    ('style="color: #555;"', 'class="text-gray-600 dark:text-gray-400"'),
]

daily_file = "operations/templates/admin/operations/dailyschedule/change_list.html"
with open(daily_file, "r", encoding="utf-8") as f:
    content_daily = f.read()

content_daily = replace_styles(content_daily, replacements_daily)

with open(daily_file, "w", encoding="utf-8") as f:
    f.write(content_daily)


replacements_weekly = [
    ('style="background: white; padding: 15px; margin-bottom: 20px; border-radius: 8px; border: 1px solid #ddd;"', 'class="p-4 mb-5 rounded-lg border border-gray-200 bg-white dark:bg-gray-800 dark:border-gray-700 dark:text-gray-200"'),
    ('style="display: flex; gap: 20px; align-items: center;"', 'class="flex gap-5 items-center flex-wrap"'),
    ('style="display: flex; align-items: center; gap: 8px;"', 'class="flex items-center gap-2"'),
    ('style="font-weight: bold; margin: 0;"', 'class="font-bold m-0 dark:text-gray-200"'),
    ('style="padding: 6px 12px; border: 1px solid #ccc; border-radius: 4px;"', 'class="px-3 py-1.5 border border-gray-300 rounded-md dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200"'),
    ('style="display: none; padding: 8px 16px; background-color: #417690; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;"', 'class="hidden px-4 py-2 bg-blue-600 text-white rounded-md font-bold cursor-pointer dark:bg-blue-500"'),
    ('style="width: 100%; border-collapse: collapse; text-align: center;"', 'class="w-full text-center border-collapse text-sm dark:text-gray-300"'),
    ('style="border: 1px solid #ccc; padding: 10px; background: #f8f8f8;"', 'class="border border-gray-300 p-2.5 bg-gray-50 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-200"'),
    ('style="text-decoration: underline; color: blue; cursor: pointer;"', 'class="underline text-blue-600 dark:text-blue-400 cursor-pointer hover:text-blue-800 dark:hover:text-blue-300"'),
    ('style="border: 1px solid #ccc; padding: 10px; font-weight: bold; background: #f8f8f8;"', 'class="border border-gray-300 p-2.5 font-bold bg-gray-50 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-200"'),
    ('style="border: 1px solid #ccc; padding: 10px;"', 'class="border border-gray-300 p-2.5 dark:border-gray-700"'),
]

weekly_file = "operations/templates/admin/operations/weeklyschedule/change_list.html"
with open(weekly_file, "r", encoding="utf-8") as f:
    content_weekly = f.read()

content_weekly = replace_styles(content_weekly, replacements_weekly)

with open(weekly_file, "w", encoding="utf-8") as f:
    f.write(content_weekly)

print("Updated HTML templates")

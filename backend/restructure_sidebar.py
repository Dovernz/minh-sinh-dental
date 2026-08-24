file_path = "core/settings.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Rename "Hệ thống & Marketing" -> "Hệ thống & Quản trị User"
content = content.replace('"title": "Hệ thống & Marketing",', '"title": "Hệ thống & Quản trị User",')

# 2. Extract and remove "Nhân viên" from "Khách hàng & Dịch vụ"
employee_block = """                    {
                        "title": "Nhân viên",
                        "icon": "badge",
                        "link": "/admin/booking/employee/",
                    },
"""
if employee_block in content:
    content = content.replace(employee_block, "")
else:
    # try slightly different whitespace
    pass

# 3. Insert "Nhân viên" into "Hệ thống & Quản trị User" under "Nhóm quyền (Groups)"
group_block = """                    {
                        "title": "Nhóm quyền (Groups)",
                        "icon": "group",
                        "link": "/admin/auth/group/",
                    },
"""
if group_block in content:
    content = content.replace(group_block, group_block + employee_block)

# 4. Extract and remove "Bài viết" from "Hệ thống & Quản trị User"
article_block = """                    {
                        "title": "Bài viết",
                        "icon": "article",
                        "link": "/admin/booking/article/",
                    },
"""
if article_block in content:
    content = content.replace(article_block, "")

# 5. Create "Marketing" group with "Bài viết"
marketing_group = """            {
                "title": "Marketing",
                "icon": "campaign",
                "separator": True,
                "collapsible": True,
                "items": [
""" + article_block + """                ],
            },
"""

# Insert the Marketing group just before the Database group
database_group_start = """            {
                "title": "Database","""
if database_group_start in content:
    content = content.replace(database_group_start, marketing_group + database_group_start)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated Sidebar navigation!")

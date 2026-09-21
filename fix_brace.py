with open('backend/templates/admin/customer_360.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('''            }
        }
    }

    document.addEventListener("DOMContentLoaded", () => {''', '''            }
        }

    document.addEventListener("DOMContentLoaded", () => {''')

with open('backend/templates/admin/customer_360.html', 'w', encoding='utf-8') as f:
    f.write(html)

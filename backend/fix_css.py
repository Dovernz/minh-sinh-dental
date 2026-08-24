file_path = "static/css/admin_custom.css"
new_css = """/* Dark mode overrides for schedule filters and tables */
.dark .schedule-filter-wrapper {
    background-color: #1f2937 !important;
    border-color: #374151 !important;
    color: #e5e7eb !important;
}
.dark .schedule-filter-wrapper input,
.dark .schedule-filter-wrapper select {
    background-color: #374151 !important;
    border-color: #4b5563 !important;
    color: #e5e7eb !important;
}
.dark .results table {
    color: #d1d5db !important;
}
.dark .results table th {
    background-color: #1f2937 !important;
    border-color: #374151 !important;
    color: #e5e7eb !important;
}
.dark .results table td {
    background-color: #111827 !important;
    border-color: #374151 !important;
}
.dark .results table td.font-bold {
    background-color: #1f2937 !important;
}
.dark .results table td .bg-blue-50 {
    background-color: rgba(30, 58, 138, 0.5) !important;
    color: #dbeafe !important;
}
.dark .results table td .text-gray-600 {
    color: #9ca3af !important;
}
.dark .results table td .text-gray-400 {
    color: #6b7280 !important;
}
"""

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_css)

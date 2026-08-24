with open('booking/management/commands/setup_roles.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Add services proxy models to Reception
old_reception = " booking

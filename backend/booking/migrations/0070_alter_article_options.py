from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0069_alter_booking_group_code_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='article',
            options={'permissions': [('manage_wordpress_posts', '[WordPress] Có quyền quản lý và viết bài trên WordPress')]},
        ),
    ]
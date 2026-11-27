from django.db import migrations, models


def sync_inventory_pk_column(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        columns = [
            col.name
            for col in schema_editor.connection.introspection.get_table_description(
                cursor, 'db_table_inventory_details'
            )
        ]
        if 'item_id' in columns and 'inventory_id' not in columns:
            schema_editor.execute(
                'ALTER TABLE db_table_inventory_details RENAME COLUMN item_id TO inventory_id'
            )


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0068_booking_pnr_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='group_code',
            field=models.CharField(
                blank=True,
                db_index=True,
                max_length=50,
                null=True,
                verbose_name='Mã đặt chỗ',
            ),
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    sync_inventory_pk_column, migrations.RunPython.noop
                )
            ],
            state_operations=[
                migrations.AlterField(
                    model_name='inventorydetail',
                    name='item_id',
                    field=models.AutoField(
                        db_column='inventory_id',
                        primary_key=True,
                        serialize=False,
                    ),
                )
            ],
        ),
    ]
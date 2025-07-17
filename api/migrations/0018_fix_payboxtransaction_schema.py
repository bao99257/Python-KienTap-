from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_fix_payboxwallet_schema'),
    ]

    operations = [
        # Thêm cột order_id cho PayboxTransaction
        migrations.RunSQL(
            "ALTER TABLE api_payboxtransaction ADD COLUMN order_id BIGINT NULL",
            reverse_sql="ALTER TABLE api_payboxtransaction DROP COLUMN order_id"
        ),
        
        # Thêm foreign key constraint nếu cần
        migrations.RunSQL(
            "ALTER TABLE api_payboxtransaction ADD CONSTRAINT fk_paybox_order FOREIGN KEY (order_id) REFERENCES api_order(id) ON DELETE SET NULL",
            reverse_sql="ALTER TABLE api_payboxtransaction DROP FOREIGN KEY fk_paybox_order"
        ),
    ]
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_color_size_orderitem_color_name_orderitem_size_name_and_more'),
    ]

    operations = [
        # Thêm cột is_active
        migrations.RunSQL(
            "ALTER TABLE api_payboxwallet ADD COLUMN is_active TINYINT(1) NOT NULL DEFAULT 1",
            reverse_sql="ALTER TABLE api_payboxwallet DROP COLUMN is_active"
        ),
        
        # Thêm cột created_at
        migrations.RunSQL(
            "ALTER TABLE api_payboxwallet ADD COLUMN created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)",
            reverse_sql="ALTER TABLE api_payboxwallet DROP COLUMN created_at"
        ),
        
        # Sửa balance field từ decimal(10,2) thành decimal(12,0)
        migrations.RunSQL(
            "ALTER TABLE api_payboxwallet MODIFY COLUMN balance DECIMAL(12,0) NOT NULL DEFAULT 0",
            reverse_sql="ALTER TABLE api_payboxwallet MODIFY COLUMN balance DECIMAL(10,2) NOT NULL DEFAULT 0"
        ),
    ]
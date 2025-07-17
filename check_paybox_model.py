import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import PayboxWallet, PayboxTransaction
from django.db import connection

def check_paybox_model():
    """Kiểm tra model PayboxWallet và database schema"""
    
    print("🔍 Checking PayboxWallet model and database")
    print("=" * 50)
    
    # 1. Kiểm tra model fields
    print("\n1️⃣ Model fields:")
    for field in PayboxWallet._meta.get_fields():
        print(f"   - {field.name}: {type(field).__name__}")
    
    # 2. Kiểm tra database schema
    print("\n2️⃣ Database schema:")
    with connection.cursor() as cursor:
        cursor.execute("DESCRIBE api_payboxwallet")
        columns = cursor.fetchall()
        
        for column in columns:
            print(f"   - {column[0]}: {column[1]}")
    
    # 3. So sánh model vs database
    print("\n3️⃣ Comparison:")
    model_fields = [field.name for field in PayboxWallet._meta.get_fields() if hasattr(field, 'column')]
    
    with connection.cursor() as cursor:
        cursor.execute("DESCRIBE api_payboxwallet")
        db_columns = [column[0] for column in cursor.fetchall()]
    
    missing_in_db = set(model_fields) - set(db_columns)
    extra_in_db = set(db_columns) - set(model_fields)
    
    if missing_in_db:
        print(f"   ❌ Missing in database: {missing_in_db}")
    if extra_in_db:
        print(f"   ⚠️ Extra in database: {extra_in_db}")
    if not missing_in_db and not extra_in_db:
        print("   ✅ Model and database are in sync")
    
    # 4. Test query
    print("\n4️⃣ Test query:")
    try:
        count = PayboxWallet.objects.count()
        print(f"   ✅ Query successful: {count} wallets found")
    except Exception as e:
        print(f"   ❌ Query failed: {e}")

if __name__ == "__main__":
    check_paybox_model()
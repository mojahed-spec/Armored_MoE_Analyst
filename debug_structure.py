import os
import ast

# المسار الذي نشك فيه (بدون أرقام كما طلبت)
target_dir = os.path.join("app", "engine", "execution_team", "workers")

print(f"🔍 جاري فحص المجلد: {target_dir}\n")

# 1. هل المجلد موجود أصلاً؟
if not os.path.exists(target_dir):
    print(f"❌ كارثة: المجلد '{target_dir}' غير موجود!")
    print("تأكد أنك قمت بإعادة تسمية المجلدات (حذف الأرقام) يدوياً أو بالكود.")
    exit()

# 2. فحص محتوى الملفات
files = os.listdir(target_dir)
found_files = [f for f in files if f.endswith(".py") and f != "__init__.py"]

print(f"✅ تم العثور على {len(found_files)} ملفات بايثون.\n")

for filename in found_files:
    print(f"📄 الملف: {filename}")
    filepath = os.path.join(target_dir, filename)
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            # نستخدم مكتبة ast لقراءة الكود كـ "هيكل" واستخراج أسماء الدوال
            tree = ast.parse(f.read())
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            
            if functions:
                print(f"   └── الدوال (Functions): {functions}")
            if classes:
                print(f"   └── الكلاسات (Classes): {classes}")
            
            if not functions and not classes:
                print("   ⚠️ تحذير: الملف فارغ أو لا يحتوي على تعريفات!")
                
    except Exception as e:
        print(f"   ❌ خطأ في قراءة الملف: {e}")
    
    print("-" * 40)
@echo off
echo Replacing class_model.py with fixed version...
cd "C:\Users\gilbe\OneDrive\Desktop\RiddleNet"
copy "admin\models\class_model.py" "admin\models\class_model_backup.py"
copy "admin\models\class_model_fixed.py" "admin\models\class_model.py"
echo Running the application...
python run.py

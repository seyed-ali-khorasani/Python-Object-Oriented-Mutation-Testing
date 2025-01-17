import os
import sys
import unittest
import importlib.util
import shutil
import time

# جایگزینی ماژول اصلی یا جهش قبلی با جهش جدید
def replace_module_with_mutant(mutant_path, last_mutation_module):
    input_file = "test.py"
    with open(input_file, "r") as file:
        lines = file.readlines()
    lines[2] = f"from {last_mutation_module} import *\n"
    with open(input_file, "w") as file:
        file.writelines(lines)

# اجرای تست‌ها روی جهش‌یافته
def run_tests_with_mutant(mutant_path, last_mutation_module):
    # جایگزینی ماژول
    replace_module_with_mutant(mutant_path, last_mutation_module)
    time.sleep(1)
    if "test" in sys.modules:
        del sys.modules["test"]
    
    # اجرای تست‌ها
    loader = unittest.TestLoader()
    suite = loader.discover("", pattern="test.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result

# محاسبه Mutation Score
def calculate_mutation_score(mutant_files, mutation_list):
    killed_mutants = 0
    total_mutants = len(mutant_files)
    mutant_number = 0

    for mutant_path in mutant_files:
        print(f"Running tests on: {mutant_path}")
        result = run_tests_with_mutant(mutant_path, mutation_list[mutant_number])
        mutant_number += 1
        if len(result.failures) > 0 or len(result.errors) > 0:
            killed_mutants += 1

    mutation_score = (killed_mutants / total_mutants) * 100 if total_mutants > 0 else 0
    return mutation_score

if __name__ == "__main__":
    # جمع‌آوری فایل‌های جهش‌یافته
    mutant_dir = "src\\mutants"
    mutant_files = [os.path.join(mutant_dir, f) for f in os.listdir(mutant_dir) if f.endswith(".py")]

    mutants_list = mutant_files.copy()
    mut_number = 0
    for mut_file in mutants_list:
        mutants_list[mut_number] = mut_file.replace("\\", ".").replace(".py", "")
        mut_number += 1

    # محاسبه Mutation Score
    mutation_score = calculate_mutation_score(mutant_files, mutants_list)
    print(f"Mutation Score: {mutation_score:.2f}%")

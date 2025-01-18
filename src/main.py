import os
import os
import sys
import unittest
import importlib.util
import shutil
import time
from AMC import *
from IHI import *
from IHD import *
from IOD import *
from IOP import *
from IOR import *
from ISI import *
from ISD import *
from IPC import *
from PNC import *
from PMD import *
from PPD import *
from PCI import *
from PCD import *
from PPC import *
from PRV import *
from OMR import *
from OMD import *
from OAC import *
from prompt import *
import example as source_file

class CodeAnalyzer:
    def __init__(self, code_file):
        self.code_file = code_file
        self.code = self._read_code()
        self.tree = ast.parse(self.code)
        self.parent_child_map = self.find_parent_child_classes()
        self.class_info = self.extract_class_information()
        self.program_body_info = self.analyze_program_body()

    def _read_code(self):
        with open(self.code_file, 'r',encoding="utf-8") as f:
            return f.read()

    def find_parent_child_classes(self):
        parent_child_map = {}
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        parent_class = base.id
                        child_class = node.name
                        if parent_class not in parent_child_map:
                            parent_child_map[parent_class] = []
                        parent_child_map[parent_class].append(child_class)
        return parent_child_map

    def extract_class_information(self):
        class_info = {}
        for class_name, class_def in self.find_class_definitions().items():
            class_info[class_name] = {
                "methods": self.get_methods(class_def),
                "members": self.get_members(class_def),
                "access_modifiers": self.get_access_modifiers(class_def),
                "constructor_args": self.get_constructor_args(class_def),
                "super_calls": self.get_super_calls(class_def),
                "instantiations": self.find_instantiations(class_name),
            }
        return class_info

    def find_class_definitions(self):
        class_definitions = {}
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                class_definitions[node.name] = node
        return class_definitions

    def get_methods(self, class_def):
        methods = []
        for node in ast.walk(class_def):
            if isinstance(node, ast.FunctionDef):
                methods.append(node.name)
        return methods

    def get_members(self, class_def):
        members = []
        for node in ast.walk(class_def):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                        members.append(target.attr)
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Attribute) and isinstance(node.target.value, ast.Name) and node.target.value.id == 'self':
                    members.append(node.target.attr)
        return members

    def get_access_modifiers(self, class_def):
        access_modifiers = {}
        for member in self.get_members(class_def):
            if member.startswith("__") and not member.endswith("__"):
                access_modifiers[member] = "private"
            elif member.startswith("_"):
                access_modifiers[member] = "protected"
            else:
                access_modifiers[member] = "public"
        return access_modifiers

    def get_constructor_args(self, class_def):
        constructor_args = []
        for node in ast.walk(class_def):
            if isinstance(node, ast.FunctionDef) and node.name == "__init__":
                constructor_args = [arg.arg for arg in node.args.args if arg.arg != 'self']
                break
        return constructor_args

    def get_super_calls(self, class_def):
        super_calls = []
        for node in ast.walk(class_def):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'super':
                super_calls.append(ast.unparse(node))
        return super_calls

    def find_instantiations(self, class_name):
        instantiations = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
                if isinstance(node.value.func, ast.Name) and node.value.func.id == class_name:
                    instantiations.append(ast.unparse(node))
        return instantiations

    def analyze_program_body(self):
        program_body_info = {
            "method_calls": [],
            "type_casts": [],
            "assignments": [],
        }
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                if isinstance(node.value.func, ast.Attribute):
                    program_body_info["method_calls"].append(ast.unparse(node))
                elif isinstance(node.value.func, ast.Name):
                    if node.value.func.id in self.class_info:
                        program_body_info["type_casts"].append(ast.unparse(node))
            elif isinstance(node, ast.Assign):
                program_body_info["assignments"].append(ast.unparse(node))

        return program_body_info

# جایگزینی ماژول اصلی یا جهش قبلی با جهش جدید
def replace_module_with_mutant(mutant_path, last_mutation_module):
    input_file = "tests.py"
    with open(input_file, "r") as file:
        lines = file.readlines()
    lines[1] = f"from {last_mutation_module} import *\n"
    with open(input_file, "w") as file:
        file.writelines(lines)

# اجرای تست‌ها روی جهش‌یافته
def run_tests_with_mutant(mutant_path, last_mutation_module):
    # جایگزینی ماژول
    replace_module_with_mutant(mutant_path, last_mutation_module)
    time.sleep(1)
    if "tests" in sys.modules:
        del sys.modules["tests"]
    
    # اجرای تست‌ها
    loader = unittest.TestLoader()
    suite = loader.discover("", pattern="tests.py")
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

    code_analyzer = CodeAnalyzer("src\example.py")
    analyze=f"{str(code_analyzer.parent_child_map)}\n{str(code_analyzer.class_info)}"
    genai.configure(api_key='AIzaSyCoYdQWfEmFUIT-FoUYk-fazYrM2NbIQ-s')
    model = genai.GenerativeModel("gemini-2.0-flash-exp", system_instruction=PROMPT)
    chat = model.start_chat()
    response = chat.send_message(analyze)
    operator_list = [line for line in response.text.strip().splitlines() if line.strip()]
    #opertor_list = ["AMC","IHI","IHD","IOD","IOP","IOR","ISI","ISD",
                    "IPC","PNC","PMD","PPD","PCI","PCD","PPC","PRV",
                    "OMR","OMD","OAC"]
    
    for operator in opertor_list:
        match operator:
            case "AMC":
                acm_mut = ACMMutation("src\example.py")
                acm_mut.mutate_amc()
            case "IHI":
                ihi_mut = IHIMutation("src\example.py")
                ihi_mut.mutate_ihi()
            case "IHD":
                ihd_mut = IHDMutation("src\example.py")
                ihd_mut.mutate_ihd()
            case "IOD":
                iod_mut = IODMutation("src\example.py")
                iod_mut.mutate_iod()
            case "IOP":
                iop_mut = IOPMutation("src\example.py")
                iop_mut.mutate_iop()
            case "IOR":
                ior_mut = IORMutation("src\example.py")
                ior_mut.mutate_ior()
            case "ISI":
                isi_mut = ISIMutation("src\example.py")
                isi_mut.mutate_isi()
            case "ISD":
                isd_mut = ISDMutation("src\example.py")
                isd_mut.mutate_isd()
            case "IPC":
                ipc_mut = IPCMutation("src\example.py")
                ipc_mut.mutate_ipc()
            case "PNC":
                pnc_mut = PNCMutation("src\example.py")
                pnc_mut.mutate_pnc()
            case "PMD":
                pmd_mut = PMDMutation("src\example.py")
                pmd_mut.mutate_pmd()
            case "PPD":
                ppd_mut = PPDMutation("src\example.py")
                ppd_mut.mutate_ppd()
            case "PCI":
                pci_mut = PCIMutation("src\example.py")
                pci_mut.mutate_pci()
            case "PCD":
                pcd_mut = PCDMutation("src\example.py")
                pcd_mut.mutate_pcd()
            case "PPC":
                ppc_mut = PPCMutation("src\example.py")
                ppc_mut.mutate_ppc()
            case "PRV":
                prv_mut = PRVMutation("src\example.py")
                prv_mut.mutate_prv()
            case "OMR":
                omr_mut = OMRMutation("src\example.py")
                omr_mut.mutate_omr()
            case "OMD":
                omd_mut = OMDMutation("src\example.py")
                omd_mut.mutate_omd()
            case "OAC":
                oac_mut = OACMutation("src\example.py")
                oac_mut.mutate_oac()
    
    

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

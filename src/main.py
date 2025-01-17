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
import example as source_file

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

    opertor_list = ["AMC","IHI","IHD","IOD","IOP","IOR","ISI","ISD",
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
import unittest
from src.mutants.example_PCI_SubClass_ParentClass import *
import sys

class TestParentClass(unittest.TestCase):

    def test_AMC(self):
        parent_instance = ParentClass('ParentValue')
        subclass_instance = SubClass('SubValue', 'ExtraValue')
        another_subclass_instance = AnotherSubClass('AnotherValue', 'ExtraInfo', 'AdditionalInfo')

        self.assertEqual(parent_instance._ParentClass__private_value, 'ParentValue')
        self.assertEqual(parent_instance._protected_status, 'active')
        self.assertEqual(parent_instance.public_id, 123)
        

        self.assertEqual(subclass_instance._SubClass__private_extra, 'ExtraValue')
        self.assertEqual(subclass_instance._protected_flag, True)

        self.assertEqual(another_subclass_instance._AnotherSubClass__private_additional, 'AdditionalInfo')
        self.assertEqual(another_subclass_instance._protected_extra, 'ExtraInfo')

    def test_IHI(self):
        parent_instance = ParentClass('ParentValue')
        subclass_instance = SubClass('SubValue', 'ExtraValue')
        another_subclass_instance = AnotherSubClass('AnotherValue', 'ExtraInfo', 'AdditionalInfo')
        
        self.assertEqual(subclass_instance._protected_status, 'active')
        self.assertEqual(another_subclass_instance._protected_status, 'active')

    def test_IHD(self):
        parent_instance = ParentClass('ParentValue')
        subclass_instance = SubClass('SubValue', 'ExtraValue')
        another_subclass_instance = AnotherSubClass('AnotherValue', 'ExtraInfo', 'AdditionalInfo')
        
        self.assertEqual(subclass_instance.public_id, "sub_public")
        self.assertEqual(another_subclass_instance.public_id, None)
        self.assertEqual(another_subclass_instance._AnotherSubClass__private_value, None)

    def test_IOP(self):
        parent_instance = ParentClass('ParentValue')
        subclass_instance = SubClass('SubValue', 'ExtraValue')
        another_subclass_instance = AnotherSubClass('AnotherValue', 'ExtraInfo', 'AdditionalInfo')
        
        self.assertEqual(subclass_instance.public_id, "sub_public")
        self.assertEqual(another_subclass_instance.public_id, None)
        


    def test_IOR_and_IOD(self):
        parent_instance = ParentClass('ParentValue')
        subclass_instance = SubClass('SubValue', 'ExtraValue')
        another_subclass_instance = AnotherSubClass('AnotherValue', 'ExtraInfo', 'AdditionalInfo')
        
        self.assertEqual(subclass_instance.method_one(), "SubClass method_one: sub_public and ExtraValue")
        self.assertEqual(subclass_instance.method_two(), "Parent method_two: SubValue with SubClass extra: ExtraValue")
        self.assertEqual(another_subclass_instance.method_two(), "SubClass method_two: Another Subclass and AdditionalInfo and extra argument is: default")
        self.assertEqual(another_subclass_instance.method_one(), "SubClass method_one: SubClass method_two: Another Subclass and AdditionalInfo and extra argument is: default and AdditionalInfo and extra argument is: default")
        self.assertEqual(another_subclass_instance.method_three(), "SubClass method_three: Another Subclass and AdditionalInfo and extra argument is: default")

    def test_ISI(self):
        parent_instance = ParentClass('ParentValue')
        another_subclass_instance = AnotherSubClass('AnotherValue', 'ExtraInfo', 'AdditionalInfo')
        
        self.assertEqual(another_subclass_instance.method_one(), "SubClass method_one: SubClass method_two: Another Subclass and AdditionalInfo and extra argument is: default and AdditionalInfo and extra argument is: default")


    def test_ISD(self):
        parent_instance = ParentClass('ParentValue')
        subclass_instance = SubClass('SubValue', 'ExtraValue')
        another_subclass_instance = AnotherSubClass('AnotherValue', 'ExtraInfo', 'AdditionalInfo')
        
        self.assertEqual(subclass_instance.method_one(), "SubClass method_one: sub_public and ExtraValue")
        self.assertEqual(subclass_instance.method_two(), "Parent method_two: SubValue with SubClass extra: ExtraValue")
        self.assertEqual(another_subclass_instance.method_two("test IOD"), "SubClass method_two: Another Subclass and AdditionalInfo and extra argument is: test IOD")

    def test_IPC(self):
        parent_instance = ParentClass('ParentValue')
        subclass_instance = SubClass('SubValue', 'ExtraValue')
        another_subclass_instance = AnotherSubClass('AnotherValue', 'ExtraInfo', 'AdditionalInfo')
        
        self.assertEqual(subclass_instance._protected_status, "active")
        self.assertEqual(another_subclass_instance._protected_status, "active")
    
    
    def test_PNC(self):

        parent_instance_type = ParentClass("temp")
        
        self.assertEqual(type(parent_instance), type(parent_instance_type))

    def test_PMD(self):

        self.assertEqual(type(pmd_parent_instance), type(parent_instance))


    def test_PPD(self):

        self.assertEqual(sample(ppd_parent_instance), type(parent_instance))

    def test_PCI(self):
        
        self.assertEqual(type(pci_subclass_instance_type), type(subclass_instance_type))   
        self.assertEqual(type(pci_another_subclass_instance_type), type(another_subclass_instance_type))
    
    def test_PCD(self):
        
        self.assertEqual(type(pcd_subclass_instance_type), type(parent_instance))   
        self.assertEqual(type(pcd_another_subclass_instance_type), type(parent_instance))

    def test_PPC(self):
        
        self.assertEqual(type(ppc_change_type_subclass), type(subclass_instance_type))   
        self.assertEqual(type(ppc_change_type_anotherclass), type(another_subclass_instance_type))

    def test_PRV(self):
        
        self.assertEqual(type(prv_change_parent_to_subclass), type(subclass_instance_type))

    def test_OMR_and_OMD(self):
        
        parent_instance = ParentClass('ParentValue')
        subclass_instance = SubClass('SubValue', 'ExtraValue')
        another_subclass_instance = AnotherSubClass('AnotherValue', 'ExtraInfo', 'AdditionalInfo')

        self.assertEqual(parent_instance.method_one(), "Parent method_one: ParentValue")   
        self.assertEqual(parent_instance.method_two(), "Parent method_two: ParentValue")
        self.assertEqual(subclass_instance.method_one(), "SubClass method_one: sub_public and ExtraValue")
        self.assertEqual(subclass_instance.method_two(), "Parent method_two: SubValue with SubClass extra: ExtraValue")
        self.assertEqual(another_subclass_instance.method_two(), "SubClass method_two: Another Subclass and AdditionalInfo and extra argument is: default")
        self.assertEqual(another_subclass_instance.method_three(), "SubClass method_three: Another Subclass and AdditionalInfo and extra argument is: default")


    def test_OAC(self):
        
        self.assertEqual(oac_sub_met_two_res, "SubClass method_two: Another Subclass and AdditionalInfo and extra argument is: default")   
        self.assertEqual(oac_sub_met_three_res, "SubClass method_three: Another Subclass and AdditionalInfo and extra argument is: default")


def main(out = sys.stderr, verbosity = 2): 
    loader = unittest.TestLoader() 
  
    suite = loader.loadTestsFromModule(sys.modules[__name__]) 
    unittest.TextTestRunner(out, verbosity = verbosity).run(suite) 






if __name__ == '__main__':
    unittest.main()

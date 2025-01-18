

class ParentClass():
    def __init__(self, value):
        self.__private_value = value
        self._protected_status = 'active'
        self.public_id = 123

    def method_one(self):
        return f'Parent method_one: {self.__private_value}'

    def method_two(self):
        return f'Parent method_two: {self.__private_value}'
    
    def method_three(self):
        return f'Parent method_three: {self.__private_value}'

class SubClass(ParentClass):
    def __init__(self, value, extra):
        super().__init__(value)
        self.__private_extra = extra
        self._protected_flag = True
        self.public_description = 'Subclass instance'
        self.public_id = "sub_public"

    def method_one(self):
        return f'SubClass method_one: {self.public_id} and {self.__private_extra}'

    def method_two(self):
        return f'{super().method_two()} with SubClass extra: {self.__private_extra}'

class AnotherSubClass(ParentClass):
    def __init__(self, value, extra, additional):
        super().__init__(value)
        self.__private_additional = additional
        self._protected_extra = extra
        self.public_label = 'Another Subclass'
        self.__private_value = None
        self.public_id = None

    def method_one(self, extra_arg = "default"):
        return f"SubClass method_one: {self.method_two()} and {self.__private_additional} and extra argument is: {extra_arg}"

    def method_two(self, extra_arg = "default"):
        return f"SubClass method_two: {self.public_label} and {self.__private_additional} and extra argument is: {extra_arg}"

    def method_three(self, extra_arg = "default"):
        return f"SubClass method_three: {self.public_label} and {self.__private_additional} and extra argument is: {extra_arg}"
    

def sample(temp:ParentClass):
    return type(temp)
    
    
    

parent_instance = ParentClass('ParentValue')
subclass_instance = SubClass('SubValue', 'ExtraValue')
another_subclass_instance = AnotherSubClass('AnotherValue', 'ExtraInfo', 'AdditionalInfo')

prv_change_parent_to_subclass = ParentClass("prv test")
prv_change_parent_to_anothersubclass = ParentClass("prv test")

pcd_subclass_instance_type = SubClass('SubValue', 'ExtraValue')
pcd_another_subclass_instance_type = AnotherSubClass('AnotherValue', 'ExtraInfo', 'AdditionalInfo')

ppd_parent_instance = ParentClass('ParentValue')

pmd_parent_instance :ParentClass=ParentClass(2)



subclass_instance_type = SubClass('SubValue', 'ExtraValue')
another_subclass_instance_type = AnotherSubClass('AnotherValue', 'ExtraInfo', 'AdditionalInfo')



oac_sub_met_two_res = another_subclass_instance.method_two()
oac_sub_met_three_res = another_subclass_instance.method_three()

ppc_change_type_subclass = SubClass(parent_instance, "sdfsdf")
ppc_change_type_anotherclass = AnotherSubClass(parent_instance, "Sdfsdf", "sdfsdf")

prv_change_parent_to_subclass = subclass_instance
prv_change_parent_to_anothersubclass = another_subclass_instance

pcd_subclass_instance_type = ParentClass(pcd_subclass_instance_type)
pcd_another_subclass_instance_type = ParentClass(pcd_another_subclass_instance_type)

pci_subclass_instance_type = SubClass('SubValue', 'ExtraValue')
pci_another_subclass_instance_type = AnotherSubClass('AnotherValue', 'ExtraInfo', 'AdditionalInfo')

sample(ppd_parent_instance)

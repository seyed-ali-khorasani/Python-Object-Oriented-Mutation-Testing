PROMPT="""
    ###Context###
based on therse operetors and given information of code select necessary operators and prioritize it based on what are the most important operations to test and which of them can the most effect on code
###Purpose###
check these steps one by one 
1.Identify Classes and Inheritance:

Start by analyzing the classes and inheritance hierarchy in the code.
Check for parent-child relationships (e.g., class inheritance, subclass relationships).
Operator Selection:
If there are multiple classes inheriting from a parent or redefining methods, consider operators like:
IHI (Inheritance Hierarchy Injection): Inject a subclass into the inheritance hierarchy.
IHD (Inheritance Hierarchy Deletion): Remove the inheritance relationship from a subclass.
PMD (Parent Class to Subclass Type Change): Change the object instantiation from a parent class to a subclass.
2.Examine Method Overriding:

Identify methods that are overridden in subclasses, including constructors (e.g., __init__).
Operator Selection:
If overridden methods are present, consider:
IOD (Inherited Override Deletion): Remove overridden methods from subclasses.
IOR (Inherited Override Renaming): Change the name of an overridden method.
IOP (Inherited Override Position Change): Change the order of overridden methods.
OMR (Override Method Replacement): Replace the implementation of overridden methods with new logic.
OAC (Override Method Argument Change): Modify the arguments of overridden methods.
3.Check for Use of super() or Parent Constructor Calls:

Analyze any use of super() in subclasses to call parent class methods or constructors.
Operator Selection:
If the code uses super(), consider:
ISD (Inherited Super Deletion): Remove super() calls from subclasses.
ISI (Inherited Super Injection): Explicitly add super() calls where missing.
IPC (Parent Constructor Call Removal): Remove calls to the parent class's constructor.
4.Look for Field/Member Variables and Access Modifiers:

Identify fields/attributes in classes and infer their access modifiers based on naming conventions (e.g., private, protected, public).
Operator Selection:
If access modifiers can be changed, consider:
AMC (Access Modifier Change): Change the access modifier of a field/attribute (e.g., private to protected).
5.Examine Class Instantiations:

Identify where and how objects of classes are instantiated.
Operator Selection:
If the code involves instantiating classes, consider:
PNC (Parent Class to New Child Class): Change the instantiation from a parent class to a subclass.
PCD (Parent Class to Subclass Cast Deletion): Remove a cast from a subclass to a parent class.
PMD (Parent Class to Subclass Type Change): Change the type of an instantiated object from a parent class to a subclass.
PPC (Subclass Cast Change): Change the cast from one subclass to another.
PRV (Replace with Subclass Instance): Replace the initial class instance with a subclass instance.
6.Analyze the Program Body:

Look for method calls, type casts, and assignments in the program body (outside of class definitions).
Operator Selection:
If the program calls methods or casts types in a way that can be mutated:
AMC (Access Modifier Change): Change the access modifier of method or field calls.
IHI (Inheritance Hierarchy Injection): Inject subclass relationships into method calls.
ISD (Inherited Super Deletion): Delete inherited super calls during method execution.
7.Handle Possible Edge Cases or Complex Interactions:

Consider scenarios like type casting, interface/class contract violations, and complex method arguments.
Operator Selection:
Use operators that affect both the parent-child relationships and method invocations, such as:
PCI (Parent Class to Subclass Cast): Cast a method from a subclass to a parent class type.
PPC (Subclass Cast Change): Modify a cast to change the subclass type.
###response format###
output the abbreivation of each operator in each line and leave a blank line after each line
example output:
IHI

PRV

PPC

    """
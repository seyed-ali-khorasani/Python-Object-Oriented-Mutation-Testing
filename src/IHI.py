import ast
import astunparse
import itertools
import copy

i=0

class IHIMutation:
    def __init__(self, code_file):
        self.code_file = code_file
        self.original_code = self._read_code()
        self.original_ast = self._parse_code(self.original_code)

    def _read_code(self):
        with open(self.code_file, 'r') as f:
            return f.read()

    def _parse_code(self, code):
        return ast.parse(code)

    def _to_code(self, tree):
        return astunparse.unparse(tree)

    def save_code(self, mutated_code, mutation_type, mutation_details):
        global i
        """Saves the mutated code to a new file only if it's different from the original."""
        temp_code_file = self.code_file
        temp_code_file = temp_code_file.replace("src", "src\\mutants")
        filename = f"{temp_code_file.replace('.py', '')}_{mutation_type}_{'_'.join(mutation_details)}.py"
        i+=1
        #filename=f"mutation{i}.py"
        # Normalize the code to ignore formatting differences
        original_code_normalized = astunparse.unparse(ast.parse(self.original_code))
        mutated_code_normalized = astunparse.unparse(ast.parse(mutated_code))
        try:
            if original_code_normalized != mutated_code_normalized:
                
                    with open(filename, 'w') as f:
                        f.write(mutated_code)
                    print(f"Saved mutated code to: {filename}")
            else:
                        print(f"Skipped saving {filename} (no changes from original)")
        except:
                    print("dup")

    def restore_original(self):
        """Restores the original code and AST."""
        self.original_code = self._read_code()
        self.original_ast = self._parse_code(self.original_code)
        print("Original code restored.")
    
    def detect_access_modifiers(self, code_snippet):
            """Detects instance variables and their implied access modifiers."""
            tree = ast.parse(code_snippet)
            instance_variables = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                            attribute_name = target.attr
                            modifier = "public"
                            if attribute_name.startswith("__") and not attribute_name.endswith("__"):
                                modifier = "private"
                            elif attribute_name.startswith("_") and not attribute_name.startswith("__"):
                                modifier = "protected"
                            instance_variables.append({"name": attribute_name, "modifier": modifier})
                elif isinstance(node, ast.AnnAssign):
                    if isinstance(node.target, ast.Attribute) and isinstance(node.target.value, ast.Name) and node.target.value.id == 'self':
                        attribute_name = node.target.attr
                        modifier = "public"
                        if attribute_name.startswith("__") and not attribute_name.endswith("__"):
                            modifier = "private"
                        elif attribute_name.startswith("_") and not attribute_name.startswith("__"):
                            modifier = "protected"
                        instance_variables.append({"name": attribute_name, "modifier": modifier})

            return instance_variables
    

    def mutate_ihi(self):
        """Applies Inheritance Hierarchy Insertion (IHI) mutations."""
        print("Applying IHI mutations...")
        tree = self._parse_code(self.original_code)
        class_definitions = {}  # Store class definitions

        # First pass: Collect class definitions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_definitions[node.name] = node

        # Second pass: Apply mutations
        for class_name, class_def in class_definitions.items():
            if class_def.bases:  # Check if the class has parent(s)
                for base in class_def.bases:
                    if isinstance(base, ast.Name) and base.id in class_definitions:
                        parent_class_name = base.id
                        parent_class_def = class_definitions[parent_class_name]
                        parent_vars = self.detect_access_modifiers(astunparse.unparse(parent_class_def))

                        if parent_vars:
                            mutated_tree = ast.parse(self.original_code)
                            mutated_class_def = None

                            # Find the mutated class definition in the new AST
                            for mutate_node in ast.walk(mutated_tree):
                                if isinstance(mutate_node, ast.ClassDef) and mutate_node.name == class_name:
                                    mutated_class_def = mutate_node
                                    break

                            if mutated_class_def:
                                # Find the __init__ method or create one
                                init_method = None
                                for body_node in mutated_class_def.body:
                                    if isinstance(body_node, ast.FunctionDef) and body_node.name == "__init__":
                                        init_method = body_node
                                        break

                                if not init_method:
                                    init_method = ast.FunctionDef(
                                        name="__init__",
                                        args=ast.arguments(
                                            posonlyargs=[],
                                            args=[ast.arg(arg="self", annotation=None, type_comment=None)],
                                            vararg=None,
                                            kwonlyargs=[],
                                            kw_defaults=[],
                                            kwarg=None,
                                            defaults=[]
                                        ),
                                        body=[],
                                        decorator_list=[],
                                        returns=None,
                                        type_comment=None
                                    )
                                    mutated_class_def.body.insert(0, init_method)  # Insert at the beginning

                                # Add parent variables to the __init__ method
                                for parent_var in parent_vars:
                                    init_method.body.append(
                                        ast.Assign(
                                            targets=[ast.Attribute(
                                                value=ast.Name(id='self', ctx=ast.Load()),
                                                attr=parent_var['name'],
                                                ctx=ast.Store()
                                            )],
                                            value=ast.Constant(value=None, kind=None),  # You can assign a default value here
                                            type_comment=None
                                        )
                                    )

                                mutated_code = astunparse.unparse(mutated_tree)
                                self.save_code(mutated_code, "IHI", [class_name, parent_class_name])

        self.restore_original()
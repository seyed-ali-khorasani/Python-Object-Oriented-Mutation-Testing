import ast
import astunparse
import itertools
import copy

i=0
class ISIMutation:
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

    def mutate_isi(self):
        """Applies Super Insertion (ISI) mutations."""
        print("Applying ISI mutations...")
        tree = ast.parse(self.original_code)
        class_definitions = {}

        # First pass: Collect class definitions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_definitions[node.name] = node

        # Second pass: Apply mutations
        for class_name, class_def in class_definitions.items():
            if class_def.bases:
                for base in class_def.bases:
                    if isinstance(base, ast.Name) and base.id in class_definitions:
                        parent_class_name = base.id
                        parent_class_def = class_definitions[parent_class_name]

                        # Get parent methods
                        parent_methods = {node.name: node for node in parent_class_def.body if isinstance(node, ast.FunctionDef)}

                        # Iterate through child methods
                        for child_method_node in class_def.body:
                            if isinstance(child_method_node, ast.FunctionDef):
                                mutated_tree = ast.parse(self.original_code)
                                mutated_class_def = None
                                mutated_method_node = None

                                # Find the mutated class definition
                                for mutate_node in ast.walk(mutated_tree):
                                    if isinstance(mutate_node, ast.ClassDef) and mutate_node.name == class_name:
                                        mutated_class_def = mutate_node
                                        break

                                # Find the mutated method within the mutated class
                                if mutated_class_def:
                                    for mutate_node in mutated_class_def.body:
                                        if isinstance(mutate_node, ast.FunctionDef) and mutate_node.name == child_method_node.name:
                                            mutated_method_node = mutate_node
                                            break

                                if mutated_class_def and mutated_method_node:
                                    # Traverse the method body and insert super() calls (only for method calls)
                                    for node in ast.walk(mutated_method_node):
                                        if isinstance(node, ast.Call):
                                            if isinstance(node.func, ast.Attribute):
                                                if isinstance(node.func.value, ast.Name) and node.func.value.id == 'self':
                                                    method_name = node.func.attr
                                                    if method_name in parent_methods:
                                                        # Modify the method call to use super()
                                                        node.func.value.id = 'super()'

                                    mutated_code = astunparse.unparse(mutated_tree)
                                    self.save_code(mutated_code, "ISI", [class_name, parent_class_name, child_method_node.name])

        self.restore_original()

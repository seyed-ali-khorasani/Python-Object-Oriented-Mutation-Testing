import ast
import astunparse
import itertools
import copy

i=0

class IHDMutation:
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
    
    def mutate_ihd(self):
        """Applies Inheritance Hierarchy Deletion (IHD) mutations."""
        print("Applying IHD mutations...")
        tree = self._parse_code(self.original_code)
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

                        # Get parent variables as strings
                        parent_vars = [f"self.{var['name']}" for var in
                                       self.detect_access_modifiers(astunparse.unparse(class_definitions[parent_class_name]))]

                        if parent_vars:
                            mutated_tree = ast.parse(self.original_code)
                            mutated_class_def = None

                            # Find the mutated class definition
                            for mutate_node in ast.walk(mutated_tree):
                                if isinstance(mutate_node, ast.ClassDef) and mutate_node.name == class_name:
                                    mutated_class_def = mutate_node
                                    break

                            if mutated_class_def:
                                # Accurately delete only inherited variables
                                new_body = []
                                for node in mutated_class_def.body:
                                    if isinstance(node, ast.FunctionDef) and node.name == "__init__":
                                        new_init_body = []
                                        for init_node in node.body:
                                            delete = False
                                            if isinstance(init_node, (ast.Assign, ast.AnnAssign)):
                                                targets = [init_node.target] if isinstance(init_node, ast.AnnAssign) else init_node.targets
                                                for target in targets:
                                                    # Get the full variable name as a string
                                                    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                                                        target_var_name = astunparse.unparse(target).strip()
                                                        if target_var_name in parent_vars:
                                                            delete = True
                                                            break  # No need to check other targets in this assignment
                                            if not delete:
                                                new_init_body.append(init_node)
                                        node.body = new_init_body
                                        new_body.append(node)
                                    
                                    else:
                                        new_body.append(node)

                                mutated_class_def.body = new_body
                                mutated_code = astunparse.unparse(mutated_tree)
                                self.save_code(mutated_code, "IHD", [class_name, parent_class_name])

        self.restore_original()

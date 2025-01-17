import ast
import astunparse
import itertools
import copy

i=0
class IOPMutation:
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


    def mutate_iop(self):
        """Applies Overridden Method Calling Position Change (IOP) mutations."""
        print("Applying IOP mutations...")
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
                        parent_methods = [node.name for node in parent_class_def.body if isinstance(node, ast.FunctionDef)]

                        # Iterate through child methods of the *current* class
                        for child_method_node in class_def.body:
                            if isinstance(child_method_node, ast.FunctionDef) and child_method_node.name in parent_methods:
                                # Get the body of the method
                                method_body = child_method_node.body

                                # Separate super().__init__() call
                                super_call = None
                                other_statements = []
                                for stmt in method_body:
                                    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call) and \
                                            isinstance(stmt.value.func, ast.Attribute) and \
                                            stmt.value.func.attr == "__init__" and \
                                            isinstance(stmt.value.func.value, ast.Call) and \
                                            stmt.value.func.value.func.id == "super":
                                        super_call = stmt
                                    else:
                                        other_statements.append(stmt)

                                # Generate permutations of statements excluding super().__init__()
                                for permutation in itertools.permutations(other_statements):
                                    mutated_tree = ast.parse(self.original_code)
                                    mutated_class_def = None
                                    mutated_method_node = None

                                    # Find the mutated class definition
                                    for mutate_node in ast.walk(mutated_tree):
                                        if isinstance(mutate_node, ast.ClassDef) and mutate_node.name == class_name:
                                            mutated_class_def = mutate_node
                                            break  # Stop searching after finding the class

                                    # Find the mutated method within the mutated class
                                    if mutated_class_def:
                                        for mutate_node in mutated_class_def.body:
                                            if isinstance(mutate_node, ast.FunctionDef) and mutate_node.name == child_method_node.name:
                                                mutated_method_node = mutate_node
                                                break  # Stop searching after finding the method

                                    if mutated_class_def and mutated_method_node:
                                        # Update the method body with the permuted statements
                                        new_body = []
                                        if super_call:
                                            # Place super().__init__() at the end, changing the position
                                            new_body.extend(list(permutation))
                                            new_body.append(super_call)  # Add super().__init__() at the end
                                        else:
                                            new_body.extend(list(permutation))  # If no super() call, just permute the body

                                        mutated_method_node.body = new_body

                                        mutated_code = astunparse.unparse(mutated_tree)
                                        self.save_code(mutated_code, "IOP", [class_name, parent_class_name, child_method_node.name])

        self.restore_original()
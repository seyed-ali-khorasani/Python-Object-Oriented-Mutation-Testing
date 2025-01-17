import ast
import astunparse
import itertools
import copy

i=0
class PPDMutation:
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
    
    def find_parent_child_classes(self):
        """
        Finds parent-child class relationships in the code.

        Returns:
            A dictionary where keys are parent class names and values are lists of
            their corresponding child class names.
        """
        parent_child_map = {}
        tree = ast.parse(self.original_code)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        parent_class = base.id
                        child_class = node.name
                        if parent_class not in parent_child_map:
                            parent_child_map[parent_class] = []
                        parent_child_map[parent_class].append(child_class)
        return parent_child_map


    def mutate_ppd(self):
        """Applies Parameter Variable Declaration with Child Class Type (PPD) mutations."""
        print("Applying PPD mutations...")
        parent_child_map = self.find_parent_child_classes()
        original_code_lines = self.original_code.splitlines(keepends=True)

        for parent_class, child_classes in parent_child_map.items():
            for child_class in child_classes:
                tree = ast.parse(self.original_code)
                mutated_tree = copy.deepcopy(tree)
                mutated_code_lines = list(original_code_lines)

                for node in ast.walk(mutated_tree):
                    if isinstance(node, ast.FunctionDef):
                        for arg in node.args.args:
                            if isinstance(arg.annotation, ast.Name) and arg.annotation.id == parent_class:
                                # Change the type annotation to the child class
                                arg.annotation.id = child_class

                                # Save mutated code
                                mutated_code = astunparse.unparse(mutated_tree)
                                self.save_code(mutated_code, "PPD", [parent_class, child_class])

                                # Restore for the next mutation
                                mutated_tree = copy.deepcopy(tree)
                                mutated_code_lines = list(original_code_lines)

                self.restore_original()
                original_code_lines = self.original_code.splitlines(keepends=True)

        print("Finished PPD mutations.")


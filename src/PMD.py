import ast
import astunparse
import copy
import inspect
import random

i = 0
class PMDMutation:
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
        i += 1
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
            print("Error while saving the mutated code")

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

    def get_constructor_arguments(self, class_name):
        """
        Extracts the constructor arguments for a given class from the original code.
        Returns a list of argument names.
        """
        tree = ast.parse(self.original_code)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for body_node in node.body:
                    if isinstance(body_node, ast.FunctionDef) and body_node.name == '__init__':
                        args = [arg.arg for arg in body_node.args.args]
                        return args
        return []

    def generate_argument_value(self, arg_name):
        """
        Generates a default value for a given argument based on its name.
        """
        # You can extend this function to generate more sophisticated values based on the argument name/type.
        if arg_name in ['self']:
            return None
        elif arg_name in ['id', 'count']:
            return random.randint(1, 10)  # Integer value for count/id
        elif arg_name in ['name', 'type']:
            return f"{arg_name}_default"  # String value
        elif arg_name in ['values']:
            return [random.randint(1, 10) for _ in range(3)]  # List of integers
        return None

    def mutate_pmd(self):
        """Applies Parent Member Variable Declaration (PMD) mutations."""
        print("Applying PMD mutations...")
        parent_child_map = self.find_parent_child_classes()
        original_code_lines = self.original_code.splitlines(keepends=True)

        for parent_class, child_classes in parent_child_map.items():
            for child_class in child_classes:
                tree = ast.parse(self.original_code)
                mutated_tree = copy.deepcopy(tree)
                mutated_code_lines = list(original_code_lines)

                for node in ast.walk(mutated_tree):
                    if isinstance(node, ast.AnnAssign) and isinstance(node.annotation, ast.Name) and node.annotation.id == parent_class:
                        # Found a member variable declaration with parent class type
                        lineno = node.lineno

                        # Create a new AnnAssign node for the child class type
                        constructor_args = self.get_constructor_arguments(child_class)
                        constructor_call_args = [self.generate_argument_value(arg) for arg in constructor_args]
                        if len(constructor_call_args) > 0:
                            constructor_call_args = constructor_call_args[:-1]
                            
                        constructor_call = ast.Call(
                            func=ast.Name(id=child_class, ctx=ast.Load()),  # Using child class as constructor
                            args=[ast.Constant(value=arg) for arg in constructor_call_args],  # Pass arguments to the constructor
                            keywords=[]
                        )
                        
                        new_node = ast.AnnAssign(
                            target=copy.deepcopy(node.target),
                            annotation=ast.Name(id=child_class, ctx=ast.Load()),
                            value=constructor_call,  # Use the constructor call for value
                            simple=node.simple
                        )
                        ast.fix_missing_locations(new_node)

                        # Insert the new declaration after the original one
                        new_line = astunparse.unparse(new_node).strip() + "\n"
                        mutated_code_lines.insert(lineno, new_line)

                        # Save mutated code
                        mutated_code = "".join(mutated_code_lines)
                        self.save_code(mutated_code, "PMD", [parent_class, child_class])

                self.restore_original()
                original_code_lines = self.original_code.splitlines(keepends=True)

        print("Finished PMD mutations.")

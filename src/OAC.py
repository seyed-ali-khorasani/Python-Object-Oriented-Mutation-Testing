import ast
import astunparse
import random


class OACMutation:
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
        """Saves the mutated code to a new file."""
        temp_code_file = self.code_file
        temp_code_file = temp_code_file.replace("src", "src\\mutants")
        filename = f"{temp_code_file.replace('.py', '')}_{mutation_type}_{'_'.join(mutation_details)}.py"
        with open(filename, 'w') as f:
            f.write(mutated_code)
        print(f"Saved mutated code to: {filename}")

    def restore_original(self):
        """Restores the original code and AST."""
        self.original_code = self._read_code()
        self.original_ast = self._parse_code(self.original_code)
        print("Original code restored.")

    def detect_overloadable_functions(self):
        """Detects functions with default arguments in all classes."""
        overloadable_functions = {}

        for node in ast.walk(self.original_ast):
            if isinstance(node, ast.ClassDef):
                for body_node in node.body:
                    if isinstance(body_node, ast.FunctionDef):
                        if body_node.args.defaults:  # Functions with default arguments
                            overloadable_functions[(node.name, body_node.name)] = body_node

        return overloadable_functions

    def mutate_oac(self):
        """Applies Overload Attribute Change (OAC) mutations."""
        print("Applying OAC mutations...")
        overloadable_functions = self.detect_overloadable_functions()

        if not overloadable_functions:
            print("No overloadable functions with default arguments found.")
            return

        for (class_name, func_name), func_def in overloadable_functions.items():
            min_args = len(func_def.args.args) - len(func_def.args.defaults)
            max_args = len(func_def.args.args)

            if min_args < 0:
                min_args = 0

            for num_args in range(min_args - 1, max_args ):
                mutated_tree = self._parse_code(self.original_code)
                for node in ast.walk(mutated_tree):
                    if isinstance(node, ast.Call):
                        if (
                            isinstance(node.func, ast.Attribute)
                            and node.func.attr == func_name
                        ):
                            # Change the number of arguments in the call
                            new_args = [
                                ast.Constant(value=random.randint(0, 100))
                                for _ in range(num_args)
                            ]
                            node.args = new_args

                mutated_code = self._to_code(mutated_tree)
                self.save_code(mutated_code, "OAC", [func_name, f"args_{num_args}"])

        self.restore_original()
import ast
import astunparse
import copy
import random
import itertools

class OMRMutation:
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
        tree = self._parse_code(self.original_code)
        functions_with_defaults = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for body_node in node.body:
                    if isinstance(body_node, ast.FunctionDef):
                        if body_node.args.defaults:  # Check if there are any default arguments
                            functions_with_defaults[(node.name, body_node.name)] = body_node
        return functions_with_defaults

    def _create_random_body(self, func_def):
        """Creates a random body for a function."""
        new_body = []
        for _ in range(random.randint(1, 3)):  # Generate between 1 to 3 statements
            if random.random() > 0.5:
                # Create a simple return statement with a random value
                new_body.append(ast.Return(value=ast.Constant(value=random.randint(0, 100), kind=None)))
            else:
                # Create a simple assignment statement
                new_body.append(ast.Assign(
                    targets=[ast.Name(id="temp", ctx=ast.Store())],
                    value=ast.Constant(value=random.randint(0, 100), kind=None)
                ))
        return new_body

    def mutate_omr(self):
        """Applies Overload Method Replacement (OMR) mutations by replacing the function body with random code."""
        print("Applying OMR mutations...")
        overloadable_functions = self.detect_overloadable_functions()
        if not overloadable_functions:
            print("No overloadable functions found.")
            return

        for (class_name, func_name), func_def in overloadable_functions.items():
            # Parse the code anew for each mutation
            mutated_tree = self._parse_code(self.original_code)

            # Locate the target class and function
            for class_node in ast.walk(mutated_tree):
                if isinstance(class_node, ast.ClassDef) and class_node.name == class_name:
                    for method_node in class_node.body:
                        if isinstance(method_node, ast.FunctionDef) and method_node.name == func_name:
                            # Replace the function body with random code
                            method_node.body = self._create_random_body(method_node)

            # Save the mutated version after processing all functions
            mutated_code = self._to_code(mutated_tree)
            self.save_code(mutated_code, "OMR", [class_name, func_name])

        self.restore_original()
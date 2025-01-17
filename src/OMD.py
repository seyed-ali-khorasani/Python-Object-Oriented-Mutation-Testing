import ast
import astunparse


class OMDMutation:
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

    def detect_methods_with_defaults(self):
        """Detects methods in classes that have arguments with default values."""
        tree = self._parse_code(self.original_code)
        methods_with_defaults = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):  # Only process classes
                for body_node in node.body:
                    if isinstance(body_node, ast.FunctionDef):  # Function definitions within the class
                        # Check if the function has arguments with default values
                        if body_node.args.defaults:
                            methods_with_defaults[(node.name, body_node.name)] = body_node
        return methods_with_defaults

    def mutate_omd(self):
        """Applies Overload Method Deletion (OMD) mutations for methods with default arguments."""
        print("Applying OMD mutations...")
        methods_with_defaults = self.detect_methods_with_defaults()
        if not methods_with_defaults:
            print("No methods with default arguments found.")
            return

        for (class_name, func_name), func_def in methods_with_defaults.items():
            # Parse the code anew for each mutation
            mutated_tree = self._parse_code(self.original_code)

            # Locate the target class and function
            for class_node in ast.walk(mutated_tree):
                if isinstance(class_node, ast.ClassDef) and class_node.name == class_name:
                    for method_node in list(class_node.body):
                        if isinstance(method_node, ast.FunctionDef) and method_node.name == func_name:
                            # Remove the method
                            class_node.body.remove(method_node)

                            # Save the mutated version
                            mutated_code = self._to_code(mutated_tree)
                            self.save_code(mutated_code, "OMD", [class_name, func_name])

        self.restore_original()

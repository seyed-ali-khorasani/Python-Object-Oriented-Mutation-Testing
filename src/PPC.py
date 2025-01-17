import ast
import astunparse
import copy


class PPCMutation:
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

    def find_parent_child_classes(self):
        """Finds parent-child class relationships in the code."""
        parent_child_map = {}
        for node in ast.walk(self.original_ast):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        parent_class = base.id
                        child_class = node.name
                        if parent_class not in parent_child_map:
                            parent_child_map[parent_class] = []
                        parent_child_map[parent_class].append(child_class)
        return parent_child_map

    def get_function_arguments(self, class_name):
        """Get the function arguments for a specific class."""
        functions = {}
        for node in ast.walk(self.original_ast):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for body_node in node.body:
                    if isinstance(body_node, ast.FunctionDef):
                        functions[body_node.name] = body_node.args
        return functions

    def mutate_ppc(self):
        """Applies Parent-to-Parent Cast (PPC) mutations."""
        print("Applying PPC mutations...")
        parent_child_map = self.find_parent_child_classes()

        # Iterate through all parent-child relationships
        for parent_class, child_classes in parent_child_map.items():
            if len(child_classes) < 2:
                # Skip if there are not enough child classes for mutation
                continue

            # Get the function arguments for each class
            class_functions = {child: self.get_function_arguments(child) for child in child_classes}

            # Iterate through the AST and replace instances of one child with another
            for node in ast.walk(copy.deepcopy(self.original_ast)):
                if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
                    if (
                        isinstance(node.value.func, ast.Name)
                        and node.value.func.id in child_classes
                    ):
                        original_child = node.value.func.id

                        for sibling_child in child_classes:
                            if sibling_child == original_child:
                                continue

                            # Apply mutation: Replace the child class
                            mutated_tree = copy.deepcopy(self.original_ast)

                            # Get the required number of arguments for the sibling class
                            sibling_functions = class_functions[sibling_child]
                            init_args = sibling_functions.get('__init__', None)
                            if init_args:
                                # Create the right number of arguments based on the sibling class's constructor
                                new_args = []
                                for idx in range(len(init_args.args) - 1):  # Skip 'self' argument
                                    new_args.append(ast.Constant(value=0))  # Default value (you can customize this)

                                # Find the node where the mutation happens (call to the original child class constructor)
                                for sub_node in ast.walk(mutated_tree):
                                    if (
                                        isinstance(sub_node, ast.Assign)
                                        and isinstance(sub_node.value, ast.Call)
                                        and isinstance(sub_node.value.func, ast.Name)
                                        and sub_node.value.func.id == original_child
                                    ):
                                        sub_node.value.func.id = sibling_child
                                        sub_node.value.args = new_args  # Assign new arguments

                            # Convert the mutated tree back to code
                            mutated_code = self._to_code(mutated_tree)
                            self.save_code(
                                mutated_code, "PPC", [original_child, sibling_child]
                            )

        print("Finished PPC mutations.")

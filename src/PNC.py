import ast
import astunparse
import itertools
import copy

i=0
class PNCMutation:
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


    def get_class_init_variables(self, class_name):
        """Helper function to get the variables initialized in a class's init method."""
        tree = ast.parse(self.original_code)
        init_vars = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for body_node in node.body:
                    if isinstance(body_node, ast.FunctionDef) and body_node.name == "init":
                        for stmt in body_node.body:
                            if isinstance(stmt, ast.Assign):
                                for target in stmt.targets:
                                    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
                                        init_vars.append(target.attr)
                        break  # Exit after finding init
        return init_vars

    def generate_argument_value(self, arg_name):
        if arg_name.lower() in ["name", "title", "label"]:
            return ast.Constant(value="example_" + arg_name, kind=None)
        elif arg_name.lower() in ["id", "count", "index"]:
            return ast.Constant(value=0, kind=None)
        else:
            return ast.Constant(value="placeholder_" + arg_name, kind=None)

    def mutate_pnc(self):
        """Applies Parent-to-New-Child (PNC) mutations."""
        print("Applying PNC mutations...")
        parent_child_map = self.find_parent_child_classes()
        original_code_lines = self.original_code.splitlines(keepends=True)
    
        for parent_class, child_classes in parent_child_map.items():
            for child_class in child_classes:
                tree = ast.parse(self.original_code)
                mutated_tree = copy.deepcopy(tree)  # Use deepcopy for independent mutations
    
                child_init_args = []
                for node in ast.walk(mutated_tree):
                    if isinstance(node, ast.ClassDef) and node.name == child_class:
                        for body_node in node.body:
                            if isinstance(body_node, ast.FunctionDef) and body_node.name == "__init__":
                                child_init_args = [arg.arg for arg in body_node.args.args if arg.arg != 'self']
                                break
                            
                for node in ast.walk(mutated_tree):
                    if isinstance(node, ast.Assign):
                        if isinstance(node.value, ast.Call):
                            if isinstance(node.value.func, ast.Name) and node.value.func.id == parent_class:
                                # Replace parent class with child class in the object creation
                                node.value.func.id = child_class
    
                                # Generate arguments for the child class constructor
                                new_args = [
                                    self.generate_argument_value(arg) for arg in child_init_args
                                ]
    
                                # Update the arguments in the AST
                                node.value.args = new_args
    
                                # Save mutated code
                                mutated_code = astunparse.unparse(mutated_tree)
                                self.save_code(mutated_code, "PNC", [parent_class, child_class])
    
                self.restore_original()
    
        print("Finished PNC mutations.")
    









    
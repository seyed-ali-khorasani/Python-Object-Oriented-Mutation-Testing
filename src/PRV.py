import ast
import astunparse
import itertools
import copy

i=0
class PRVMutation:
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

    def mutate_prv(self):
        """Applies Reference Assignment with Other Compatible Type (PRV) mutations."""
        print("Applying PRV mutations...")
        parent_child_map = self.find_parent_child_classes()
        original_code_lines = self.original_code.splitlines(keepends=True)

        for parent_class, child_classes in parent_child_map.items():
            for i in range(len(child_classes)):
                for j in range(i + 1, len(child_classes)):
                    # Consider both directions: child1 to child2 AND child2 to child1
                    for child1, child2 in [(child_classes[i], child_classes[j]), (child_classes[j], child_classes[i])]:
                        tree = ast.parse(self.original_code)
                        mutated_tree = copy.deepcopy(tree)
                        mutated_code_lines = list(original_code_lines)

                        for node in ast.walk(mutated_tree):
                            if isinstance(node, ast.Assign):
                                # Check if the right-hand side is a variable (not a direct object creation)
                                if isinstance(node.value, ast.Name):
                                    # Check if the left-hand side has the parent class type
                                    for target in node.targets:
                                        if isinstance(target, ast.Name):
                                            # Find the declaration of the right-hand side variable
                                            for assign_node in ast.walk(mutated_tree):
                                                if isinstance(assign_node, ast.Assign):
                                                    for target2 in assign_node.targets:
                                                        if isinstance(target2, ast.Name) and target2.id == node.value.id:
                                                            # Check if this assignment is creating an object of child1 or assigning a variable of type child1
                                                            if isinstance(assign_node.value, ast.Call) and isinstance(assign_node.value.func, ast.Name) and assign_node.value.func.id == child1 or \
                                                               (isinstance(assign_node.value, ast.Name) and assign_node.value.id in [var_decl.targets[0].id for var_decl in ast.walk(mutated_tree) if isinstance(var_decl, ast.Assign) and isinstance(var_decl.value, ast.Call) and isinstance(var_decl.value.func, ast.Name) and var_decl.value.func.id == child1]):
                                                                # Find declaration of the variable being assigned (the left-hand side)
                                                                for var_decl in ast.walk(mutated_tree):
                                                                    if isinstance(var_decl, (ast.AnnAssign, ast.Assign)):
                                                                        decl_targets = [var_decl.target] if isinstance(var_decl, ast.AnnAssign) else var_decl.targets
                                                                        for decl_target in decl_targets:
                                                                            if isinstance(decl_target, ast.Name) and decl_target.id == target.id:
                                                                                # Check if the declared type is the parent class or if it's an assignment creating a parent class object
                                                                                if (isinstance(var_decl, ast.AnnAssign) and isinstance(var_decl.annotation, ast.Name) and var_decl.annotation.id == parent_class) or \
                                                                                   (isinstance(var_decl, ast.Assign) and isinstance(var_decl.value, ast.Call) and isinstance(var_decl.value.func, ast.Name) and var_decl.value.func.id == parent_class):
                                                                                    # Iterate through all assignments to find instances of child2 or variables of type child2
                                                                                    for child2_decl in ast.walk(mutated_tree):
                                                                                        if isinstance(child2_decl, ast.Assign):
                                                                                            for child2_target in child2_decl.targets:
                                                                                                if isinstance(child2_target, ast.Name):
                                                                                                    if isinstance(child2_decl.value, ast.Call) and isinstance(child2_decl.value.func, ast.Name) and child2_decl.value.func.id == child2 or \
                                                                                                       (isinstance(child2_decl.value, ast.Name) and child2_decl.value.id in [var_decl.targets[0].id for var_decl in ast.walk(mutated_tree) if isinstance(var_decl, ast.Assign) and isinstance(var_decl.value, ast.Call) and isinstance(var_decl.value.func, ast.Name) and var_decl.value.func.id == child2]):
                                                                                                        # Replace the right-hand side with the variable of type child2
                                                                                                        node.value.id = child2_target.id

                                                                                                        # Save mutated code
                                                                                                        mutated_code = astunparse.unparse(mutated_tree)
                                                                                                        self.save_code(mutated_code, "PRV", [parent_class, child1, child2])
                                                                                                        # Restore for next mutation within the same child pair
                                                                                                        mutated_tree = copy.deepcopy(tree)
                                                                                                        mutated_code_lines = list(original_code_lines)
                                                                                                        # Re-parse the mutated tree to continue searching for other child1 instances
                                                                                                        tree = ast.parse(mutated_code)
                                                                                                        mutated_tree = copy.deepcopy(tree)
                                                                                                        # Break out of the child2 loop to avoid duplicate mutations
                                                                                                        break
                                                                                            else:
                                                                                                continue  # Only consider assignments where child2 is created or assigned
                                                                                            break  # Found the assignment for child2, no need to check other targets
                                                                                        else:
                                                                                            continue  # Only consider assignment nodes
                                                                                        break  # Found child2 declaration, move to the next mutation
                        self.restore_original()
                        original_code_lines = self.original_code.splitlines(keepends=True)

        print("Finished PRV mutations.")

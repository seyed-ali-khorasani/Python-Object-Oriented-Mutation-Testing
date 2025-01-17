import ast
import astunparse
import itertools
import copy

i=0
class ACMMutation:
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
        if original_code_normalized != mutated_code_normalized:
            
                with open(filename, 'w') as f:
                    f.write(mutated_code)
                print(f"Saved mutated code to: {filename}")
        else:
                    print(f"Skipped saving {filename} (no changes from original)")

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

    def mutate_amc(self):
        """Applies Access Modifier Change (AMC) mutations."""
        print("Applying AMC mutations...")
        tree = self._parse_code(self.original_code)
        original_code_lines = self.original_code.splitlines(keepends=True)
        detected_variables = self.detect_access_modifiers(self.original_code)
        possible_modifiers = {'public': '', 'protected': '_', 'private': '__'}
        for var_info in detected_variables:
            variable_name = var_info['name']
            current_modifier_type = var_info['modifier']
            for new_modifier_type, new_modifier_prefix in possible_modifiers.items():
                if new_modifier_type != current_modifier_type:
                    mutated_tree = self._parse_code(self.original_code)
                    mutated_code_lines = list(original_code_lines)
                    original_prefix = ''
                    if variable_name.startswith('__'):
                        original_prefix = '__'
                    elif variable_name.startswith('_'):
                        original_prefix = '_'
                    original_base_name = variable_name.lstrip('_')
                    new_variable_name = new_modifier_prefix + original_base_name
                    for mutate_node in ast.walk(mutated_tree):
                        if isinstance(mutate_node, (ast.Assign, ast.AnnAssign)):
                            targets = [mutate_node.target] if isinstance(mutate_node, ast.AnnAssign) else mutate_node.targets
                            for target in targets:
                                if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self' and target.attr == variable_name:
                                    lineno = mutate_node.lineno - 1
                                    print(mutated_code_lines[lineno])
                                    original_line = mutated_code_lines[lineno]
                                    mutated_line = original_line.replace(f"self.{variable_name}", f"self.{new_variable_name}")
                                    mutated_code_lines[lineno] = mutated_line
                                    mutated_code = "".join(mutated_code_lines)
                                    self.save_code(mutated_code, "AMC", [variable_name, current_modifier_type, new_modifier_type])
        self.restore_original()
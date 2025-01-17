import ast
import astunparse
import itertools
import copy
import random

i=0
class ISDMutation:
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

    

    def mutate_isd(self):
        """Applies Inheritance Super Delete (ISD) mutations."""
        print("Applying ISD mutations...")
        original_code_lines = self.original_code.splitlines(keepends=True)
    
        tree = ast.parse(self.original_code)
        for node in ast.walk(tree):
            # Identify super() calls that are followed by a method other than '__init__'
            if (
                isinstance(node, ast.Call) 
                and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Call)
                and isinstance(node.func.value.func, ast.Name)
                and node.func.value.func.id == 'super'
            ):
                # Check if the method being called is NOT '__init__'
                if node.func.attr != '__init__':
                    random_number = random.randint(1, 100)  # Generate a random number
                    start_lineno = node.lineno - 1
                    start_col_offset = node.col_offset
    
                    # Convert the AST node for the `super.method()` call to a string
                    original_super_call = astunparse.unparse(node).strip()
    
                    # Replace only the `super.method()` part with a random number in the corresponding line
                    mutated_line = original_code_lines[start_lineno]
                    mutated_line = (
                        mutated_line[:start_col_offset] +  # Keep everything before `super.method()`
                        str(random_number) +  # Replace `super.method()` with the random number
                        mutated_line[start_col_offset + len(original_super_call):]  # Keep everything after
                    )
    
                    # Update the mutated line in the code
                    mutated_code_lines = list(original_code_lines)
                    mutated_code_lines[start_lineno] = mutated_line
    
                    # Generate mutated code
                    mutated_code = "".join(mutated_code_lines)
                    self.save_code(mutated_code, "ISD", [str(start_lineno)])
    
                    # Restore original code to avoid overlapping mutations
                    self.restore_original()
                    original_code_lines = self.original_code.splitlines(keepends=True)
    
        print("Finished ISD mutations.")

    

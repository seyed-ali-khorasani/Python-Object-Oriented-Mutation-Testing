import ast
import astunparse
import itertools
import copy

i=0
class IPCMutation:
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


    def mutate_ipc(self):
        """Applies explicit parent constructor deletion mutation by removing super().__init__() calls."""
        print("Applying explicit parent constructor deletion mutation...")
        original_code_lines = self.original_code.splitlines(keepends=True)

        tree = ast.parse(self.original_code)
        
        super_init_calls_info = []
        for node in ast.walk(tree):
            # Look for super().__init__() calls
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and \
               isinstance(node.value.func, ast.Attribute) and \
               isinstance(node.value.func.value, ast.Call) and \
               isinstance(node.value.func.value.func, ast.Name) and \
               node.value.func.value.func.id == "super" and \
               node.value.func.attr == "__init__":
                super_init_calls_info.append(node.lineno)
            
        for lineno in super_init_calls_info:
            # Get the line number of the super call
            lineno = lineno - 1

            # Remove the line with the super() call from the code
            mutated_code_lines = list(original_code_lines)
            mutated_code_lines.pop(lineno)  # Remove the line entirely

            mutated_code = "".join(mutated_code_lines)
            self.save_code(mutated_code, "ExplicitParentConstructorDeletion", [str(lineno)])
            self.restore_original()  # Restore original code for further mutation

            original_code_lines = self.original_code.splitlines(keepends=True)  # Restore original code lines


        print("Finished explicit parent constructor deletion mutation.")
import os
import re

subprograms_called = set()
BASE_PATH = "nc_programs"
DEFAULT_CALL = "BP9725(0,,10,,,-20,,,22,,,0,,,-1)"
PARAM_FILE = "parameters.txt"

# Parse the call like BP9725(0,,10,,,-20...)
def parse_call(call_str):
    match = re.match(r"(BP\d+)\((.*)\)", call_str)
    if not match:
        print("❌ Invalid format. Use: BP9725(0,,10,,,-20,,,22,,,0,,,-1)")
        return None, []
    func = match.group(1)
    args = [arg.strip() if arg.strip() else None for arg in match.group(2).split(',')]
    return func, args

# Read file contents
def read_file(name):
    path = os.path.join(BASE_PATH, f"{name}.nc")
    if os.path.isfile(path):
        with open(path, 'r') as f:
            print(f"📂 Loaded: {path}")
            return f.readlines()
    return None

# Parameter persistence (optional memory)
def load_parameters():
    parameters = {}
    if os.path.exists(PARAM_FILE):
        with open(PARAM_FILE, 'r') as f:
            for line in f:
                key, value = line.strip().split('=')
                parameters[key] = value
    return parameters

def save_parameters(parameters):
    with open(PARAM_FILE, 'w') as f:
        for key, value in parameters.items():
            f.write(f"{key}={value}\n")

# Detect G-code movements
def extract_movements(code_line):
    movements = re.findall(r'G[0-9]+', code_line)
    descriptions = {
        'G0': 'Rapid movement (non-cutting)',
        'G1': 'Linear movement',
        'G2': 'Circular CW',
        'G3': 'Circular CCW',
        'G4': 'Dwell (pause)'
    }
    return [(m, descriptions.get(m, "Unknown movement")) for m in movements]

# Core simulation logic
def simulate_execution(func, args, parameters_loaded={}):
    variables = bind_arguments(args, parameters_loaded)
    print(f"\n🔧 Starting step-by-step execution of {func} with arguments:")
    print(f"  Bound variables: {variables}")

    content = read_file(func)
    if not content:
        print("❌ Could not read subprogram.")
        return

    line_idx = 0
    while line_idx < len(content):
        line = content[line_idx].strip()
        print(f"\n🔍 Line {line_idx + 1}: {line}")
        line_idx += 1

        # Conditional jump
        if "IF" in line:
            condition = extract_condition(line)
            if condition:
                result = evaluate_condition(condition, variables)
                print(f"  Condition: {line.strip()} -> Evaluated: {result}")

                # Handle conditional jumps
                if "GOTOF" in line:
                    destination = extract_goto_destination(line)
                    if not result:
                        print(f"  Condition failed, jumping to {destination}")
                        line_idx = find_label_destination(content, destination)
                        continue
                elif "GOTO" in line:
                    destination = extract_goto_destination(line)
                    if result:
                        print(f"  Condition true, jumping to {destination}")
                        line_idx = find_label_destination(content, destination)
                        continue

        # Movement command
        elif "G" in line:
            for mov, desc in extract_movements(line):
                print(f"  Executing: {mov} - {desc}")

        # Assignment
        elif "=" in line:
            variables = update_variables(line, variables)

        # Subprogram call
        elif re.search(r"BP\d+\(", line):
            called = re.findall(r"(BP\d+)", line)
            for sub in called:
                if sub not in subprograms_called:
                    print(f"  Calling subprogram: {sub}")
                    subprograms_called.add(sub)
                    simulate_execution(sub, args, variables)
                else:
                    print(f"  Subprogram {sub} already called. Skipping to prevent infinite recursion.")

        # End of program
        if "M30" in line or "M17" in line:
            print("  Program end reached.")
            break


# Extracts the condition from IF(...)
def extract_condition(line):
    match = re.search(r"IF\((.*?)\)", line)
    return match.group(1) if match else None

# Evaluates conditions like ($P_SUBPAR[1]<>FALSE)
def evaluate_condition(condition, variables):
    condition = condition.replace("<>", "!=")

    # Substituir sintaxe de array, como $P_SUBPAR[1]
    def replace_array(match):
        var_name = match.group(1)
        index = match.group(2)
        index_val = variables.get(index, index)
        return variables.get(f"{var_name}[{index_val}]", "False")

    condition = re.sub(r"(\$\w+)\[(.*?)\]", replace_array, condition)

    # Substituir TRUE/FALSE por Python
    condition = condition.replace("TRUE", "True").replace("FALSE", "False")

    # Substituir variáveis com regex: só palavras inteiras
    for var, val in sorted(variables.items(), key=lambda x: -len(x[0])):
        pattern = r'\b{}\b'.format(re.escape(var))
        condition = re.sub(pattern, val, condition)

    try:
        result = eval(condition)
        print(f"  🧠 Evaluating: {condition} = {result}")
        return bool(result)
    except Exception as e:
        print(f"❌ Evaluation error: {condition} -> {e}")
        return False


# Extract destination label from GOTOF/GOTO
def extract_goto_destination(line):
    match = re.search(r"GOTOF? (LBL\d+)", line)
    return match.group(1) if match else None

# Finds the line index of the label like LBL201:
def find_label_destination(content, label):
    for idx, line in enumerate(content):
        if re.match(rf"{label}\s*:", line.strip()):
            return idx
    print(f"⚠️ Label {label} not found.")
    return len(content)

# Process assignment like VAR = EXPR
def update_variables(line, variables):
    match = re.match(r"(\w+)\s*=\s*(.*)", line)
    if match:
        var = match.group(1)
        val = evaluate_expression(match.group(2).strip(), variables)
        variables[var] = val
    return variables

# Evaluate expressions (supports ABS, ROUND)
def evaluate_expression(expr, variables):
    expr = expr.replace("<>", "!=").replace("ABS", "abs").replace("ROUND", "round")
    for var, val in variables.items():
        expr = expr.replace(var, val)
    try:
        return str(eval(expr))
    except Exception as e:
        print(f"❌ Error in expression evaluation: {e}")
        return expr

# Assign arguments like BP_1, BP_2 and also $P_SUBPAR[n]
def bind_arguments(args, loaded_params):
    vars = loaded_params.copy()
    for i, arg in enumerate(args):
        name = f"BP_{i + 1}"
        vars[name] = arg if arg is not None else request_input(name)
        vars[f"$P_SUBPAR[{i + 1}]"] = "True" if arg is not None else "False"
    return vars

# Prompt user for variable if not given
def request_input(name):
    params = load_parameters()
    if name not in params:
        print(f"Parameter {name} not found.")
        value = input(f"Enter value for {name} (default = 9999): ").strip()
        if value == "":
            value = "9999"
        params[name] = value
        save_parameters(params)  # Isso garante que o parâmetro será salvo corretamente
    return params[name]


# MAIN
if __name__ == "__main__":
    print(f"🔹 Enter function call like: {DEFAULT_CALL}")
    user_input = input("> ").strip()
    if not user_input:
        user_input = DEFAULT_CALL

    func_name, arguments = parse_call(user_input)
    if func_name:
        print(f"➡️ Function: {func_name}")
        print(f"➡️ Arguments: {arguments}")
        loaded_params = load_parameters()
        simulate_execution(func_name, arguments, loaded_params)

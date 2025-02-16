import ast

def extract_model_details(train_file):
    # Open and parse the train.py file
    with open(train_file, "r") as f:
        script_content = f.read()

    # Search for model creation patterns (for example, PyTorch or TensorFlow models)
    model_info = {}
    hyperparameters = {}

    if "torch" in script_content:
        # Assuming PyTorch model building (can be extended for other frameworks)
        model_info = {
            "framework": "PyTorch",
            "architecture": "CNN",  # We can dynamically extract layers too if needed
        }
        hyperparameters = extract_hyperparameters(script_content)
    elif "tensorflow" in script_content:
        model_info = {
            "framework": "TensorFlow",
            "architecture": "Sequential",  # Placeholder for simplicity
        }
        hyperparameters = extract_hyperparameters(script_content)

    return model_info, hyperparameters


def extract_hyperparameters(script_content):
    # Extract hyperparameters like learning rate, batch size, etc. from the script content
    hyperparameters = {}
    if "learning_rate" in script_content:
        hyperparameters["learning_rate"] = extract_value_from_script(script_content, "learning_rate")
    if "batch_size" in script_content:
        hyperparameters["batch_size"] = extract_value_from_script(script_content, "batch_size")
    if "epochs" in script_content:
        hyperparameters["epochs"] = extract_value_from_script(script_content, "epochs")

    return hyperparameters


def extract_value_from_script(script_content, variable_name):
    # Extract a variable's value from the script content using simple parsing
    try:
        tree = ast.parse(script_content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == variable_name:
                        return eval(compile(ast.Expression(node.value), filename="<ast>", mode="eval"))
    except Exception as e:
        print(f"Error extracting {variable_name}: {e}")
    return None
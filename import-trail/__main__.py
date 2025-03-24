import ast
import os
import sys

def resolve_local_module_path(module, project_root):
    parts = module.split('.')
    mod_path = os.path.join(project_root, *parts) + '.py'
    if os.path.isfile(mod_path):
        return os.path.abspath(mod_path)
    init_path = os.path.join(project_root, *parts, '__init__.py')
    if os.path.isfile(init_path):
        return os.path.abspath(init_path)
    return None

def get_module_name(filepath, project_root):
    abs_path = os.path.abspath(filepath)
    rel_path = os.path.relpath(abs_path, project_root)
    parts = rel_path.split(os.sep)
    if parts[-1] == '__init__.py':
        parts = parts[:-1]
    else:
        parts[-1] = os.path.splitext(parts[-1])[0]
    return ".".join(parts)

def get_imports_from_file(filepath, current_module=None, project_root=None):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        tree = ast.parse(content, filename=filepath)
    except Exception:
        return set()
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level > 0:
                if current_module:
                    base_parts = current_module.split('.')[:-node.level]
                    if node.module:
                        abs_mod = ".".join(base_parts + [node.module])
                        imports.add(abs_mod)
                    else:
                        for alias in node.names:
                            abs_mod = ".".join(base_parts + [alias.name])
                            imports.add(abs_mod)
            else:
                if node.module:
                    # add the base module
                    imports.add(node.module)
                    # also consider candidate submodules if they exist (e.g. "from mod.name.func import x" might refer to "mod.name.func.x")
                    if project_root:
                        for alias in node.names:
                            candidate = node.module + '.' + alias.name
                            if resolve_local_module_path(candidate, project_root):
                                imports.add(candidate)
    # Handle dynamic imports
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if (isinstance(node.func, ast.Attribute) and 
                node.func.attr == 'import_module' and 
                isinstance(node.func.value, ast.Name) and 
                node.func.value.id == 'importlib'):
                if node.args:
                    mod_arg = node.args[0]
                    mod_str = None
                    if isinstance(mod_arg, ast.Str):
                        mod_str = mod_arg.s
                    elif isinstance(mod_arg, ast.Constant) and isinstance(mod_arg.value, str):
                        mod_str = mod_arg.value
                    if mod_str:
                        imports.add(mod_str)
            elif isinstance(node.func, ast.Name) and node.func.id == '__import__':
                if node.args:
                    mod_arg = node.args[0]
                    mod_str = None
                    if isinstance(mod_arg, ast.Str):
                        mod_str = mod_arg.s
                    elif isinstance(mod_arg, ast.Constant) and isinstance(mod_arg.value, str):
                        mod_str = mod_arg.value
                    if mod_str:
                        imports.add(mod_str)
    return imports

def collect_import_routes(filepath, project_root, current_chain=None, collected=None):
    if current_chain is None:
        current_chain = []
    if collected is None:
        collected = {}
    abs_path = os.path.abspath(filepath)
    new_chain = current_chain + [abs_path]
    if abs_path not in collected:
        collected[abs_path] = []
    collected[abs_path].append(new_chain)
    current_module = get_module_name(abs_path, project_root)
    imports = get_imports_from_file(abs_path, current_module, project_root)
    for imp in imports:
        mod_path = resolve_local_module_path(imp, project_root)
        if mod_path and mod_path not in new_chain:  # avoid cycles
            collect_import_routes(mod_path, project_root, new_chain, collected)
    return collected

def print_routes(collected, project_root):
    for abs_path, routes in collected.items():
        mod_name = get_module_name(abs_path, project_root)
        for route in routes:
            mod_route = [get_module_name(p, project_root) for p in route]
            print(" -> ".join(mod_route))

def main():
    if len(sys.argv) < 2:
        print("usage: python import_routes.py <entry_file> [project_root]")
        sys.exit(1)
    entry_file = sys.argv[1]
    project_root = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.dirname(entry_file)
    routes = collect_import_routes(entry_file, project_root)
    print_routes(routes, project_root)

if __name__ == "__main__":
    main()

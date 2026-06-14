# parser_worker.py
import os
import tree_sitter_python as tspython
from tree_sitter import Language, Parser
import json

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

def run_advanced_mesh_scan(directory_path: str):
    system_map = {}

    # Crawls through whatever directory we pass it
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".py") and file != "parser_worker.py":
                full_path = os.path.join(root, file)
                relative_key = os.path.relpath(full_path, directory_path)

                with open(full_path, "rb") as f:
                    source_code = f.read()

                syntax_tree = parser.parse(source_code)
                root_node = syntax_tree.root_node

                file_telemetry = {
                    "exposed_api_routes": [],
                    "outbound_network_calls": [],
                    "database_dependencies": []
                }

                def traverse_nodes(node):
                    if node.type == "decorator":
                        text = source_code[node.start_byte:node.end_byte].decode("utf-8", errors="ignore")
                        if "app.post" in text or "app.get" in text:
                            file_telemetry["exposed_api_routes"].append(text)

                    if node.type == "string":
                        val = source_code[node.start_byte:node.end_byte].decode("utf-8", errors="ignore").strip("'\"")
                        if "postgresql://" in val or "mongodb://" in val:
                            file_telemetry["database_dependencies"].append({
                                "connection_string": val,
                                "target": val.split("/")[-1]
                            })
                        if "http://" in val and ".internal" in val:
                            file_telemetry["outbound_network_calls"].append({
                                "destination_api": val,
                                "target_host": val.split("//")[-1].split(":")[0]
                            })

                    for child in node.children:
                        traverse_nodes(child)

                traverse_nodes(root_node)
                if any(file_telemetry.values()):
                    system_map[relative_key] = file_telemetry

    return system_map

if __name__ == "__main__":
    print("Running advanced cross-service mesh AST parsing scanner...\n")
    # "." tells it to scan the current directory it is sitting in!
    mesh_results = run_advanced_mesh_scan(".")
    print(json.dumps(mesh_results, indent=2))
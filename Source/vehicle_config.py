import json
import os

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the JSON file
json_path = os.path.join(script_dir, 'vehicle_data.json')

try:
    with open(json_path, 'r') as f:
        vehicle_dict = json.load(f)
except FileNotFoundError:
    # Try to load the example file if the main one is not found
    example_path = os.path.join(script_dir, 'vehicle_data.example.json')
    try:
        with open(example_path, 'r') as f:
            print(f"Warning: '{os.path.basename(json_path)}' not found. Loading example data from '{os.path.basename(example_path)}'.")
            vehicle_dict = json.load(f)
    except FileNotFoundError:
        print(f"Error: Neither '{os.path.basename(json_path)}' nor '{os.path.basename(example_path)}' were found.")
        vehicle_dict = {}
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from the file {json_path}.")
    print("Please check the file for syntax errors.")
    vehicle_dict = {}

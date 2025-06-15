import json
import os
import glob
import sys

# --- CONFIGURATION ---
HTML_TEMPLATE_FILE = 'template.html'
INPUT_DIR = 'tasks_for_html'  # Directory with your JSON task files
OUTPUT_DIR = 'deploy'         # Where the generated 'deploy_*.html' files will be saved
# --- END CONFIGURATION ---


def main():
    """
    Main function to find all task files, load the template,
    and generate an HTML file for each task.
    """
    print("--- Starting Batch DRAFT HTML Generation ---")
    
    # 1. Create the output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: '{OUTPUT_DIR}/'")

    # 2. Load the template file once
    try:
        with open(HTML_TEMPLATE_FILE, 'r', encoding='utf-8') as f:
            template_html = f.read()
    except FileNotFoundError:
        print(f"Error: HTML template file not found: {HTML_TEMPLATE_FILE}")
        return

    # 3. Find all .json files in the input directory
    task_files = glob.glob(os.path.join(INPUT_DIR, '*.json'))
    
    if not task_files:
        print(f"⚠️  No JSON task files found in the '{INPUT_DIR}/' directory. Nothing to do.")
        return

    print(f"Found {len(task_files)} task files to process...")
    
    # 4. Loop through each task file and generate its HTML
    for task_file in task_files:
        # Load the specific task data
        with open(task_file, 'r', encoding='utf-8') as f:
            task_data = json.load(f)

        # Inject only the task data. The URL placeholder remains.
        final_html = template_html.replace(
            "'PASTE_TASK_DATA_HERE'",
            json.dumps(task_data, indent=4)
        )
        
        # Create and write the output file
        base_name = os.path.splitext(os.path.basename(task_file))[0]
        output_filename = f"deploy_{base_name}.html"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_html)
            
        print(f"✅ Generated draft: {output_path}")
        
    print("\n--- Draft generation complete. ---")
    print(f"Next step: Upload the '{OUTPUT_DIR}/' directory to GitHub.")


if __name__ == '__main__':
    main()
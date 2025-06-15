import requests
import json
import os
import time
import glob
import subprocess
import uuid 

# ==============================================================================
# --- CONFIGURATION ---
# ==============================================================================

PROLIFIC_API_TOKEN = "0Ip3_GziE4JEUQ-mH30hNO5GYF2CL0JbibXEfJb5v850TI5-QwjKLp1daE22zbPDeXTUGu3woDT6UdZj98Zo4FofIdy0RATO7DYerdZ-2eQGtzmNzrkoWExa"
PROLIFIC_PROJECT_ID = "6847b2cf53ca2e7177c6c4fc"
PROLIFIC_PLACEHOLDER_URL = "https://kexinb426.github.io/docsimp_eval_study/"

# The FINAL base URL for your studies. Make sure it ends with a forward slash /
FINAL_HTML_BASE_URL = "https://kexinb426.github.io/docsimp_eval_study/deploy/"

HTML_FILES_DIR = 'deploy' 
TASKS_DIR = 'tasks_for_html'
GIT_COMMIT_MESSAGE = "Automated creation and update of Prolific studies"


# 6. General settings for all studies.
STUDY_SETTINGS = {
    "name": "Document Simplification Evaluation (Study {study_number})",
    "internal_name": "{doc_name}",
    "description": "In this study, you will read a short document and several simplified versions of it, then answer questions about their quality.",
    "project": PROLIFIC_PROJECT_ID,
    "external_study_url": "{study_url}", # This gets filled in automatically
    "completion_codes": [
        {
            "code": "{completion_code}", # This is where your unique code goes
            "code_type": "COMPLETED",
            "actions": [
                {
                    "action": "AUTOMATICALLY_APPROVE"
                }
            ]
        }
    ],
    "reward": 150,
    "currency": "GBP",
    "total_available_places": 3,
    "estimated_completion_time": 10,
    "device_compatibility": ["desktop"],
    "eligibility_requirements": [],
    "is_custom_screening": False, # Required by Prolific API for study creation
    "maximum_allowed_time": 40, # Set a reasonable maximum, e.g., 15 minutes (or 1.5x estimated)
    "prolific_id_option": "url_parameters", # Common requirement for external studies
    "peripheral_requirements": [] # Often required, even if empty
}
# ==============================================================================
# --- SCRIPT LOGIC (No need to edit below) ---
# ==============================================================================

def create_prolific_study(doc_name, completion_code, study_number): # Add study_number here
    """Creates a draft study on Prolific and returns its ID."""
    print(f"\n-> Creating Prolific study for '{doc_name}'...")

    payload = STUDY_SETTINGS.copy()
    pretty_name = doc_name.replace('_', ' ').title()

    payload["name"] = payload["name"].format(study_number=study_number)
    payload["internal_name"] = payload["internal_name"].format(doc_name=pretty_name)
    payload["external_study_url"] = (
        f"{FINAL_HTML_BASE_URL}deploy_{doc_name}.html?"
        "PROLIFIC_PID={{%PROLIFIC_PID%}}"
        "&STUDY_ID={{%STUDY_ID%}}"
        "&SESSION_ID={{%SESSION_ID%}}"
    )

    if payload["completion_codes"] and len(payload["completion_codes"]) > 0:
        payload["completion_codes"][0]["code"] = completion_code

    headers = {"Authorization": f"Token {PROLIFIC_API_TOKEN}"}
    response = requests.post("https://api.prolific.com/api/v1/studies/", headers=headers, json=payload)

    if response.status_code == 201:
        study = response.json()
        print(f"   ✅ SUCCESS: Created draft study '{pretty_name}'.")
        return study['id']
    else:
        print(f"   ❌ FAILED to create study '{doc_name}'.")
        print(f"      Status Code: {response.status_code}")
        print(f"      Error Response: {response.text}")
        return None

def update_html_file(doc_name, completion_code):
    """Replaces placeholder in an HTML file with the real completion code."""
    file_path = os.path.join(HTML_FILES_DIR, f"deploy_{doc_name}.html")
    completion_url = f"https://app.prolific.com/submissions/complete?cc={completion_code}"
    try:
        with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
        new_content = content.replace("'PASTE_PROLIFIC_URL_HERE'", json.dumps(completion_url))
        with open(file_path, 'w', encoding='utf-8') as f: f.write(new_content)
        print(f"-> Updated local HTML for '{doc_name}' with code {completion_code}.")
        return True
    except FileNotFoundError:
        print(f"   ❌ FAILED to update HTML. File not found: {file_path}")
        return False

def main():
    if "PASTE_YOUR" in PROLIFIC_API_TOKEN or "PASTE_YOUR" in PROLIFIC_PROJECT_ID:
        print("🚨 ERROR: Please fill in your API Token and Project ID.")
        return

    doc_names = [os.path.splitext(os.path.basename(f))[0] for f in glob.glob(os.path.join(TASKS_DIR, '*.json'))]
    if not doc_names:
        print(f"⚠️  No JSON task files found in '{TASKS_DIR}/'.")
        return
        
    print(f"Found {len(doc_names)} documents to process.")
    
    # 1. Generate unique codes and update local HTML files first.
    print("\n--- PART 1: Generating Codes & Updating Local HTML Files ---")
    study_codes = {}
    for i, doc_name in enumerate(doc_names): # Add enumerate to get an index
        study_number = i + 1 # Start study numbers from 1
        unique_code = f"C{str(uuid.uuid4()).upper()[:8]}"
        study_codes[doc_name] = unique_code
        update_html_file(doc_name, unique_code)
    
    # 2. Pause and instruct the user to upload the files to get live URLs.
    print("\n--- PART 2: ACTION REQUIRED: Upload to GitHub ---")
    print("The script has updated your local HTML files with unique completion codes.")
    print("Now, you must upload them to GitHub to make their links live.")
    print("Please run these commands in your terminal, from this project folder:\n")
    print(f"  git add {HTML_FILES_DIR}/")
    print(f'  git commit -m "Generate study files for batch: {", ".join(doc_names)}"')
    print( "  git push\n")
    input("After you have successfully pushed the files to GitHub, press Enter here to continue...")

    # 3. Create the studies on Prolific using the now-live URLs.
    print("\n--- PART 3: Creating Studies on Prolific ---")
    print("Waiting 10 seconds for GitHub Pages to update...")
    time.sleep(10)
    for i, doc_name in enumerate(doc_names): # Use enumerate here too
        study_number = i + 1 # Pass the study number
        completion_code = study_codes[doc_name]
        # Pass study_number to the create_prolific_study function
        create_prolific_study(doc_name, completion_code, study_number)
        time.sleep(1)

    print("\n\n🎉🎉🎉 SCRIPT COMPLETE! 🎉🎉🎉")
    print("Your draft studies are in your project on Prolific, ready to be reviewed and published.")

if __name__ == '__main__':
    main()
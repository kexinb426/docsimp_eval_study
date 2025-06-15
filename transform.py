import json
import os
import re

# --- CONFIGURATION ---
# This configuration remains the same. You can define your standard
# overall quality questions that will be added to every simplification.
STANDARD_OVERALL_QUESTIONS = [
    {
        "key": "fluency",
        "label": "Fluency: How grammatically correct and well-formed are the sentences?",
        "options": [
            { "label": "1 - Very Poor", "description": "Many sentences are ungrammatical or nonsensical." },
            { "label": "2 - Poor",      "description": "Some sentences are awkward or contain errors." },
            { "label": "3 - Acceptable","description": "Mostly fluent, with a few minor awkward phrases." },
            { "label": "4 - Good",      "description": "The text reads naturally with no errors." },
            { "label": "5 - Excellent", "description": "The language is exceptionally well-formed and articulate." }
        ]
    },
    {
        "key": "clarity",
        "label": "Clarity: As a stand-alone text, how clear and easy is it to understand the main points?",
        "options": [
            { "label": "1 - Very Unclear", "description": "The text is confusing and the main points are hard to grasp." },
            { "label": "2 - Unclear",      "description": "Some parts of the text are confusing or ambiguous." },
            { "label": "3 - Acceptable",   "description": "The text is generally understandable, but could be clearer." },
            { "label": "4 - Clear",        "description": "The text is easy to understand." },
            { "label": "5 - Very Clear",   "description": "The text is exceptionally easy to follow and unambiguous." }
        ]
    },
    {
        "key": "conciseness",
        "label": "Conciseness: Is the text succinct or does it use unnecessary words?",
         "options": [
            { "label": "1 - Very Wordy", "description": "The text is highly repetitive or uses many unnecessary words." },
            { "label": "2 - Wordy",      "description": "The text is somewhat repetitive or wordy." },
            { "label": "3 - Acceptable", "description": "The text is mostly concise but could be tightened." },
            { "label": "4 - Concise",    "description": "The text is direct and to the point." },
            { "label": "5 - Very Concise","description": "Every word serves a clear purpose." }
        ]
    },
    {
        "key": "style",
        "label": "Style: How appropriate and natural is the writing style?",
        "options": [
            { "label": "1 - Very Unnatural", "description": "The style feels robotic, 'dumbed down,' or childish." },
            { "label": "2 - Slightly Unnatural", "description": "The style is a bit simplistic or awkward in places." },
            { "label": "3 - Acceptable", "description": "The style is functional but not particularly engaging." },
            { "label": "4 - Good", "description": "The style is clear, simple, and appropriate for a general audience." },
            { "label": "5 - Excellent", "description": "The style is engaging and perfectly suited for the topic." }
        ]
    },
    {
        "key": "overall_impression",
        "label": "Overall: As a stand-alone piece of writing, what is your overall impression of this text?",
        "options": [
            { "label": "1 - Very Poor", "description": "Unacceptable quality, many flaws." },
            { "label": "2 - Poor", "description": "Has significant flaws that detract from the text." },
            { "label": "3 - Acceptable", "description": "Generally okay, but with noticeable room for improvement." },
            { "label": "4 - Good", "description": "Well-written and effective with only minor issues." },
            { "label": "5 - Excellent", "description": "Exceptionally clear, fluent, and well-written." }
        ]
    }
]

def transform_nested_data_for_html(source_data):
    """
    Transforms the nested source data into a "flat" list of task objects
    ready to be used by the HTML template.

    Args:
        source_data (list): A list of objects, where each object contains a title,
                            an original text, and a list of simplifications.

    Returns:
        list: A flat list where each item represents one simplification evaluation task.
    """
    # This will be the final flat list of tasks for the HTML
    task_list = []

    # Loop through each top-level document (e.g., "Blackrocks Brewery")
    for document in source_data:
        original_text = document.get("original", "")
        
        # Loop through each simplification within that document
        for simplification in document.get("simplifications", []):
            all_issues = []
            evaluation_data = simplification.get("evaluation", {})

            # Process meaning_issues if they exist
            if "meaning_issues" in evaluation_data:
                for issue in evaluation_data.get("meaning_issues", []):
                    all_issues.append({
                        "type": "meaning",
                        "original_span": issue.get("original_span"),
                        "simplified_span": issue.get("simplified_span"),
                        "explanation": issue.get("explanation"),
                        "suggested_fix": issue.get("suggested_fix")
                    })

            # Process writing_issues if they exist
            if "writing_issues" in evaluation_data:
                for issue in evaluation_data.get("writing_issues", []):
                    all_issues.append({
                        "type": "writing",
                        "original_span": None,
                        "simplified_span": issue.get("span"),
                        "explanation": issue.get("explanation"),
                        "suggested_fix": issue.get("suggested_fix")
                    })
            
            # Create a single, flat task object for this simplification
            task_item = {
                "title": document.get("title", "No Title"),
                "model_id": simplification.get("model_id", "UNKNOWN_MODEL"),
                "original": original_text,
                "simplified": simplification.get("simplified", ""),
                "evaluation": {
                    "overall_questions": STANDARD_OVERALL_QUESTIONS,
                    "simplicity_issues": all_issues
                }
            }
            task_list.append(task_item)
            
    return task_list

def sanitize_filename(name):
    """
    Takes a string and returns a version safe for use as a filename.
    Replaces spaces with underscores and removes non-alphanumeric characters.
    """
    name = name.replace(' ', '_')
    name = re.sub(r'[^a-zA-Z0-9_.-]', '', name)
    return name.lower()

def main():
    """
    Main function to run the script. Reads the nested input file, loops through
    each document, and creates a separate transformed JSON file for each one
    in a new directory.
    """
    input_filename = 'source_data_nested.json'
    output_directory = 'tasks_for_html'

    if not os.path.exists(input_filename):
        print(f"---")
        print(f"Error: Input file '{input_filename}' not found.")
        print(f"Please run the 'merge_data.py' script first to generate this file.")
        print(f"---")
        return

    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            source_data = json.load(f)

        if not source_data:
            print(f"---")
            print(f"Warning: Input file '{input_filename}' is empty. No output generated.")
            print(f"---")
            return

        # Loop over each document in the source data
        for document in source_data:
            # Each document becomes a separate task containing all its simplifications
            task_list_for_html = transform_nested_data_for_html([document])
            
            # Create a safe filename from the document title
            doc_title = document.get("title", "untitled_document")
            sanitized_title = sanitize_filename(doc_title)
            output_filename = os.path.join(output_directory, f"{sanitized_title}.json")

            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(task_list_for_html, f, ensure_ascii=False, indent=4)
            
            print(f"✅ Created task file: '{output_filename}'")
        
        print(f"\n---")
        print(f"🎉 Success! All documents have been processed.")
        print(f"Output files are located in the '{output_directory}' directory.")
        print(f"---")


    except json.JSONDecodeError:
        print(f"---")
        print(f"Error: The input file '{input_filename}' contains invalid JSON.")
        print(f"---")
    except Exception as e:
        print(f"---")
        print(f"An unexpected error occurred: {e}")
        print(f"---")

if __name__ == '__main__':
    main()

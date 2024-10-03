import csv
import ollama

def determine_shell(command):
    cmd_indicators = ['%', 'echo', 'set ', 'if ', 'for ', 'dir ', 'type ']
    for indicator in cmd_indicators:
        if indicator.lower() in command.lower():
            return 'CMD'
    return 'PowerShell'  # Default to PowerShell if no CMD indicators are found

def clean_response(response):
    return response.strip('`').strip()

def process_stig_csv(input_file_path, output_file_path):
    with open(input_file_path, 'r', newline='') as infile, \
         open(output_file_path, 'w', newline='') as outfile:
        
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['shell', 'command']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row_num, row in enumerate(reader, start=1):
            print(f"Processing row {row_num}")  # Debug print for row counter
            
            check_text = row['checktext']
            fix_text = row['fixtext']
            prompt = (
                "Write a command in PowerShell or CMD that will perform the following test on a Windows 11 Enterprise system."
                "Only return the command, no other text. Only give one answer for Powershell or CMD." 
                "Do not output any text other than the command itself."
                "If you are not certain of an answer then respond saying I don't know." 
                "Do not make up Powershell functions that do not exist."
                "Only write code to do the test. DO NOT WRITE CODE TO TRY AND FIX IT."
                "The check test field is as follows: {check_text}"
                "The fix test field is as follows: {fix_text}"
            )
            
            response = ollama.chat(model='deepseek-coder-v2', messages=[
                {'role': 'user', 'content': prompt}
            ])
            
            command = clean_response(response['message']['content'])
            shell = determine_shell(command)
            
            new_row = {**row, 'shell': shell, 'command': command}
            writer.writerow(new_row)

    print(f"Processing complete. Output saved to {output_file_path}")

process_stig_csv(r'C:\Store\Microsoft Windows 11 Security Technical Implementation Guide-MAC-3_Sensitive.csv', r'C:\Store\output.csv')
# File Editor Script

 

This script allows you to edit a specific line in a file and apply a manifest file to it. You can run this script from the command line and specify the line number and the new content for that line as arguments.

 

## Usage

 

To run the script, navigate to the directory containing the script in your terminal, and use the following command:

 

```
python line_editor.py line_num "new_content"
```

 

- `line_num`: An integer specifying the line number you want to edit (starting from 1).
- `new_content`: A string that specifies the new content for the line, enclosed in quotation marks.

 

Example:

 

```
python line_editor.py 2 "This is the new line content."
```
This command replaces the second line in the file with "This is the new line content."

 

### Reversing changes

 

To reverse the last changes made to the file, use the following command:

 

```
python line_editor.py --reverse
```
This command restores the file to its state before the last edit.

 

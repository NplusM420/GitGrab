# GitGrab

GitGrab is a powerful and user-friendly GUI tool for cloning GitHub repositories and selectively scraping specific files into a single Markdown document. It provides an intuitive interface for users to choose which files they want to include in their final output.
Use this to create files for use with giving AI models full context of an entire repo from a single folder. 

## Features

- Clone multiple GitHub repositories
- Visual file structure representation
- Selective file scraping
- Support for multiple file extensions
- Dark mode interface
- Progress tracking
- Error handling and logging

## Installation

1. Ensure you have Python 3.6 or higher installed on your system.

2. Clone this repository:
   ```
   git clone https://github.com/NplusM420/GitGrab.git
   cd GitGrab
   ```

3. (Optional but recommended) Create a virtual environment:
   ```
   python -m venv venv
   ```

4. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source venv/bin/activate
     ```

5. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the GitGrab tool:
   ```
   python GitGrab.py
   ```

2. The GitGrab GUI will open. Here's how to use it:

   a. Enter one or more GitHub repository URLs in the "GitHub URL(s)" field, separated by commas.
   
   b. (Optional) Specify a target folder for cloning the repositories.
   
   c. Modify the file extensions if needed (default extensions are provided).
   
   d. Click "Fetch Files" to clone the repositories and display their file structure.
   
   e. In the left pane, you'll see the file structure of the cloned repositories.
   
   f. Select files or folders you want to scrape:
      - Use the right-click context menu to add or remove files/folders.
      - Alternatively, select items and use the "Add Selected" or "Remove Selected" buttons.
   
   g. The right pane will show the list of files that will be included in the final output.
   
   h. Once you've selected all desired files, click "Start Scraping".
   
   i. The tool will create a `scraped_repos.md` file in the target folder, containing the content of all selected files.

3. After scraping, the cloned repositories will be automatically deleted to save space.

## Troubleshooting

- If you encounter any issues, check the `app_log.txt` file for error messages and debugging information.
- Ensure you have the necessary permissions to clone repositories and write files in the target directory.
- If you're having trouble with specific repositories, make sure they are public or you have the necessary access rights.

## Contributing

Contributions to GitGrab are welcome! Please feel free to submit pull requests, create issues or spread the word.

## License

[MIT License](LICENSE)

## Acknowledgements

GitGrab uses the following open-source libraries:
- tkinter for the GUI
- GitPython for repository cloning

Special thanks to all contributors and users of GitGrab!

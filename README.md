# Console-Based Editor - Multi-Line

A simple, basic console-based text editor with multi-line editing capabilities, demonstrating fundamental data structure and algorithm concepts in Python. This editor provides a command-line interface for text manipulation, inspired by early text editors that lacked sophisticated graphical user interfaces.

## Overview

This project focuses on designing and developing a console-based editor that supports multi-line text editing. Unlike modern WYSIWYG editors, this program operates purely through text commands entered via the keyboard. It aims to illustrate principles of problem decomposition, clean coding, and refactoring to achieve high code readability and maintainability.

The editor allows users to insert, append, delete characters and words, navigate through text using character and word-based movements, manage lines, and perform undo/repeat operations.

## Features

* **Multi-Line Editing:** Supports editing across multiple lines of text.
* **Cursor Management:**
    * Move cursor left (`h`), right (`l`), up (`j`), down (`k`).
    * Move to beginning of line (`^`), end of line (`$`).
    * Move to beginning of next word (`w`), previous word (`b`).
    * Toggle row cursor visibility (`.`) and line cursor visibility (`;`).
* **Text Manipulation:**
    * Insert text before cursor (`i <text>`).
    * Append text after cursor (`a <text>`).
    * Delete character at cursor (`x`).
    * Delete word and trailing spaces at cursor (`dw`).
* **Line Operations:**
    * Copy current line to memory (`yy`).
    * Paste copied line(s) below current line (`p`).
    * Paste copied line(s) above current line (`P`).
    * Delete current line (`dd`).
    * Insert empty line below (`o`).
    * Insert empty line above (`O`).
* **History & Utility:**
    * Undo previous command (`u`).
    * Repeat last command (`r`).
    * Show current content (`s`).
    * Display help information (`?`).
    * Quit program (`q`).
* **Console-Based Interface:** All interactions happen via a simple `>` prompt in the terminal.
* **Command Parsing & Validation:** Ensures user input adheres to defined command syntax.
* **Undo/Repeat Logic:** Implements a stack-based mechanism for undoing and repeating commands, with specific rules for non-modifying commands.

## Getting Started

### Prerequisites

* Python 3.x installed on your system.
* No external modules beyond `re` are required.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/ConsoleEditor.git](https://github.com/your-username/ConsoleEditor.git)
    cd ConsoleEditor
    ```
    (Replace `your-username` with your actual GitHub username.)

2.  **Ensure the main script is present:**
    The main script, `A3_SDS_124040088.py`, should be in the directory.

### Running the Program

Execute the main Python script from your terminal:

```bash
python A3_SDS_124040088.py
```

The editor will start and display a `>` prompt, awaiting your commands.

## Project Structure

* `A3_SDS_124040088.py`: The core Python script containing all the editor's logic, including state management, command parsing, command execution, and display functions.
* `Editor-Multi-Line-Basic-2025(4).pdf`: The assignment brief detailing the project requirements, scope, and specific command behaviors.

## Commands

Here is a list of supported commands:

| Command | Description                                   |
| :------ | :-------------------------------------------- |
| `?`     | display this help info                        |
| `.`     | toggle row cursor on and off                  |
| `;`     | toggle line cursor on and off                 |
| `h`     | move cursor left                              |
| `j`     | move cursor up                                |
| `k`     | move cursor down                              |
| `l`     | move cursor right                             |
| `^`     | move cursor to beginning of the line          |
| `$`     | move cursor to end of the line                |
| `w`     | move cursor to beginning of next word         |
| `b`     | move cursor to beginning of previous word     |
| `i <text>`| insert `<text>` before cursor                 |
| `a <text>`| append `<text>` after cursor                  |
| `x`     | delete character at cursor                    |
| `dw`    | delete word and trailing spaces at cursor     |
| `yy`    | copy current line to memory                   |
| `p`     | paste copied line(s) below line cursor        |
| `P`     | paste copied line(s) above line cursor        |
| `dd`    | delete line                                   |
| `o`     | insert empty line below                       |
| `O`     | insert empty line above                       |
| `u`     | undo previous command                         |
| `r`     | repeat last command                           |
| `s`     | show content                                  |
| `q`     | quit program                                  |

**Note on Command Syntax:**
* Commands like `i` and `a` require additional text input. For example: `i Hello World`.
* All commands are case-sensitive.
* Invalid commands will simply result in a new prompt without an error message.

## Code Overview

The `A3_SDS_124040088.py` script is organized into several functions, each responsible for a specific part of the editor's functionality:

* `initialize_state()`: Sets up the initial state of the editor, including content, cursor positions, clipboard, and undo stack.
* `save_state(state)`: Pushes the current editor state onto the undo stack.
* `restore_state(state, saved_state)`: Restores the editor's state from a saved snapshot.
* `clamp_cursor(state)`: Ensures cursor positions remain within valid bounds of the current line and content.
* `parse_command(cmd)`: Parses the raw user input string into a command and its argument (if any).
* `find_word_boundary(line, pos, direction)`: Helper for word navigation, finding the start of the next or previous word.
* `next_word(state)`: Moves the cursor to the beginning of the next word.
* `previous_word(state)`: Moves the cursor to the beginning of the previous word.
* `handle_cursor_toggle(state, cursor_type, _)`: Toggles the visibility of either the row or line cursor.
* `handle_h(state, _)`: Moves the cursor one position to the left.
* `handle_l(state, _)`: Moves the cursor one position to the right.
* `handle_j(state, _)`: Moves the cursor one line up.
* `handle_k(state, _)`: Moves the cursor one line down.
* `handle_caret(state, _)`: Moves the cursor to the beginning of the current line.
* `handle_dollar(state, _)`: Moves the cursor to the end of the current line.
* `handle_word_navigation(state, direction, _)`: Dispatches to `next_word` or `previous_word`.
* `handle_i(state, arg)`: Inserts the given text before the cursor.
* `handle_a(state, arg)`: Appends the given text after the cursor.
* `handle_x(state, _)`: Deletes the character at the cursor.
* `handle_dw(state, _)`: Deletes the word at the cursor, including trailing spaces.
* `find_word_end(line, pos)`: Helper for `dw`, finds the end of a word including spaces.
* `handle_yy(state, _)`: Copies the current line to the clipboard.
* `handle_dd(state, _)`: Deletes the current line.
* `handle_insert_line(state, above)`: Inserts an empty line either above or below the current line.
* `handle_paste(state, above)`: Pastes the content from the clipboard either above or below the current line.
* `handle_u(state, _)`: Undoes the last modifying command.
* `handle_r(state, _)`: Repeats the last modifying command.
* `handle_command(state, cmd, arg)`: The central dispatcher that executes the appropriate handler function for a given command. It also manages the undo stack and command history.
* `render_cursor_segment(state, line, cursor_pos)`: Formats a line segment to include cursor highlighting using ANSI escape codes.
* `display_content(state)`: Prints the current editor content to the console, applying line and row cursor indicators if enabled.
* `display_help_info()`: Prints the list of all available commands and their descriptions.
* `main()`: The main loop of the editor, handling user input, parsing commands, executing them, and displaying content until the quit command is issued.

## Contributing

Feel free to fork this repository, make improvements, and submit pull requests.

## License

This project is developed for educational purposes as part of the CSC1002-Computational Laboratory course.

## Contact

For any questions or feedback, please open an issue in the GitHub repository.

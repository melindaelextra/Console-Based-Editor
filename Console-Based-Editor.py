def initialize_state():
    '''
    Initializes the editor state with default values.

    Args:
        None

    Returns:
        dict: A dictionary containing the initial editor state.
    '''
    return {
        'cursor_highlight': "\033[42m",
        'cursor_reset': "\033[0m",
        'content': [],
        'current_line': 0,
        'current_row': 0,
        'show_line_cursor': False,
        'show_row_cursor': False,
        'clipboard': None,
        'undo_stack': [],
        'command_history': []
    }

def save_state(state):
    '''
    Saves the current editor state to the undo stack.

    Args:
        state (dict): The current state of the editor.

    Returns:
        None
    '''
    state['undo_stack'].append({
        'content': list(state['content']),
        'current_line': state['current_line'],
        'current_row': state['current_row'],
        'show_line_cursor': state['show_line_cursor'],
        'show_row_cursor': state['show_row_cursor'],
        'clipboard': state['clipboard']
    })

def restore_state(state, saved_state):
    '''
    Restores the editor state from a saved state.

    Args:
        state (dict): The current state of the editor.
        saved_state (dict): The saved state to restore.

    Returns:
        None
    '''
    state.update({
        'content': list(saved_state['content']),
        'current_line': saved_state['current_line'],
        'current_row': saved_state['current_row'],
        'show_line_cursor': saved_state['show_line_cursor'],
        'show_row_cursor': saved_state['show_row_cursor'],
        'clipboard': saved_state['clipboard']
    })

def clamp_cursor(state):
    '''
    Ensures the cursor positions stay within valid bounds.

    Args:
        state (dict): The current state of the editor.

    Returns:
        None
    '''
    line_count = len(state['content'])
    state['current_line'] = max(0, min(state['current_line'], line_count - 1)) if line_count > 0 else 0
    line_length = len(state['content'][state['current_line']]) if state['content'] and state['current_line'] < line_count else 0
    state['current_row'] = max(0, min(state['current_row'], line_length - 1 if line_length > 0 else 0))

def parse_command(cmd):
    '''
    Parses and validates user command input.

    Args:
        cmd (str): Raw command input from user.

    Returns:
        tuple: (command, argument) or (None, None) if invalid.
    '''
    patterns = [
        (lambda c: c in {'?', '.', ';', 'h', 'j', 'k', 'l', '^', '$', 'x', 's', 'q', 'w', 'b'},
         lambda c: (c, None)),
        (lambda c: c in {'dw', 'yy', 'dd', 'p', 'P', 'o', 'O'},
         lambda c: (c, None)),
        (lambda c: c.startswith('i'),
         lambda c: ('i', c[1:]) if len(c) > 1 else (None, None)),
        (lambda c: c.startswith('a'),
         lambda c: ('a', c[1:]) if len(c) > 1 else (None, None)),
        (lambda c: c in {'u', 'r'},
         lambda c: (c, None))
    ]
    return next((handler(cmd) for condition, handler in patterns if condition(cmd)), (None, None))

def find_word_boundary(line, pos, direction):
    '''
    Finds the start position of the next/previous word in a line.

    Args:
        line (str): The text line to search.
        pos (int): The starting position.
        direction (int): 1 for next, -1 for previous

    Returns:
        int: The position of the next/previous word start.
    '''
    isspace_func = lambda ch: ch.isspace()
    
    if direction == 1:
        while pos < len(line) and not isspace_func(line[pos]):
            pos += 1
        while pos < len(line) and isspace_func(line[pos]):
            pos += 1
    elif direction == -1:
        while pos > 0 and isspace_func(line[pos-1]):
            pos -= 1
        while pos > 0 and not isspace_func(line[pos-1]):
            pos -= 1
    return pos

def next_word(state):
    '''
    Moves the cursor to the start of the next word in the current line.

    Args:
        state (dict): The current state of the editor.

    Returns:
        None
    '''
    if not state['content'] or not (line := state['content'][state['current_line']]):
        return
    original = state['current_row']
    new_pos = find_word_boundary(line, original, 1)
    state['current_row'] = original if new_pos >= len(line) else new_pos
    clamp_cursor(state)

def previous_word(state):
    '''
    Moves the cursor to the start of the previous word in the current line.

    Args:
        state (dict): The current state of the editor.

    Returns:
        None
    '''
    if not state['content'] or not (line := state['content'][state['current_line']]):
        return
    state['current_row'] = find_word_boundary(line, state['current_row'], -1)
    clamp_cursor(state)

def handle_cursor_toggle(state, cursor_type, _):
    '''
    Toggles the visibility of the row or line cursor.

    Args:
        state (dict): The current state of the editor.
        cursor_type (str): 'row' or 'line'.
        _ (None): Unused argument.

    Returns:
        None
    '''
    if cursor_type == 'row':
        state['show_row_cursor'] = not state['show_row_cursor']
    elif cursor_type == 'line':
        state['show_line_cursor'] = not state['show_line_cursor']

def handle_h(state, _):
    '''
    Moves the cursor left one character.

    Args:
        state (dict): The current state of the editor.
        _ (None): Unused argument.

    Returns:
        None
    '''
    state['current_row'] = max(0, state['current_row'] - 1)

def handle_l(state, _):
    '''
    Moves the cursor right one character.

    Args:
        state (dict): The current state of the editor.
        _ (None): Unused argument.

    Returns:
        None
    '''
    if state['content']:
        state['current_row'] = min(len(state['content'][state['current_line']]), state['current_row'] + 1)

def handle_j(state, _):
    '''
    Moves the cursor up one line.

    Args:
        state (dict): The current state of the editor.
        _ (None): Unused argument.

    Returns:
        None
    '''
    if state['current_line'] > 0:
        state['current_line'] -= 1

def handle_k(state, _):
    '''
    Moves the cursor down one line.

    Args:
        state (dict): The current state of the editor.
        _ (None): Unused argument.

    Returns:
        None
    '''
    if state['current_line'] < len(state['content']) - 1:
        state['current_line'] += 1

def handle_caret(state, _):
    '''
    Moves the cursor to the start of the current line.

    Args:
        state (dict): The current state of the editor.
        _ (None): Unused argument.

    Returns:
        None
    '''
    state['current_row'] = 0

def handle_dollar(state, _):
    '''
    Moves the cursor to the end of the current line.

    Args:
        state (dict): The current state of the editor.
        _ (None): Unused argument.

    Returns:
        None
    '''
    state['current_row'] = len(state['content'][state['current_line']]) if state['content'] else 0

def handle_word_navigation(state, direction, _):
    '''
    Handles word navigation commands (next/previous).

    Args:
        state (dict): The current state of the editor.
        direction (str): 'next' or 'previous'.
        _ (None): Unused argument.

    Returns:
        None
    '''
    if direction == 'next':
        next_word(state)
    elif direction == 'previous':
        previous_word(state)

def handle_i(state, arg):
    '''
    Inserts text before the cursor position.

    Args:
        state (dict): The current state of the editor.
        arg (str): The text to insert.

    Returns:
        None
    '''
    if not state['content']:
        state['content'].append("")
    cl = state['current_line']
    cr = state['current_row']
    line = state['content'][cl]
    state['content'][cl] = line[:cr] + arg + line[cr:]
    state['command_history'].append(('i', arg))

def handle_a(state, arg):
    '''
    Appends text after the cursor position.

    Args:
        state (dict): The current state of the editor.
        arg (str): The text to append.

    Returns:
        None
    '''
    if not state['content']:
        state['content'].append("")
    cl = state['current_line']
    cr = state['current_row']
    line = state['content'][cl]
    state['content'][cl] = line[:cr+1] + arg + line[cr+1:]
    state['current_row'] += len(arg)
    state['command_history'].append(('a', arg))

def handle_x(state, _):
    '''
    Deletes the character at the cursor position.

    Args:
        state (dict): The current state of the editor.
        _ (None): Unused argument.

    Returns:
        None
    '''
    if state['content'] and state['content'][state['current_line']] and state['current_row'] < len(state['content'][state['current_line']]):
        cl = state['current_line']
        cr = state['current_row']
        state['content'][cl] = state['content'][cl][:cr] + state['content'][cl][cr+1:]
        state['command_history'].append(('x', None))

def handle_dw(state, _):
    '''
    Deletes the word and trailing spaces at the cursor.

    Args:
        state (dict): The current state of the editor.
        _ (None): Unused argument.

    Returns:
        None
    '''
    if not state['content'] or not (line := state['content'][state['current_line']]):
        return
    cr = state['current_row']
    state['content'][state['current_line']] = (line[:cr] + line[find_word_end(line, cr):]) or ""
    state['command_history'].append(('dw', None))

def find_word_end(line, pos):
    '''
    Finds the end position of the current word including trailing spaces.

    Args:
        line (str): The line to search.
        pos (int): The starting position.

    Returns:
        int: The end position of the word + trailing spaces.
    '''
    while pos < len(line) and not line[pos].isspace():
        pos += 1
    while pos < len(line) and line[pos].isspace():
        pos += 1
    return pos

def handle_yy(state, _):
    '''
    Copies the current line to the clipboard.

    Args:
        state (dict): The current state of the editor.
        _ (None): Unused argument.

    Returns:
        None
    '''
    if state['content']:
        state['clipboard'] = state['content'][state['current_line']]

def handle_dd(state, _):
    '''
    Deletes the current line.

    Args:
        state (dict): The current state of the editor.
        _ (None): Unused argument.

    Returns:
        None
    '''
    if state['content']:
        del state['content'][state['current_line']]
        state['current_line'] = max(0, min(state['current_line'], len(state['content'])-1)) if state['content'] else 0
        state['command_history'].append(('dd', None))

def handle_insert_line(state, above):
    '''
    Inserts an empty line above or below the current line.

    Args:
        state (dict): The current state of the editor.
        above (bool): True to insert above, False to insert below.

    Returns:
        None
    '''
    if above:
        state['content'].insert(state['current_line'], "")
        state['command_history'].append(('O', None))
    else:
        state['content'].insert(state['current_line'] + 1, "")
        state['current_line'] += 1
        state['current_row'] = 0
        state['command_history'].append(('o', None))

def handle_paste(state, above):
    '''
    Pastes the copied line above or below the current line.

    Args:
        state (dict): The current state of the editor.
        above (bool): True to paste above, False to paste below.

    Returns:
        None
    '''
    if state['clipboard'] is not None:
        if above:
            state['content'].insert(state['current_line'], state['clipboard'])
            state['command_history'].append(('P', None))
        else:
            state['content'].insert(state['current_line'] + 1, state['clipboard'])
            state['current_line'] += 1
            state['command_history'].append(('p', None))

def handle_u(state, _):
    '''
    Undoes the last command.

    Args:
        state (dict): The current state of the editor.
        _ (None): Unused argument.

    Returns:
        None
    '''
    if not state['undo_stack']:
        return
    restore_state(state, state['undo_stack'].pop())
    if state['command_history']:
        state['command_history'].pop()

def handle_r(state, _):
    '''
    Repeats the last command.

    Args:
        state (dict): The current state of the editor.
        _ (None): Unused argument.

    Returns:
        None
    '''
    if state['command_history']:
        last_cmd = state['command_history'][-1]
        handle_command(state, last_cmd[0], last_cmd[1])

command_map = {
    '.': lambda s, a: handle_cursor_toggle(s, 'row', a),
    ';': lambda s, a: handle_cursor_toggle(s, 'line', a),
    'h': handle_h,
    'l': handle_l,
    'j': handle_j,
    'k': handle_k,
    '^': handle_caret,
    'w': lambda s, a: handle_word_navigation(s, 'next', a),
    'b': lambda s, a: handle_word_navigation(s, 'previous', a),
    '$': handle_dollar,
    'i': handle_i,
    'a': handle_a,
    'x': handle_x,
    'dw': handle_dw,
    'yy': handle_yy,
    'dd': handle_dd,
    'o': lambda s, a: handle_insert_line(s, False),
    'O': lambda s, a: handle_insert_line(s, True),
    'p': lambda s, a: handle_paste(s, False),
    'P': lambda s, a: handle_paste(s, True),
    'u': handle_u,
    'r': handle_r,
}

def handle_command(state, cmd, arg):
    '''
    Executes an editor command.

    Args:
        state (dict): The current state of the editor.
        cmd (str): The command to execute.
        arg (str): The argument for the command.

    Returns:
        None
    '''
    if cmd not in ['u', 'r', '?', 's']:
        save_state(state)
    handler = command_map.get(cmd)
    if handler:
        handler(state, arg)
    clamp_cursor(state)
    
    if cmd not in ['u', 'r', '?', 's']:
        if cmd in command_map and cmd != 'r':
            state['command_history'].append((cmd, arg))
    elif cmd == 'u' and state['command_history']:
        state['command_history'].pop()

def render_cursor_segment(state, line, cursor_pos):
    '''
    Renders a line segment with cursor highlighting.

    Args:
        state (dict): The current state of the editor.
        line (str): The line to render.
        cursor_pos (int): The cursor position.

    Returns:
        str: The rendered line segment.
    '''
    if not line:
        return ""
    clamped_pos = min(cursor_pos, len(line) - 1)
    return f"{line[:clamped_pos]}{state['cursor_highlight']}{line[cursor_pos]}{state['cursor_reset']}{line[cursor_pos+1:]}"

def display_content(state):
    '''
    Displays the editor content with cursor markers.

    Args:
        state (dict): The current state of the editor.

    Returns:
        None
    '''
    if not state['content']:
        return

    for idx, line in enumerate(state['content']):
        prefix = "*" if (state['show_line_cursor'] and idx == state['current_line']) else " " if state['show_line_cursor'] else ""
        if idx == state['current_line'] and state['show_row_cursor']:
            line_part = render_cursor_segment(state, line, state['current_row'])
        else:
            line_part = line
        print(f"{prefix}{line_part}")

def display_help_info():
    '''
    Displays the help information.

    Args:
        None

    Returns:
        None
    '''
    help_data = [
        ('?', 'display this help info'),
        ('.', 'toggle row cursor on and off'),
        (';', 'toggle line cursor on and off'),
        ('h', 'move cursor left'),
        ('j', 'move cursor up'),
        ('k', 'move cursor down'),
        ('l', 'move cursor right'),
        ('^', 'move cursor to beginning of the line'),
        ('$', 'move cursor to end of the line'),
        ('w', 'move cursor to beginning of next word'),
        ('b', 'move cursor to beginning of previous word'),
        ('i', 'insert <text> before cursor'),
        ('a', 'append <text> after cursor'),
        ('x', 'delete character at cursor'),
        ('dw', 'delete word and trailing spaces at cursor'),
        ('yy', 'copy current line to memory'),
        ('p', 'paste copied line(s) below line cursor'),
        ('P', 'paste copied line(s) above line cursor'),
        ('dd', 'delete line'),
        ('o', 'insert empty line below'),
        ('O', 'insert empty line above'),
        ('u', 'undo previous command'),
        ('r', 'repeat last command'),
        ('s', 'show content'),
        ('q', 'quit program')
    ]
    print('\n'.join(f"{cmd} - {desc}" for cmd, desc in help_data))

def main():
    '''
    Main function to run the editor.

    Args:
        None

    Returns:
        None
    '''
    state = initialize_state()
    while True:
        user_input = input(">")
        if user_input == 'q':
            break
        cmd, arg = parse_command(user_input)
        if cmd is None:
            continue
        if cmd == '?':
            display_help_info()
        else:
            handle_command(state, cmd, arg)
            display_content(state)

if __name__ == "__main__":
    main()
import os
from os import path
import pandas
from database import Database, DataCell
import re
import pickle
from random import choice
import string


def main() -> None:
    PSM_VERSION = '1.0.1'
    global PF_PATH
    PF_PATH = 'data.bin'
    global DB_PATH
    DB_PATH = path.join('data', 'database.json')
    os.chdir(path.dirname(path.realpath(__file__)))
    check_for_data()
    log_in()
    global database
    database = Database()
    database.load()

    command = ''
    os.system('cls')
    os.system('cls')
    print(f'PSM version {PSM_VERSION}')
    while True:
        print('Commands: help, show [int], search [str] [float], new, edit, delete, export, chpassword, save, exit.')
        command = input('> ').lower().strip()
        os.system('cls')
        print(f'> {command}')
        if command == 'help':
            help_function()
            print()
        elif command.startswith('show'):
            number = parse_int(command)
            print_db(command, number)
        elif command == 'new':
            print('Creating new data cell.')
            cell = new_cell()
            database.update(cell)
            database.save()
            print(f'Saved with ID {cell.id}!')
            print()
        elif command == 'edit':
            print('Editing data cell.')
            cell_id, is_cancelled = input_id()
            if not is_cancelled:
                cell = edit_cell(cell_id)
                database.update(cell)
                database.save()
                print('Saved!')
            else:
                print('Cancelled.')
            print()
        elif command == 'delete':
            print('Deleting data cell.')
            cell_id, is_cancelled = input_id()
            if not is_cancelled:
                database.rm(cell_id)
                print('Deleted!')
            else:
                print('Cancelled.')
            print()
        elif command == 'export':
            print('Exporting data.')
            savedir, is_cancelled = enter_dir()
            if not is_cancelled:
                export_data(savedir)
            else:
                print('Cancelled.')
            print()
        elif command.startswith('search'):
            search_db(command)
            print()
        elif command == 'chpassword':
            change_password()
            print('Password changed!')
            print()
        elif command == 'save':
            database.save()
            print('Database saved!')
            print()
        elif command == 'exit':
            break
        else:
            print(f'No such command "{command}"')
            print()

    database.save()


def help_function() -> None:
    """Print help for each command."""
    # show
    print('\033[31mshow\033[0m')
    print('Show database content. Usage: show [i: int], i - how many results to show at one time.')
    # search
    print('\033[31msearch\033[0m')
    print('Search in database by word. Usage: search [query: str] [i: float], query - what to search for, i - indicator of similarity.')
    # new
    print('\033[31mnew\033[0m')
    print('Create new data cell with information. Usage: new.')
    print('Note: you can press do "Tab <n: int>" when filling in password field. This will create a good password of n signs.')
    # edit
    print('\033[31medit\033[0m')
    print('Edit data cell (cell is defined by ID). Usage: edit.')
    # delete
    print('\033[31mdelete\033[0m')
    print('Delete data cell (cell is defined by ID). Usage: delete.')
    # export
    print('\033[31mexport\033[0m')
    print('Export database as .xlsx file to folder user gives. Usage: export.')
    # chpassword
    print('\033[31mchpassword\033[0m')
    print('Change password to enter this app. Usage: chpassword.')
    # save
    print('\033[31msave\033[0m')
    print('Save database. Usage: save.')
    # exit
    print('\033[31mexit\033[0m')
    print('ALWAYS run this command when you want to exit an app, otherwise database won\'t be updated. Usage: exit.')
    print('Sometimes you can enter "x" to cancel.')


def init() -> None:
    """Create all files, setup password."""
    new = ''
    while new == '':
        new = input('Create password to enter an app: ')
        if new == '':
            print('Password field can\'t be empty.')
    save_password(new)
    # do not create new file if there is already one (might be with password)
    if not path.exists(DB_PATH):
        if not path.exists('data'):
            os.mkdir('data')
        with open(DB_PATH, 'w') as db_file:
            db_file.write('[]')


def check_for_data() -> None:
    """Check if there are any passwords, if not - init()."""
    if path.exists(PF_PATH) and path.exists(DB_PATH):
        p = load_password()
        if not p:
            init()
    else:
        init()


def load_password() -> str:
    """Read and encode password from file."""
    pf = open(PF_PATH, 'rb')
    try:
        p = pickle.load(pf)
        pf.close()
        return p
    except EOFError:
        pf.close()
        save_password('')
        return ''


def save_password(x: str) -> None:
    """Encode and save password to file."""
    with open(PF_PATH, 'wb') as pf:
        pickle.dump(x, pf)


def log_in() -> None:
    """Enter a password to open an app."""
    password = load_password()
    input_password = input('Enter password: ')
    while input_password != password:
        input_password = input('Enter password: ')


def change_password() -> None:
    """Update password of the app."""
    print('Changing app password.')
    password = load_password()
    p = input('Enter old password: ')
    if p != password:
        return
    new = input('Enter new password: ')
    if not new:
        print('Password field can\'t be empty.')
    confirm = input('Confirm new password: ')
    if new != confirm:
        print('Passwords don\'t match.')
        return
    save_password(new)


def search_db(cmd: str) -> None:
    """Search for something in database. Result will be printed."""
    cwords = cmd.split()
    if len(cwords) == 1:
        print('Incorrect usage.')
        return
    if len(cwords) > 2 and cwords[-1].isnumeric():  # search q ... 0.5
        query = ' '.join(cwords[1:-1])
        i = float(cwords[-1])
    elif len(cwords) > 2:  # search q ... q
        query = ' '.join(cwords[1:])
        i = 0.8
    else:  # search q
        query = cwords[1]
        i = 0.8
    if i == 0:
        print('Incorrect value of i.')
        return

    print(f'Searching for {query}.')
    search_results = database.search_db(query, i)
    print(f'Found {len(search_results)} matches.')
    for cell in search_results:
        print_cell(cell, True)


def enter_dir() -> tuple:
    save_path = ''
    while not path.isdir(path.dirname(save_path)):
        save_path = input('Enter directory: ')
        if save_path.lower() == 'x':
            return '', True
        if not path.isdir(path.dirname(save_path)):
            print('Wrong directory!')
    return save_path, False


def edit_cell(cell_id: int) -> DataCell:
    """Edit data cell."""
    cell = database.find_cell(cell_id)
    print_cell(cell, False)

    choice = ''
    cell_content = ['name', 'link', 'login', 'email', 'password', 'other_data', 'codes']

    def edit_cell(cell_content):
        print('What you want to edit?', end=' ')
        for i in cell_content:
            if cell_content.index(i) != len(cell_content):
                end = ', '
            else:
                end = '. '
            print(i, end=end)
        print("Use 's' to save changes.")

    edit_cell(cell_content)
    while choice != 's':
        choice = input('Element to edit: ')
        if choice in cell_content:
            i = input('new '+choice+': ')
            cell.update(choice, i)
            os.system('cls')
            print_cell(cell, False)
            edit_cell(cell_content)
    return cell


def input_id() -> tuple:
    """Enter existing ID."""
    cell_id = ''
    while cell_id not in database.ids():
        cell_id = input('ID: ')
        if cell_id.lower() == 'x': # cancel
            return 0, True
        if cell_id.isnumeric():
            cell_id = int(cell_id)
        if cell_id not in database.ids():
            print('Incorrect ID!')
    return cell_id, False


def gen_password(length: int) -> str:
    """Create a string of random letters, numbers and special characters."""
    if length < 6: # length too min to create reliable password
        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(choice(characters) for _ in range(length))
        return password
    # 1/6 - punctuation, 2/6 - digits, 3/6 - letters
    punc_amount = length // 6
    dig_amount = length // 6 * 2
    let_amount = length - punc_amount - dig_amount
    to_build_from = [choice(string.punctuation) for _ in range(punc_amount)] + [choice(string.digits) for _ in range(dig_amount)] + [choice(string.ascii_letters) for _ in range(let_amount)]
    password = ''
    for _ in range(length):
        l = choice(to_build_from)
        password += l
        to_build_from.remove(l)
    return password


def parse_int(s: str, is_password: bool=False) -> int:
    """Get integer from end of a string."""
    if bool(re.search(r'\d', s)):  # digit in s
        try:
            number =  int(s.split()[-1])
        except Exception:
            if is_password:
                return 8
            return 2
        if number < 1:
            if is_password:
                return 8
            return 2
        return number
    if is_password:
        return 8
    return 2


def new_cell() -> DataCell:
    """Create a new data cell."""
    x = {}
    cell_content = ['name', 'link', 'login', 'email', 'password', 'other_data', 'codes']
    max_len = len(max(cell_content, key=len))
    for i in cell_content:
        x[i] = input(i.replace('_', ' ')+': '+' '*(max_len-len(i)))
        if i == 'password' and x[i].startswith('\t'): # tab - generate password
            n = parse_int(x[i], True)
            x[i] = gen_password(n)
    x['id'] = database.gen_id()
    return DataCell(x)


def print_cell(cell: DataCell, show_id: bool) -> None:
    """Print data cell content"""
    print('----------')
    if show_id:
        print(f'\033[32mname\033[0m:       {cell.name}')
    else:
        print(f'name:       {cell.name}')
    print(f'link:       {cell.link}')
    print(f'login:      {cell.login}')
    print(f'email:      {cell.email}')
    print(f'password:   {cell.password}')
    print(f'other data: {cell.other_data}')
    print(f'codes:      {cell.codes}')
    if show_id:
        print(f'\033[35mid\033[0m:         {cell.id}')
    print('----------')


def print_db(command: str, psize: int = 2) -> None:
    """Print database by parts."""
    page_amount = len(database.data_cells) // psize + bool(len(database.data_cells) % psize)
    current_page = 1
    for number, cell in enumerate(database.data_cells, start=1):
        print_cell(cell, True)
        if number % psize == 0 or number == len(database.data_cells):
            print(f'[{current_page}/{page_amount}]')
        if number % psize == 0:
            current_page += 1
            if number != len(database.data_cells):
                n = input('...')
                if n.lower() == 'x': # Cancel viewing DB
                    return
                os.system('cls')
                print(f'> {command}')
    print()


def export_data(output_dir: str) -> None:
    """Export data as excel file to directory user gives."""
    index = 1
    filename = 'passwords.xlsx'
    while path.exists(path.join(output_dir, filename)): # find name that is not taken
        filename = f'passwords ({index}).xlsx'
        index += 1
    pandas.read_json(path.join('data', 'database.json')).to_excel(path.join(output_dir, filename), header=['Resource', 'Link', 'Login', 'Email', 'Password', 'Other data', 'Codes', 'ID in database'], index=False)
    print(f'Exported as {filename}!')

# main() # DEBUG

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('A program error has occurred:')
        print(e)

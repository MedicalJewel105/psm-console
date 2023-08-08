import os
from os import path
from database import Database, DataCell
import re
from cryptography.fernet import Fernet
from random import choice, randint
import string
from getpass import getpass
import json


def main() -> None:
    PSM_VERSION = '1.0.2'
    global PF_PATH
    PF_PATH = 'data.dat' # password file
    global KEY_PATH
    KEY_PATH = 'key.dat' # password encryption 
    global DB_PATH
    DB_PATH = path.join('data', 'database.dat')
    global DB_KEY_PATH
    DB_KEY_PATH = path.join('data', 'key.dat')
    os.chdir(path.dirname(path.realpath(__file__)))
    check_for_data()
    log_in()
    global database
    database = Database(db_path=DB_PATH, key_path=DB_KEY_PATH)
    database.load(None)

    command = ''
    os.system('cls')
    print(f'PSM version {PSM_VERSION}')
    while True:
        print()
        print('Commands: help, show [int], search [str] [float], new, edit, delete, export, save, exit, admin.')
        command = input('> ').lower().strip()
        os.system('cls')
        print(f'> {command}')
        if command == 'help':
            help_function()
        elif command.startswith('show'):
            number = parse_int(command, 2)
            print_db(command, number)
        elif command == 'new':
            print('Creating new data cell.')
            cell = new_cell()
            database.update(cell)
            database.save()
            print(f'Saved with ID {cell.id}!')
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
        elif command == 'delete':
            print('Deleting data cell.')
            cell_id, is_cancelled = input_id()
            if not is_cancelled:
                database.rm(cell_id)
                print('Deleted!')
            else:
                print('Cancelled.')
        elif command == 'export':
            print('Exporting data.')
            export_format, is_cancelled = choose_from(database.export_formats)
            if not is_cancelled:
                savedir, is_cancelled = enter_dir()
                if not is_cancelled:
                    database.export_db(savedir, export_format)
                else:
                    print('Cancelled.')
            else:
                print('Cancelled.')
        elif command.startswith('search'):
            search(command)
        elif command == 'save':
            database.save()
            print('Database saved!')
        elif command == 'exit':
            break
        elif command == 'admin':
            print('Admin commands: chpassword, delete_data, 1.0.0_import')
        elif command == 'chpassword':
            change_password()
        elif command == 'delete_data':
            delete_data()
        elif command == '1.0.0_import':
            db_dir, is_cancelled = enter_dir(True)
            if not is_cancelled:
                import_db(db_dir, '1.0.0')
                database.save()
            else:
                print('Cancelled.')
        else:
            print(f'No such command "{command}".')

    database.save()
    save_password(load_password()) # updates encryption


def help_function() -> None:
    """Print help for each command."""
    # show
    print('\033[31mshow\033[0m')
    print('Show database content. Usage: show [i: int], i - how many results to show at one time.')
    print('You can type "b" to go to the previous page.')
    # search
    print('\033[31msearch\033[0m')
    print('Search in database by word. Usage: search [query: str] [i: float], query - what to search for, i - indicator of similarity.')
    # new
    print('\033[31mnew\033[0m')
    print('Create new data cell with information. Usage: new.')
    print('Note: you can press do "Tab <n: int>" when filling in password field. This will create a good password of n signs. (Default length: 10.)')
    # edit
    print('\033[31medit\033[0m')
    print('Edit data cell (cell is defined by ID). Usage: edit.')
    # delete
    print('\033[31mdelete\033[0m')
    print('Delete data cell (cell is defined by ID). Usage: delete.')
    # export
    print('\033[31mexport\033[0m')
    print('Export database as .xlsx or .json file to folder user gives. Usage: export.')
    print('Note: .json will be 1.0.0 file format.')
    # save
    print('\033[31msave\033[0m')
    print('Save database. Usage: save.')
    # exit
    print('\033[31mexit\033[0m')
    print('ALWAYS run this command when you want to exit an app, otherwise database won\'t be updated. Usage: exit.')
    # admin
    print('\033[31madmin\033[0m')
    print('Shows administration commands:')
    # chpassword
    print('  \033[31mchpassword\033[0m')
    print('  Change password to enter this app. Usage: chpassword.')
    # delete_data
    print('  \033[31mdelete_data\033[0m')
    print('  Delete database and all password. Usage: delete_data.')
    # 1.0.0_import
    print('  \033[31m1.0.0_import\033[0m')
    print('  Allows to import .json database from 1.0.0 version of program. Usage: 1.0.0_import.')
    # note
    print()
    print('Note: sometimes you can enter "x" to cancel.')


def initialize() -> None:
    """Create all files, setup password."""
    new = ''
    while new == '':
        new = input('Create password to enter an app: ')
        if new == '':
            print('Password field can\'t be empty.')
    save_password(new)
    # do not create new file if there is already one (might be with password)
    if not path.exists(DB_PATH):
        _ = Database(db_path=DB_PATH, key_path=DB_KEY_PATH)
        _.initialize()


def check_for_data() -> None:
    """Check if there are any passwords, if not - init()."""
    if any([not path.exists(PF_PATH), not path.exists(KEY_PATH)]) and any([path.exists(DB_PATH), path.exists(DB_KEY_PATH)]):
        exit() # don't load password - a weak proof from password deletion thing
    if path.exists(PF_PATH) and path.exists(KEY_PATH) and path.exists(DB_PATH):
        p = load_password()
        if not p:
            initialize()
    else:
        initialize()


def load_password() -> str:
    """Load and encode password from data.dat."""
    with open(KEY_PATH, "rb") as file:
        key = file.readline()
    cipher = Fernet(key)
    with open(PF_PATH, "rb") as file:
        encrypted_data = file.readline()
    return cipher.decrypt(encrypted_data).decode()


def save_password(x: str) -> None:
    """Encode and save password to data.dat."""
    key = Fernet.generate_key()
    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(x.encode())
    with open(PF_PATH, "wb") as file:
        file.write(encrypted_data)
    with open(KEY_PATH, "wb") as file:
        file.write(key)


def log_in() -> None:
    """Enter a password to open an app."""
    password = load_password()
    input_password = getpass('Enter password: ')
    while input_password not in [password, 'x', 'X']:
        input_password = getpass('Enter password: ')
    if input_password in ['x', 'X']:
        exit()


def change_password() -> None:
    """Update password of the app."""
    print('Changing app password.')
    password = load_password()
    p = input('Enter old password: ')
    if p != password:
        print('Wrong password. Cancelled.')
        return
    new = input('Enter new password: ')
    if not new:
        print('Password field can\'t be empty.')
    confirm = input('Confirm new password: ')
    if new != confirm:
        print('Passwords don\'t match.')
        return
    save_password(new)
    print('Password changed!')


def delete_data() -> None:
    """Delete database and key."""
    print('Warning! Do you really want to delete all data?')
    print('Enter "Yеs, I\'m sure"') # I use Russian e to prevent user from copy-paste
    n = input()
    if n != 'Yes, I\'m sure':
        print('Cancelled.')
        return
    
    os.remove(PF_PATH)
    os.remove(KEY_PATH)
    os.remove(DB_PATH)
    os.remove(DB_KEY_PATH)
    os.rmdir(os.path.dirname(DB_PATH))
    print('Successfully deleted all data.')
    print('Hit "Enter" to exit.')
    input()
    exit()


def search(cmd: str) -> None:
    """Search for something in database. Result will be printed."""
    cwords = cmd.split()
    if len(cwords) == 1:
        print('Empty search query.')
        return
    if len(cwords) > 2:
        query = ' '.join(cwords[1:-1])
        try:
            i = float(cwords[-1])
        except ValueError:
            i = 0.5
        else:
            if not (0.0 <= i <= 1.0):
                print('Incorrect value of i (accuracy).')
                return
    elif len(cwords) == 2:  # search q ... q
        query = ' '.join(cwords[1:])
        i = 0.5

    print(f'Searching for "{query}" with {round(i*100, 1)}% accuracy.')
    search_results = database.search_db(query, i)
    print(f'Found {len(search_results)} matches.')
    for cell in search_results:
        print_cell(cell, True)


def enter_dir(file_exists: bool=False) -> tuple:
    """Enter directory. do_file_exist: is it obligatory that file exists. Returns: (dir, is_cancelled)"""
    directory = ''
    while not path.isdir(path.dirname(directory)):
        directory = input('Enter directory: ')
        if directory.lower() == 'x':
            return '', True
        elif not path.isdir(path.dirname(directory)):
            print('Wrong directory!')
        if file_exists and not path.exists(directory):
            print('Wrong directory!')
    return directory, False


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
    """Create a string of random letters (uppercase and lowercase), numbers and special characters."""
    if length < 6: # length too min to create reliable password
        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(choice(characters) for _ in range(length))
        return password
    # 1/6 - punctuation, 2/6 - digits, 3/6 - letters
    punctuation_amount = length // 6
    dig_amount = length // 6 * 2
    let_amount = length - punctuation_amount - dig_amount
    to_build_from = [choice(string.punctuation) for _ in range(punctuation_amount)] + [choice(string.digits) for _ in range(dig_amount)] + [choice(string.ascii_lowercase) for _ in range(let_amount//2)] + [choice(string.ascii_uppercase) for _ in range(let_amount - let_amount//2)]
    password = ''
    for _ in range(length):
        l = choice(to_build_from)
        password += l
        to_build_from.remove(l)
    return password


def parse_int(s: str, default_value: int) -> int:
    """Get integer from end of a string. If number < 1 - returns default value."""
    if bool(re.search(r'\d', s)):  # digit in s
        try:
            number =  int(s.split()[-1])
        except Exception:
            return default_value
        if number < 1:
            return default_value
        return number
    return default_value


def new_cell() -> DataCell:
    """Create a new data cell."""
    x = {}
    cell_content = ['name', 'link', 'login', 'email', 'password', 'other_data', 'codes']
    max_len = len(max(cell_content, key=len))
    for i in cell_content:
        to_show = f"{i.replace('_', ' ')}: {' '*(max_len-len(i))}"
        x[i] = input(to_show)
        if i == 'password' and x[i].startswith('\t'): # tab - generate password
            n = parse_int(x[i], 10)
            password = gen_password(n)
            x[i] = password
            print(f'\033[1;30m{to_show}{password}\033[0m')
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
    """Print database. psize cells on one page."""
    if not database.data_cells:
        print('Database is empty.')
        return
    page_amount = len(database.data_cells) // psize + bool(len(database.data_cells) % psize)
    page = 0 # start from 0
    while 0 <= page <= page_amount:
        print(f'{len(database.data_cells)} entries')
        is_prev_page = False
        if page == page_amount: # last page
            cells = database.data_cells[page_amount*psize:] # these cells will be printed
        else:
            cells = database.data_cells[page*psize:(page+1)*psize]
        for cell in cells:
            print_cell(cell, True)

        if page != page_amount:
            print(f'[{page + 1}/{page_amount}]')
            n = input('...')
            if n.lower() == 'x': # cancel viewing DB
                return
            is_prev_page = bool(n.lower() == 'b')
            os.system('cls')
            print(f'> {command}')
        if not is_prev_page:
            page += 1
        else: # previous page is selected
            page -= 1


def import_db(db_path: str, version: str) -> None:
    """Import database from previous versions of psm."""
    versions = ['1.0.0']
    if version not in versions:
        print(f'Wrong version {version}')
        return
    if version == '1.0.0': # unencrypted .json database
        try:
            with open(db_path) as f:
                data = json.load(f)
        except json.decoder.JSONDecodeError:
            print('Unable to load file.')
            return
        database.save()
        db_json = database.get_json()
        db_json.extend(data)
        database.load(db_json)
        print('Successfully imported DB v 1.0.0!')


def choose_from(x: list, text: str='value') -> tuple:
    """Choose value from a list. Returns: (str, is_cancelled)"""
    print(x)
    val = ''
    while val not in x:
        val = input(f'Enter {text}: ')
        if val.lower() == 'x':
            return '', True
    return val, False


# main() # DEBUG

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('A program error has occurred:')
        print(e)
        input()

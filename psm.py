import os
from os import path
import pandas
from database import Database, DataCell
import re
import pickle


def main() -> None:
    PSM_VERSION = '1.0.0'
    global pf_path
    pf_path = 'data.bin'
    global db_path
    db_path = path.join('data', 'database.json')
    os.chdir(path.dirname(path.realpath(__file__)))
    check_for_data()
    log_in()
    global database
    database = Database()
    database.load()

    command = ''
    os.system('cls')
    print(f'PSM version {PSM_VERSION}')
    while True:
        print('Commands: help, show [int], search [str] [int], new, edit, delete, export, chpassword, exit.')
        command = input('> ')
        os.system('cls')
        print(f'> {command}')
        if command == 'help':
            help_function()
            print()
        elif command.startswith('show'):
            number = find_number(command)
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
            savepath, is_cancelled = enter_path()
            if not is_cancelled:
                export_data(savepath)
                print('Exported!')
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
    print('Search in database by word. Usage: search [query: str] [i: int], query - what to search for, i - how many results to show.')
    # new
    print('\033[31mnew\033[0m')
    print('Create new data cell with information. Usage: new.')
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
    if not path.exists(db_path):
        if not path.exists('data'):
            os.mkdir('data')
        with open(db_path, 'w') as db_file:
            db_file.write('[]')


def check_for_data() -> None:
    """Check if there are any passwords, if not - init()."""
    if path.exists(pf_path) and path.exists(db_path):
        p = get_password()
        if not p:
            init()
    else:
        init()


def get_password() -> str:
    """Read and encode password from file."""
    pf = open(pf_path, 'rb')
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
    with open(pf_path, 'wb') as pf:
        pickle.dump(x, pf)


def log_in() -> None:
    """Enter a password to open an app."""
    password = get_password()
    input_password = input('Enter password: ')
    while input_password != password:
        input_password = input('Enter password: ')


def change_password() -> None:
    """Update password of the app."""
    print('Changing app password.')
    password = get_password()
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
    if len(cwords) > 2 and cwords[-1].isnumeric():  # search q ... 7
        query = ' '.join(cwords[1:-1])
        n = int(cwords[-1])
    elif len(cwords) > 2:  # search q ... q
        query = ' '.join(cwords[1:])
        n = 3
    else:  # search q
        query = cwords[1]
        n = 3
    if n == 0:
        print('Incorrect usage.')
        return
    search_results = database.search_db(query, n)
    print(f'Searching for {query}')
    for i in search_results[:n]:
        print_cell(i, True)


def find_number(s: str) -> int:
    """Find number in a string."""
    if bool(re.search(r'\d', s)):  # digit in s
        return int(s.split()[1])
    else:
        return 2


def enter_path() -> tuple:
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


def new_cell() -> DataCell:
    """Create a new data cell."""
    x = {}
    cell_content = ['name', 'link', 'login', 'email', 'password', 'other_data', 'codes']
    max_len = len(max(cell_content, key=len))
    for i in cell_content:
        x[i] = input(i.replace('_', ' ')+': '+' '*(max_len-len(i)))
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
                input('...')
                os.system('cls')
                print(f'> {command}')
    print()


def export_data(output_path: str) -> None:
    """Export data as excel file to directory user gives."""
    pandas.read_json(path.join('data', 'database.json')).to_excel(path.join(output_path, 'passwords.xlsx'), header=[
        'Resource', 'Link', 'Login', 'Email', 'Password', 'Other data', 'Codes', 'ID in database'], index=False)


if __name__ == '__main__':
    main()

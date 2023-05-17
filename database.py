import json
from cryptography.fernet import Fernet
from os import path, mkdir
import difflib
from copy import deepcopy
import pandas as pd


class DataCell:
    """Class to interact with data."""
    # items: name link login email password other_data codes id
    def __init__(self, x: dict):
        self.name = x.get('name', '')
        self.link = x.get('link', '')
        self.login = x.get('login', '')
        self.email = x.get('email', '')
        self.password = x.get('password', '')
        self.other_data = x.get('other_data', '')
        self.codes = x.get('codes', '')
        self.id = x.get('id', None)
    
    def update(self, elem: str, value: str) -> None:
        """Update any value (except id)"""
        if elem == 'name':
            self.name = value
        elif elem == 'link':
            self.link = value
        elif elem == 'login':
            self.login = value
        elif elem == 'email':
            self.email = value
        elif elem == 'password':
            self.password = value
        elif elem == 'other_data':
            self.other_data = value
        elif elem == 'codes':
            self.other_data = value
        else:
            print('Incorrect element: ', elem)


class Database:
    """Class that holds all DataCells."""
    def __init__(self, db_path: str=path.join('data', 'database.dat'), key_path: str=path.join('data', 'key.dat')):
        self.data_cells = []
        global DB_PATH
        DB_PATH = db_path
        global DB_KEY_PATH
        DB_KEY_PATH = key_path
        self.export_formats = ['xlsx', 'json']
    
    def get_json(self) -> list:
        """Get JSON dictionary of database."""
        with open(DB_KEY_PATH, 'r') as key_file:
            key = key_file.readline()
        cipher = Fernet(key)
        with open(DB_PATH, 'rb') as data_file:
            data_encoded =  data_file.readline()
            data_s = cipher.decrypt(data_encoded).decode()
        data_json = json.loads(data_s)
        return data_json

    def load(self, data_json: None) -> None:
        """Create list of DataCell objects loaded from JSON. DB can be loaded from custom JSON, data_json=my_dict."""
        if data_json == None:
            data_json = self.get_json()
        
        self.data_cells = [DataCell(i) for i in data_json]
        self.sort_cells()
    
    def initialize(self) -> None:
        """Initialize database: create files & key."""
        if not path.exists(path.dirname(DB_PATH)):
            mkdir(path.dirname(DB_PATH))
        key = Fernet.generate_key()
        cipher = Fernet(key)
        placeholder = cipher.encrypt(bytes('[]'.encode()))
        with open(DB_KEY_PATH, 'wb') as key_file:
            key_file.write(key)
        with open(DB_PATH, 'wb') as data_file:
            data_file.write(placeholder)

    def save(self) -> None:
        """Save data to file."""
        list_of_dicts = []
        for i in self.data_cells: # convert data from class objects to dictionaries
            cell = {
                "name": i.name,
                "link": i.link,
                "login": i.login,
                "email": i.email,
                "password": i.password,
                "other_data": i.other_data,
                "codes": i.codes,
                "id": i.id
            }
            list_of_dicts.append(cell)
        
        with open(DB_KEY_PATH, 'r') as key_file:
            key = key_file.readline()
        cipher = Fernet(key)
        bytes_data = bytes(json.dumps(list_of_dicts).encode())
        encrypted_data = cipher.encrypt(bytes_data)
        with open(DB_PATH, 'wb') as data_file:
            data_file.write(encrypted_data)

    def sort_cells(self) -> None:
        """Sort database by source names"""
        self.data_cells.sort(key=lambda x: x.name)

    def gen_id(self) -> int:
        """Generate valid id for element."""
        # fetch already existing ones
        ids = self.ids()
        if not ids:
            return 0
        # fill holes
        if min(ids) > 0: # if ... x1, x2, x3 indexes exist
            return min(ids) -1
        else:
            for i in range(len(ids)-1):
                if ids[i+1] != ids[i] + 1:
                    return ids[i] + 1
        return max(ids) + 1 # new one
    
    def rm(self, id: int) -> None:
        """Deletes data cell from database via id."""
        cell = self.find_cell(id)
        self.data_cells.remove(cell)
    
    def ids(self) -> list:
        """Get sorted list of all existing ID's."""
        return sorted([i.id for i in self.data_cells])

    def update(self, cell: DataCell) -> None:
        """Add new cell (already filled) to database."""
        if cell.id in self.ids():
            self.rm(cell.id)
        self.data_cells.append(cell)

    def find_cell(self, id: int) -> DataCell:
        """Find data cell by ID."""
        for i in self.data_cells:
            if i.id == id:
                return i
    
    def search_db(self, q: str, x: float=0.8) -> list:
        """Search DB for matching things. x - indicator of similarity. Returns list with DataCells."""
        result = []
        q = q.lower()
        temp = deepcopy(self.data_cells)
        names = [i.name.lower() for i in temp]
        links = [i.link.lower() for i in temp]
        logins = [i.login.lower() for i in temp]
        passwords = [i.password.lower() for i in temp]
        other_datas = [i.other_data.lower() for i in temp]
        codes_paths = [i.codes.lower() for i in temp]
        everything = names + links + logins + passwords + other_datas + codes_paths
        match_result = difflib.get_close_matches(q, everything, cutoff=x)
        for i in temp:
            if (i.name.lower() or i.link.lower() or i.login.lower() or i.password.lower() or i.other_data.lower() or i.codes.lower()) in match_result:
                result.append(i)
        return result

    def export_db(self, output_dir: str, export_format: str='xlsx') -> None:
        """Export database in a convenient format."""
        if export_format not in self.export_formats:
            print(f'Format {export_format} is not in available lists.')
            return
        data_json = self.get_json()
        filename = 'database.' + export_format
        index = 1
        while path.exists(path.join(output_dir, filename)): # find name that is not already taken
                filename = f'database ({index}).' + export_format
                index += 1
        if export_format == 'xlsx':
            df = pd.DataFrame(data_json)
            df.to_excel(path.join(output_dir, filename), header=['Resource', 'Link', 'Login', 'Email', 'Password', 'Other data', 'Codes', 'ID in database'], index=False)
        
        elif export_format == 'json':
            with open(path.join(output_dir, filename), 'w') as f:
                json.dump(data_json, f, indent=4)
        
        print(f'Exported as "{filename}"!')


if __name__ == '__main__':
    print("The database library file cannot be started.")
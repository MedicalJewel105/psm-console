import json
from os import path
import difflib
from copy import deepcopy


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
    def __init__(self):
        self.data_cells = []
    
    def load(self, path: str=path.join('data', 'database.json')):
        """Create list of DataCell objects loaded from JSON."""
        with open(path, 'r') as data:
            data_json = json.load(data)
        self.data_cells = [DataCell(i) for i in data_json]
        self.sort_cells()
    
    def save(self, path: str=path.join('data', 'database.json')):
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
        
        with open(path, 'w') as data:
            json.dump(list_of_dicts, data, indent=4)

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

if __name__ == '__main__':
    print("The database library file cannot be started.")
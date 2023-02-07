from PySide6.QtWidgets import QApplication, QWidget
import json
import sys


def main() -> None:
    check_for_data()
    log_in()
    load_data()
    launch_ui()
    pass

def check_for_data():
    # check if there are any passwords, if not - run init()
    pass

def log_in():
    # enter a password to open an app
    pass

def launch_ui() -> None:
    # launch ui, all interactions somewhere here
    app = QApplication(sys.argv)

    window = QWidget()
    window.show()

    app.exec()

def load_data() -> None:
    # load data from file
    pass

def export_data() -> None:
    # export data as excel file to directory user gives
    pass

if __name__ == '__main__':
    main()
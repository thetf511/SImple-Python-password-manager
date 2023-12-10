from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QFormLayout
import json
import os

class ConfigManager:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.master_password_key = 'master_password'
        self.config_data = {}

        if os.path.exists(self.config_file):
            self.load_config()
        else:
            self.create_config()

    def load_config(self):
        with open(self.config_file, 'r') as file:
            self.config_data = json.load(file)

    def create_config(self):
        master_password = input('Create a master password: ')
        self.config_data[self.master_password_key] = master_password
        self.save_config()

    def save_config(self):
        with open(self.config_file, 'w') as file:
            json.dump(self.config_data, file)

    def get_master_password(self):
        return self.config_data.get(self.master_password_key, '')

class PasswordManager:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.master_password = self.config_manager.get_master_password()
        self.data_file = 'passwords.json'
        self.key = None
        self.data = {}

        if os.path.exists(self.data_file):
            with open(self.data_file, 'rb') as file:
                encrypted_data = file.read()
            self.load_data(encrypted_data)
        else:
            self.create_data_file()

    def generate_key(self):
        return os.urandom(32)

    def encrypt_data(self, data):
        key = self.generate_key()
        encrypted_data = key + data.encode()
        return encrypted_data

    def decrypt_data(self, encrypted_data):
        key = encrypted_data[:32]
        decrypted_data = encrypted_data[32:].decode()
        return decrypted_data

    def load_data(self, encrypted_data):
        try:
            self.key = self.generate_key()
            decrypted_data = self.decrypt_data(encrypted_data)
            self.data = json.loads(decrypted_data)
        except Exception as e:
            print(f"Error loading data: {e}")
            self.data = {}

    def save_data(self):
        try:
            encrypted_data = self.encrypt_data(json.dumps(self.data))
            with open(self.data_file, 'wb') as file:
                file.write(encrypted_data)
        except Exception as e:
            print(f"Error saving data: {e}")

    def add_password(self, website, username, password):
        if website not in self.data:
            self.data[website] = {}
        self.data[website][username] = password
        self.save_data()

    def get_passwords(self):
        return self.data

class PasswordManagerGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.password_manager = PasswordManager()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.edit_website = QLineEdit()
        self.edit_username = QLineEdit()
        self.edit_password = QLineEdit()
        self.edit_password.setEchoMode(QLineEdit.Password)

        form_layout.addRow('Website:', self.edit_website)
        form_layout.addRow('Username:', self.edit_username)
        form_layout.addRow('Password:', self.edit_password)

        layout.addLayout(form_layout)

        button_save = QPushButton('Save Password')
        button_save.clicked.connect(self.save_password)

        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(['Website', 'Username', 'Password'])

        passwords = self.password_manager.get_passwords()
        for website, credentials in passwords.items():
            for username, password in credentials.items():
                row_position = table.rowCount()
                table.insertRow(row_position)
                table.setItem(row_position, 0, QTableWidgetItem(website))
                table.setItem(row_position, 1, QTableWidgetItem(username))
                table.setItem(row_position, 2, QTableWidgetItem(password))

        layout.addWidget(table)
        layout.addWidget(button_save)

        self.setLayout(layout)
        self.setWindowTitle('Password List')

    def save_password(self):
        # Master password verification
        master_password_input = self.get_master_password_from_user()
        if master_password_input == self.password_manager.master_password:
            website = self.edit_website.text()
            username = self.edit_username.text()
            password = self.edit_password.text()

            if not website or not username or not password:
                QMessageBox.warning(self, 'Error', 'Please enter Website, Username, and Password.')
                return

            self.password_manager.add_password(website, username, password)

            table = self.findChild(QTableWidget)
            table.setRowCount(0)

            passwords = self.password_manager.get_passwords()
            for website, credentials in passwords.items():
                for username, password in credentials.items():
                    row_position = table.rowCount()
                    table.insertRow(row_position)
                    table.setItem(row_position, 0, QTableWidgetItem(website))
                    table.setItem(row_position, 1, QTableWidgetItem(username))
                    table.setItem(row_position, 2, QTableWidgetItem(password))

            self.edit_website.clear()
            self.edit_username.clear()
            self.edit_password.clear()
        else:
            QMessageBox.warning(self, 'Error', 'Incorrect master password.')

    def get_master_password_from_user(self):
        app = QApplication([])

        master_password_input = QLineEdit()
        master_password_input.setEchoMode(QLineEdit.Password)

        ok_button = QPushButton('OK')
        ok_button.clicked.connect(app.quit)

        layout = QVBoxLayout()
        layout.addWidget(QLabel('Enter master password:'))
        layout.addWidget(master_password_input)
        layout.addWidget(ok_button)

        window = QWidget()
        window.setLayout(layout)
        window.setWindowTitle('Master Password Input')
        window.show()

        app.exec_()

        return master_password_input.text()


if __name__ == '__main__':
    app = QApplication([])

    window = PasswordManagerGUI()
    window.show()

    app.exec_()

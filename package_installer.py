import sys
import subprocess
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QListWidget, QMessageBox, QTextEdit, QFileDialog, QProgressBar, QPlainTextEdit, QHBoxLayout, QMenuBar, QAction
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class InstallerThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(int)
    output = pyqtSignal(str)

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                self.output.emit(output.strip())

        # قراءة stderr لعرض الأخطاء
        stderr_output = process.stderr.read()
        if stderr_output:
            self.output.emit(stderr_output.strip())

        returncode = process.wait()  # انتظر حتى ينتهي
        self.finished.emit(returncode)

class PackageInstaller(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Package Installer')
        self.setGeometry(100, 100, 600, 400)
        self.setWindowIcon(QIcon("icon.png"))  # إضافة أيقونة للنوافذ

        # إنشاء قائمة منسدلة
        menubar = QMenuBar(self)
        file_menu = menubar.addMenu('File')
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        self.label = QLabel('Enter package name or path:', self)
        self.entry = QLineEdit(self)
        self.install_button = QPushButton('Install', self)
        self.remove_button = QPushButton('Remove', self)
        self.browse_button = QPushButton('Browse', self)
        self.solve_problem_button = QPushButton('Solve Problem')  # زر حل المشكلة
        self.package_list = QListWidget(self)
        self.details_box = QTextEdit(self)
        self.details_box.setReadOnly(True)
        self.progress_bar = QProgressBar(self)
        self.output_box = QPlainTextEdit(self)
        self.output_box.setReadOnly(True)

        # إضافة أيقونات للأزرار
        self.install_button.setIcon(QIcon("install_icon.png"))
        self.remove_button.setIcon(QIcon("remove_icon.png"))
        self.browse_button.setIcon(QIcon("browse_icon.png"))
        self.solve_problem_button.setIcon(QIcon("solve_icon.png"))

        self.install_button.clicked.connect(self.confirm_install_package)
        self.remove_button.clicked.connect(self.confirm_remove_package)
        self.browse_button.clicked.connect(self.browse_file)
        self.solve_problem_button.clicked.connect(self.solve_problem)  # ربط زر حل المشكلة
        self.package_list.itemClicked.connect(self.show_details)

        layout = QVBoxLayout()
        layout.addWidget(menubar)  # إضافة القائمة المنسدلة
        layout.addWidget(self.label)
        layout.addWidget(self.entry)
        
        # إضافة زر حل المشكلة
        layout.addWidget(self.solve_problem_button)
        
        layout.addWidget(self.browse_button)
        layout.addWidget(self.install_button)
        layout.addWidget(self.remove_button)
        layout.addWidget(QLabel('Available Packages:', self))
        layout.addWidget(self.package_list)
        layout.addWidget(QLabel('Package Details:', self))
        layout.addWidget(self.details_box)
        layout.addWidget(QLabel('Terminal Output:', self))  # عنوان للطرفية
        layout.addWidget(self.output_box)  # منطقة عرض المخرجات
        layout.addWidget(QLabel('Progress:', self))  # عنوان لشريط التقدم
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)
        self.load_packages()

    def load_packages(self):
        try:
            result = subprocess.run(["pacman", "-Ss"], capture_output=True, text=True, check=True)
            packages = result.stdout.splitlines()
            self.package_list.addItems([pkg.split(' ')[0] for pkg in packages if pkg])
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"Failed to load packages: {e.stderr}")

    def show_details(self, item):
        package_name = item.text()
        try:
            result = subprocess.run(["pacman", "-Qi", package_name], capture_output=True, text=True, check=True)
            self.details_box.setPlainText(result.stdout)
        except subprocess.CalledProcessError as e:
            self.details_box.setPlainText(f"Failed to retrieve package details: {e.stderr}")

    def confirm_install_package(self):
        package_name = self.entry.text()
        if package_name.endswith('.pkg.tar.zst'):
            self.confirm_action(f"Are you sure you want to install the local package '{package_name}'?", 
                                lambda: self.install_local_package(package_name))
        else:
            self.confirm_action(f"Are you sure you want to install the package '{package_name}'?", 
                                lambda: self.install_remote_package(package_name))

    def confirm_remove_package(self):
        package_name = self.entry.text()
        self.confirm_action(f"Are you sure you want to remove the package '{package_name}'?", 
                            lambda: self.remove_package(package_name))

    def confirm_action(self, message, action):
        reply = QMessageBox.question(self, 'Confirm Action', message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            action()

    def install_remote_package(self, package_name):
        if package_name:
            command = ["sudo", "pacman", "-S", package_name, "--noconfirm"]  # إضافة --noconfirm لتجنب الحاجة للموافقة
            self.run_command(command)

    def install_local_package(self, package_path):
        if os.path.isfile(package_path):
            command = ["sudo", "pacman", "-U", package_path, "--noconfirm"]  # إضافة --noconfirm لتجنب الحاجة للموافقة
            self.run_command(command)
        else:
            QMessageBox.critical(self, "Error", "Invalid package file.")

    def run_command(self, command):
        self.progress_bar.setValue(0)
        self.output_box.clear()
        self.thread = InstallerThread(command)
        self.thread.output.connect(self.update_output)
        self.thread.finished.connect(self.on_finished)
        self.thread.start()

    def update_output(self, text):
        self.output_box.appendPlainText(text)

    def on_finished(self, returncode):
        if returncode == 0:
            QMessageBox.information(self, "Success", "Operation completed successfully!")
            self.load_packages()  # Reload package list
        else:
            QMessageBox.critical(self, "Error", "Operation failed. Please check the output for details.")

    def remove_package(self, package_name):
        if package_name:
            command = ["sudo", "pacman", "-R", package_name, "--noconfirm"]  # إضافة --noconfirm لتجنب الحاجة للموافقة
            self.run_command(command)

    def browse_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Package File", "", "Package Files (*.pkg.tar.zst);;All Files (*)", options=options)
        if file_name:
            self.entry.setText(file_name)

    def solve_problem(self):
        command = ["sudo", "rm", "/var/lib/pacman/db.lck"]
        self.run_command(command)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    installer = PackageInstaller()
    installer.show()
    sys.exit(app.exec_())

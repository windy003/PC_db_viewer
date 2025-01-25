import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
                           QFileDialog, QComboBox, QMessageBox, QLabel, QDialog, QTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import sqlite3
import os

class ContentDialog(QDialog):
    def __init__(self, content, parent=None):
        super().__init__(parent)
        self.setWindowTitle('内容详情')
        self.setWindowFlags(Qt.Window)  # 设置为独立窗口
        
        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlainText(str(content))
        
        layout.addWidget(self.text_edit)
        self.setLayout(layout)
        
        # 设置对话框大小为屏幕大小
        screen = QApplication.desktop().screenGeometry()
        self.resize(screen.width(), screen.height())

class DBBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('数据库浏览器 v2025/1/25-02')
        self.setGeometry(100, 100, 800, 600)
        
        # 设置应用图标
        icon_path = self.get_resource_path('icon.ico')  # 假设图标文件名为icon.ico
        self.setWindowIcon(QIcon(icon_path))
        
        # 添加最后打开的路径变量
        self.last_directory = ''
        
        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 创建布局
        layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        
        # 创建控件
        self.open_button = QPushButton('打开数据库(&O)')
        self.table_label = QLabel('选择表格(&T):')
        self.table_combo = QComboBox()
        self.table_widget = QTableWidget()
        
        # 添加显示当前数据库名的标签
        self.db_name_label = QLabel('当前数据库: 未打开')
        
        # 设置标签的伙伴控件
        self.table_label.setBuddy(self.table_combo)
        
        # 添加控件到布局
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.table_label)
        button_layout.addWidget(self.table_combo)
        layout.addWidget(self.db_name_label)  # 添加数据库名标签到布局
        layout.addLayout(button_layout)
        layout.addWidget(self.table_widget)
        
        main_widget.setLayout(layout)
        
        # 连接信号
        self.open_button.clicked.connect(self.open_database)
        self.table_combo.currentTextChanged.connect(self.show_table_content)
        self.table_widget.itemDoubleClicked.connect(self.show_content_dialog)
        
        self.conn = None
        
        # 检查是否有命令行参数（双击文件时会传入文件路径）
        if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
            self.open_database_file(sys.argv[1])
        
    def get_resource_path(self, relative_path):
        """获取资源文件的绝对路径"""
        try:
            # PyInstaller创建临时文件夹,将路径存储在_MEIPASS中
            base_path = sys._MEIPASS
        except Exception:
            # 如果不是打包后的环境，就使用当前目录
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, relative_path)
        
    def open_database_file(self, file_path):
        """打开指定路径的数据库文件"""
        try:
            self.conn = sqlite3.connect(file_path)
            self.last_directory = file_path
            self.load_tables()
            self.db_name_label.setText(f'当前数据库: {os.path.basename(file_path)}')  # 更新数据库名标签
        except sqlite3.Error as e:
            QMessageBox.critical(self, '错误', f'无法打开数据库：{str(e)}')

    def open_database(self):
        initial_path = self.last_directory if self.last_directory else ''
        file_name, _ = QFileDialog.getOpenFileName(
            self, 
            '选择数据库文件', 
            initial_path,
            'SQLite数据库文件 (*.db)'
        )
        if file_name:
            self.open_database_file(file_name)
        
    def load_tables(self):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            self.table_combo.clear()
            for table in tables:
                self.table_combo.addItem(table[0])
                
    def show_table_content(self, table_name):
        if not table_name or not self.conn:
            return
            
        cursor = self.conn.cursor()
        
        # 获取表格结构
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        # 获取表格数据
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        # 设置表格
        self.table_widget.setColumnCount(len(columns))
        self.table_widget.setRowCount(len(rows))
        
        # 设置表头
        headers = [column[1] for column in columns]
        self.table_widget.setHorizontalHeaderLabels(headers)
        
        # 填充数据
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setToolTip(str(value))
                self.table_widget.setItem(i, j, item)
                
        self.table_widget.resizeColumnsToContents()
        
    def show_content_dialog(self, item):
        if item:
            dialog = ContentDialog(item.text(), self)
            dialog.showMaximized()
            dialog.exec_()
        
    def closeEvent(self, event):
        if self.conn:
            self.conn.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # 设置应用程序图标
    icon_path = DBBrowser.get_resource_path(DBBrowser, 'icon.ico')  # 假设图标文件名为icon.ico
    app.setWindowIcon(QIcon(icon_path))
    
    browser = DBBrowser()
    browser.showMaximized()
    sys.exit(app.exec_())

# Add dependencies
import sys
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QAction, QPainter
from PySide6.QtWidgets import (QApplication, QHeaderView, QHBoxLayout, QLabel, QLineEdit, 
                               QMainWindow, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, 
                               QWidget, QMessageBox, QInputDialog)
from PySide6.QtCharts import QChartView, QPieSeries, QChart


class Widget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.items = 0
        self.monthly_budget = None  # Initial monthly budget
        self._data = {}

        # Left Widget
        self.table = QTableWidget()
        self.table.setColumnCount(3)  # Add another column for monthly budget
        self.table.setHorizontalHeaderLabels(["Description", "Price", "Monthly Budget"])  # Modify header labels
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Chart
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        # Right Widget
        self.description = QLineEdit()
        self.price = QLineEdit()
        self.add = QPushButton("Add")
        self.clear = QPushButton("Clear")
        self.quit = QPushButton("Quit")
        self.plot = QPushButton("Plot")

        # Disabling 'Add' button initially
        self.add.setEnabled(False)

        self.right = QVBoxLayout()
        self.right.addWidget(QLabel("Description"))
        self.right.addWidget(self.description)
        self.right.addWidget(QLabel("Price"))
        self.right.addWidget(self.price)
        self.right.addWidget(self.add)
        self.right.addWidget(self.plot)
        self.right.addWidget(self.chart_view)
        self.right.addWidget(self.clear)
        self.right.addWidget(self.quit)

        # QWidget Layout
        self.layout = QHBoxLayout()

        # Set background color to dark purple
        self.setStyleSheet("background-color: #6bc9db; color: #040c52;")

        # self.table_view.setSizePolicy(size)
        self.layout.addWidget(self.table)
        self.layout.addLayout(self.right)

        # Set the layout to the QWidget
        self.setLayout(self.layout)

        # Signals and Slots
        self.add.clicked.connect(self.add_element)
        self.quit.clicked.connect(self.quit_application)
        self.plot.clicked.connect(self.plot_data)
        self.clear.clicked.connect(self.clear_table)
        self.description.textChanged[str].connect(self.check_disable)
        self.price.textChanged[str].connect(self.check_disable)

        # Prompt user for monthly budget initially
        self.prompt_monthly_budget()

    def prompt_monthly_budget(self):
        dialog = QInputDialog()
        dialog.setStyleSheet("background-color: #6A0DAD; color: #00FF00;")
        text, ok = dialog.getText(None, "Monthly Budget", "Enter your monthly budget:")
        if ok:
            try:
                self.monthly_budget = float(text)
            except ValueError:
                QMessageBox.critical(None, "Error", "Invalid input for monthly budget.")
                self.prompt_monthly_budget()

    @Slot()
    def add_element(self):
        des = self.description.text()
        price = self.price.text()

        try:
            price_float = float(price)
            if price_float > self.monthly_budget:
                print("Price exceeds monthly budget!")
                QMessageBox.warning(None, "Warning", "Price exceeds monthly budget!")
                return
            
            price_item = QTableWidgetItem(f"{price_float:.2f}")
            price_item.setTextAlignment(Qt.AlignRight)

            self.table.insertRow(self.items)
            description_item = QTableWidgetItem(des)
            budget_item = QTableWidgetItem(f"{self.monthly_budget:.2f}")

            self.table.setItem(self.items, 0, description_item)
            self.table.setItem(self.items, 1, price_item)
            self.table.setItem(self.items, 2, budget_item)

            self.description.setText("")
            self.price.setText("")

            # Update monthly budget
            self.monthly_budget -= price_float
            budget_item.setText(f"{self.monthly_budget:.2f}")

            self.items += 1
        except ValueError:
            print("That is not an invalid input:", price, "Make sure to enter a price!")

    @Slot()
    def check_disable(self, x):
        if not self.description.text() or not self.price.text() or self.monthly_budget is None:
            self.add.setEnabled(False)
        else:
            self.add.setEnabled(True)

    @Slot()
    def plot_data(self):
        # Get remaining budget
        remaining_budget = self.monthly_budget
        for i in range(self.table.rowCount()):
            price = float(self.table.item(i, 1).text())
            remaining_budget -= price

        # Add remaining budget as a separate item to the table
        remaining_item = QTableWidgetItem("Remaining Budget")
        remaining_price_item = QTableWidgetItem(f"{remaining_budget:.2f}")
        remaining_price_item.setTextAlignment(Qt.AlignRight)
        self.table.insertRow(self.items)
        self.table.setItem(self.items, 0, remaining_item)
        self.table.setItem(self.items, 1, remaining_price_item)
        self.table.setItem(self.items, 2, QTableWidgetItem())

        # Plot the pie chart with updated data
        series = QPieSeries()
        for i in range(self.table.rowCount()):
            text = self.table.item(i, 0).text()
            number = float(self.table.item(i, 1).text())
            series.append(text, number)

        chart = QChart()
        chart.addSeries(series)
        chart.legend().setAlignment(Qt.AlignLeft)
        self.chart_view.setChart(chart)

    @Slot()
    def quit_application(self):
        QApplication.quit()

    @Slot()
    def clear_table(self):
        self.table.setRowCount(0)
        self.items = 0
        self.monthly_budget = None
        self.prompt_monthly_budget()


class MainWindow(QMainWindow):
    def __init__(self, widget):
        QMainWindow.__init__(self)
        self.setWindowTitle("Tutorial")

        # Menu
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

        # Exit QAction
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.exit_app)

        self.file_menu.addAction(exit_action)
        self.setCentralWidget(widget)

    @Slot()
    def exit_app(self, checked):
        QApplication.quit()


if __name__ == "__main__":
    # Qt Application
    app = QApplication(sys.argv)
    # QWidget
    widget = Widget()
    # QMainWindow using QWidget as central widget
    window = MainWindow(widget)
    window.resize(800, 600)
    window.show()

    # Execute application
    sys.exit(app.exec())

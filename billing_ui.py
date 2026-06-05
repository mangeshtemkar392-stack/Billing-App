from datetime import datetime
from openpyxl.workbook import Workbook

from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QMessageBox,
    QComboBox, QFileDialog
)


class BillingUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Billing Software")
        self.setGeometry(300, 150, 1000, 600)

        self.sub_total = 0.0
        self.cgst_rate = 0.09
        self.sgst_rate = 0.09

        # ---------------- INPUTS ---------------- #

        self.product_input = QLineEdit()
        self.product_input.setPlaceholderText("Product Name")

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Price")

        self.qty_input = QLineEdit()
        self.qty_input.setPlaceholderText("Quantity")

        self.gst_combo = QComboBox()
        self.gst_combo.addItems(["0", "5", "12", "18", "28"])
        self.gst_combo.setCurrentText("18")
        self.gst_combo.currentTextChanged.connect(self.on_gst_change)

        # ---------------- BUTTONS ---------------- #

        self.add_btn = QPushButton("Add Item")
        self.add_btn.clicked.connect(self.add_item)

        self.remove_btn = QPushButton("Remove Selected")
        self.remove_btn.clicked.connect(self.remove_item)

        self.save_btn = QPushButton("Save TXT")
        self.save_btn.clicked.connect(self.save_bill)

        self.excel_btn = QPushButton("Save Excel")
        self.excel_btn.clicked.connect(self.save_to_excel)

        self.new_bill_btn = QPushButton("New Bill")
        self.new_bill_btn.clicked.connect(self.new_bill)

        # ---------------- TABLE ---------------- #

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(
            ["Product", "Price", "Qty", "Total"]
        )

        # ---------------- LABELS ---------------- #

        self.subtotal_label = QLabel("Subtotal: ₹0.00")
        self.cgst_label = QLabel("CGST (9%): ₹0.00")
        self.sgst_label = QLabel("SGST (9%): ₹0.00")
        self.total_label = QLabel("Grand Total: ₹0.00")

        # ---------------- LAYOUTS ---------------- #

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.product_input)
        input_layout.addWidget(self.price_input)
        input_layout.addWidget(self.qty_input)
        input_layout.addWidget(QLabel("GST %"))
        input_layout.addWidget(self.gst_combo)
        input_layout.addWidget(self.add_btn)
        input_layout.addWidget(self.remove_btn)
        input_layout.addWidget(self.save_btn)
        input_layout.addWidget(self.excel_btn)
        input_layout.addWidget(self.new_bill_btn)

        totals_layout = QVBoxLayout()
        totals_layout.addWidget(self.subtotal_label)
        totals_layout.addWidget(self.cgst_label)
        totals_layout.addWidget(self.sgst_label)
        totals_layout.addWidget(self.total_label)

        main_layout = QVBoxLayout()
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.table)
        main_layout.addLayout(totals_layout)

        self.setLayout(main_layout)

    # ---------------- GST CHANGE ---------------- #

    def on_gst_change(self):
        gst_percent = float(self.gst_combo.currentText())

        self.cgst_rate = gst_percent / 200
        self.sgst_rate = gst_percent / 200

        self.update_totals()

    # ---------------- ADD ITEM ---------------- #

    def add_item(self):
        product = self.product_input.text().strip()
        price = self.price_input.text().strip()
        qty = self.qty_input.text().strip()

        if not product or not price or not qty:
            QMessageBox.warning(self, "Error", "Fill all fields")
            return

        try:
            price = float(price)
            qty = int(qty)
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid input")
            return

        item_total = price * qty
        self.sub_total += item_total

        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, 0, QTableWidgetItem(product))
        self.table.setItem(row, 1, QTableWidgetItem(f"{price:.2f}"))
        self.table.setItem(row, 2, QTableWidgetItem(str(qty)))
        self.table.setItem(row, 3, QTableWidgetItem(f"{item_total:.2f}"))

        self.update_totals()

        self.product_input.clear()
        self.price_input.clear()
        self.qty_input.clear()
        self.product_input.setFocus()

    # ---------------- REMOVE ITEM ---------------- #

    def remove_item(self):
        row = self.table.currentRow()

        if row < 0:
            QMessageBox.warning(self, "Error", "Select item to remove")
            return

        item_total = float(self.table.item(row, 3).text())
        self.sub_total -= item_total

        self.table.removeRow(row)
        self.update_totals()

    # ---------------- UPDATE TOTALS ---------------- #

    def update_totals(self):
        cgst = self.sub_total * self.cgst_rate
        sgst = self.sub_total * self.sgst_rate
        grand_total = self.sub_total + cgst + sgst

        cgst_percent = int(self.cgst_rate * 200)
        sgst_percent = int(self.sgst_rate * 200)

        self.subtotal_label.setText(
            f"Subtotal: ₹{self.sub_total:.2f}"
        )
        self.cgst_label.setText(
            f"CGST ({cgst_percent}%): ₹{cgst:.2f}"
        )
        self.sgst_label.setText(
            f"SGST ({sgst_percent}%): ₹{sgst:.2f}"
        )
        self.total_label.setText(
            f"Grand Total: ₹{grand_total:.2f}"
        )

    # ---------------- SAVE TXT ---------------- #

    def save_bill(self):
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Error", "No items to save")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Bill",
            "Bill.txt",
            "Text Files (*.txt)"
        )

        if not file_path:
            return

        with open(file_path, "w", encoding="utf-8") as file:
            file.write("========= BILL RECEIPT =========\n")
            file.write(f"{datetime.now()}\n")
            file.write("---------------------------------\n")

            for row in range(self.table.rowCount()):
                product = self.table.item(row, 0).text()
                price = self.table.item(row, 1).text()
                qty = self.table.item(row, 2).text()
                total = self.table.item(row, 3).text()

                file.write(
                    f"{product} | ₹{price} | Qty:{qty} | ₹{total}\n"
                )

            file.write("---------------------------------\n")
            file.write(self.subtotal_label.text() + "\n")
            file.write(self.cgst_label.text() + "\n")
            file.write(self.sgst_label.text() + "\n")
            file.write(self.total_label.text() + "\n")

        QMessageBox.information(self, "Success", "Bill Saved")

    # ---------------- SAVE EXCEL ---------------- #

    def save_to_excel(self):
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Error", "No items")
            return

        default_name = f"Bill_{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.xlsx"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Excel",
            default_name,
            "Excel Files (*.xlsx)"
        )

        if not file_path:
            return

        wb = Workbook()
        ws = wb.active
        ws.title = "Bill"

        ws.append(["Product", "Price", "Qty", "Total"])

        for row in range(self.table.rowCount()):
            product = self.table.item(row, 0).text()
            price = float(self.table.item(row, 1).text())
            qty = int(self.table.item(row, 2).text())
            total = float(self.table.item(row, 3).text())

            ws.append([product, price, qty, total])

        ws.append([])
        ws.append([self.subtotal_label.text()])
        ws.append([self.cgst_label.text()])
        ws.append([self.sgst_label.text()])
        ws.append([self.total_label.text()])

        wb.save(file_path)

        QMessageBox.information(
            self,
            "Success",
            "Excel Saved"
        )

    # ---------------- NEW BILL ---------------- #

    def new_bill(self):
        reply = QMessageBox.question(
            self,
            "New Bill",
            "Clear current bill?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.No:
            return

        self.table.setRowCount(0)
        self.sub_total = 0.0
        self.update_totals()

        self.product_input.clear()
        self.price_input.clear()
        self.qty_input.clear()
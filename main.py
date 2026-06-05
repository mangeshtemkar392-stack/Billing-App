import sys
from PyQt5.QtWidgets import QApplication
from ui.billing_ui import BillingUI


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BillingUI()
    window.show()
    sys.exit(app.exec_())
import sys
import os
import requests
import json
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QTextBrowser,
    QGridLayout,
)
from PyQt6.QtCore import Qt
from dotenv import load_dotenv

# Load .env file located one directory above the script's directory
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"))


class TelegramBotWebhook(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Telegram Bot Webhook")
        self.setGeometry(100, 100, 400, 350)

        layout = QVBoxLayout()

        # Automatically fetch token and URL from the .env file
        self.token = os.getenv("BOT_TOKEN")
        self.webhook_url = os.getenv("HOME_URL")

        # If no values are found, show a message and disable the input fields
        if not self.token or not self.webhook_url:
            self.textBrowser = QTextBrowser()
            self.textBrowser.setText(
                "Error: Missing BOT_TOKEN or HOME_URL in .env file."
            )
            layout.addWidget(self.textBrowser)
            self.setLayout(layout)
            return

        # Set up the UI elements
        self.tokenEdit = QLineEdit()
        self.tokenEdit.setText(self.token)  # Pre-fill the token field
        self.tokenEdit.setEchoMode(QLineEdit.EchoMode.Normal)
        self.tokenEdit.setPlaceholderText("Telegram Bot Token")
        layout.addWidget(self.tokenEdit)

        self.urlEdit = QLineEdit()
        self.urlEdit.setText(self.webhook_url)  # Pre-fill the URL field
        self.urlEdit.setPlaceholderText("Webhook URL")
        layout.addWidget(self.urlEdit)

        gridLayout = QGridLayout()
        setButton = QPushButton("Set Webhook")
        setButton.clicked.connect(self.setWebhook)
        gridLayout.addWidget(setButton, 0, 0)

        checkButton = QPushButton("Check Webhook")
        checkButton.clicked.connect(self.checkWebhook)
        gridLayout.addWidget(checkButton, 0, 1)

        deleteButton = QPushButton("Delete Webhook")
        deleteButton.clicked.connect(self.deleteWebhook)
        gridLayout.addWidget(deleteButton, 1, 0)

        resetButton = QPushButton("Reset Pending Updates")
        resetButton.clicked.connect(self.resetPendingUpdates)
        gridLayout.addWidget(resetButton, 1, 1)

        checkTokenButton = QPushButton("Check Token")
        checkTokenButton.clicked.connect(self.checkTokenValidity)
        gridLayout.addWidget(checkTokenButton, 2, 0, 1, 2)

        layout.addLayout(gridLayout)

        self.textBrowser = QTextBrowser()
        layout.addWidget(self.textBrowser)

        self.setLayout(layout)

    def setWebhook(self):
        try:
            response = requests.post(
                f"https://api.telegram.org/bot{self.token}/setWebhook?url={self.webhook_url}"
            )
            response_data = response.json()
            if response.status_code == 200:
                if response_data.get("ok"):
                    self.textBrowser.setText("Webhook set successfully")
                    self.textBrowser.append(json.dumps(response_data, indent=4))
                else:
                    self.textBrowser.setText(
                        f"Failed to set webhook: {response_data.get('description')}"
                    )
                    self.textBrowser.append(json.dumps(response_data, indent=4))
            else:
                self.textBrowser.setText("Error setting webhook")
                self.textBrowser.append(response.text)
        except requests.exceptions.RequestException as e:
            self.textBrowser.setText("Error connecting to Telegram API")
            self.textBrowser.append(str(e))

    def checkWebhook(self):
        try:
            response = requests.post(
                f"https://api.telegram.org/bot{self.token}/getWebhookInfo"
            )
            if response.status_code == 200:
                response_data = response.json()
                self.textBrowser.setText("Webhook info")
                self.textBrowser.append(json.dumps(response_data, indent=4))
            else:
                self.textBrowser.setText("Error getting webhook info")
                self.textBrowser.append(response.text)
        except requests.exceptions.RequestException as e:
            self.textBrowser.setText("Error connecting to Telegram API")
            self.textBrowser.append(str(e))

    def deleteWebhook(self):
        try:
            response = requests.post(
                f"https://api.telegram.org/bot{self.token}/deleteWebhook"
            )
            response_data = response.json()
            if response.status_code == 200:
                if response_data.get("ok"):
                    self.textBrowser.setText("Webhook deleted successfully")
                    self.textBrowser.append(json.dumps(response_data, indent=4))
                else:
                    self.textBrowser.setText(
                        f"Failed to delete webhook: {response_data.get('description')}"
                    )
                    self.textBrowser.append(json.dumps(response_data, indent=4))
            else:
                self.textBrowser.setText("Error deleting webhook")
                self.textBrowser.append(response.text)
        except requests.exceptions.RequestException as e:
            self.textBrowser.setText("Error connecting to Telegram API")
            self.textBrowser.append(str(e))

    def resetPendingUpdates(self):
        try:
            response = requests.post(
                f"https://api.telegram.org/bot{self.token}/deleteWebhook?drop_pending_updates=true"
            )
            response_data = response.json()
            if response.status_code == 200:
                if response_data.get("ok"):
                    self.textBrowser.setText("Pending updates reset successfully")
                    self.textBrowser.append(json.dumps(response_data, indent=4))
                else:
                    self.textBrowser.setText(
                        f"Failed to reset pending updates: {response_data.get('description')}"
                    )
                    self.textBrowser.append(json.dumps(response_data, indent=4))
            else:
                self.textBrowser.setText("Error resetting pending updates")
                self.textBrowser.append(response.text)
        except requests.exceptions.RequestException as e:
            self.textBrowser.setText("Error connecting to Telegram API")
            self.textBrowser.append(str(e))

    def checkTokenValidity(self):
        try:
            response = requests.get(f"https://api.telegram.org/bot{self.token}/getMe")
            response_data = response.json()
            if response.status_code == 200 and response_data.get("ok"):
                # Pretty print the JSON response in QTextBrowser
                pretty_data = json.dumps(response_data, indent=4)
                self.textBrowser.setText(f"Bot info:\n{pretty_data}")
            else:
                self.textBrowser.setText(
                    f"Failed to authenticate the bot token.\n{response_data.get('description')}"
                )
                self.textBrowser.append(json.dumps(response_data, indent=4))
        except requests.exceptions.RequestException as e:
            self.textBrowser.setText("Error connecting to Telegram API")
            self.textBrowser.append(str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TelegramBotWebhook()
    window.show()
    sys.exit(app.exec())

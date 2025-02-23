import requests
import json

from functools import partial

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from TutorialWindow import TutorialWindow


class InitialWindow(QWidget):
    ENTRY_API = "https://usabcheck.herokuapp.com/api/localapp/"
    # ENTRY_API = "http://localhost:8090/api/localapp/"

    GET_TEST_BY_REF_CODE_ENTRY = "getTestDetailsByReferenceCode/"


    def __init__(self, parent):
        QWidget.__init__(self, None) #, Qt.WindowStaysOnTopHint)

        self.parent = parent

        # Window configurations
        self.setGeometry(400, 350, 500, 250)
        self.setWindowTitle("UsabCheck")
        self.setStyleSheet("font-size: 16px;")
        
        # Layout
        self.mainLayout = QVBoxLayout()
        self.mainLayout.setContentsMargins(20, 20, 150, 0)
        self.createTestEnterLayout()

        self.displayTestLayout = QGroupBox()
        self.beginForm = QWidget(self)
        self.setLayout(self.mainLayout)


    # Creates the first part of the form where the user enters a test reference code
    def createTestEnterLayout(self):
        layout = QFormLayout()
        
        refCodeLabel = QLabel("Test Reference Code:")
        self.refCodeInput = QLineEdit()
        self.submitBtn = QPushButton("Submit", self)
        self.submitBtn.clicked.connect(self.submitRefCode)
        self.submitBtn.resize(self.submitBtn.sizeHint())
        self.submitBtn.setStyleSheet("background-color: rgb(32, 123, 207);")
        self.submitBtn.setFixedWidth(100)

        layout.addRow(refCodeLabel)
        layout.addRow(self.refCodeInput)
        layout.addRow(self.submitBtn)
        layout.setContentsMargins(0, 0, 0, 30)

        self.mainLayout.addLayout(layout)
    

    # When the user submits the code get the data
    def submitRefCode(self, e):
        refCode = self.refCodeInput.text()
        if refCode == "":
            refCode = "H8VH1NLA"

        sendData = {"referenceCode": str(refCode)}
        request = requests.post(self.ENTRY_API + self.GET_TEST_BY_REF_CODE_ENTRY, data=sendData)
        print("#request", request)
        
        if (request.status_code != 200):
            errorMessage = "ERROR " + str(request.status_code) + ": " + request.text
            print(errorMessage)
            self.displayError(errorMessage)
        else:
            data = json.loads(request.text)
            
            if 'sequenceData' in data.keys():
                data["sequenceData"].sort(key=lambda obj: obj["sequenceNumber"], reverse=False)

                self.displayTestData(data)


    def displayError(self, errorMessage):
        self.mainLayout.removeWidget(self.displayTestLayout)
        self.mainLayout.removeWidget(self.beginForm)

        self.displayTestLayout = QWidget(self)
        self.beginForm = QWidget(self)
        layout = QFormLayout()
        layout.setSpacing(10)
        layout.addRow(QLabel(errorMessage))
        self.displayTestLayout.setLayout(layout)
        self.mainLayout.addWidget(self.displayTestLayout)

    
    # Display the data so that the user can verify that the test is correct
    def displayTestData(self, data):
        self.data = data
        self.testName = data["testName"]
        self.createdDate = data["launchedDate"]
        self.noOfTasks = 0
        self.noOfQuestions = 0

        print(data)

        # Counte the number of tasks and questions
        for item in data["sequenceData"]:
            if ("questionConfigsJSON" in item.keys()):
                self.noOfQuestions += 1
            if ("stepsJSON" in item.keys()):
                self.noOfTasks += 1

        # Remove the widget if it already exists (if the user submits another code the data is reloaded)
        self.mainLayout.removeWidget(self.displayTestLayout)
        self.mainLayout.removeWidget(self.beginForm)
        self.displayTestLayout = QGroupBox("Usability Test Details")
        layout = QFormLayout()
        layout.setSpacing(10)
        layout.addRow(QLabel("Test Name:  "), QLabel(str(self.testName)))
        layout.addRow(QLabel("Created Date:  "), QLabel(str(self.createdDate)))
        layout.addRow(QLabel("No. of Tasks:  "), QLabel(str(self.noOfTasks)))
        layout.addRow(QLabel("No. of Questions:  "), QLabel(str(self.noOfQuestions)))
        layout.addRow(QLabel("Scenario/Information:"))

        scenarioLabel = QLabel(data["scenario"])
        scenarioLabel.setFixedWidth(400)
        scenarioLabel.setWordWrap(True) 
        scenarioLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addRow(scenarioLabel)
        self.displayTestLayout.setLayout(layout)
        
        self.mainLayout.addWidget(self.displayTestLayout)
        self.displayBeginForm()

    
    def displayBeginForm(self):
        self.beginForm = QWidget(self) 

        # Form that asks the user for their info
        layout = QFormLayout()
        
        tutorialBtn = QPushButton("Open Tutorial", self)
        tutorialBtn.clicked.connect(partial(self.showTutorial))
        tutorialBtn.resize(tutorialBtn.sizeHint())
        tutorialBtn.setStyleSheet("background-color: rgb(32, 123, 207);")
        tutorialBtn.setFixedWidth(150)
        tutorialBtn.setContentsMargins(100, 100, 100, 100)

        self.userNameLabel = QLabel("Your name:")
        self.userNameInput = QLineEdit()
        self.beginBtn = QPushButton("Begin", self)
        self.beginBtn.clicked.connect(partial(self.begin))
        self.beginBtn.resize(self.beginBtn.sizeHint())
        self.beginBtn.setStyleSheet("background-color: rgb(32, 207, 76);")
        self.beginBtn.setFixedWidth(100)

        layout.addRow(tutorialBtn)
        layout.addRow(QLabel())
        layout.addRow(self.userNameLabel)
        layout.addRow(self.userNameInput)
        layout.addRow(self.beginBtn)
        layout.setContentsMargins(0, 30, 0, 30)

        self.beginForm.setLayout(layout)
        self.mainLayout.addWidget(self.beginForm)


    def begin(self):
        data = self.data
        data["participantName"] = self.userNameInput.text()
        self.parent.loadComponents(data)


    def showTutorial(self):
        self.tutorialWindow = TutorialWindow()
        self.tutorialWindow.show()
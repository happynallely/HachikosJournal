import os
import sys
import time
import random
import textwrap
import datetime
import re
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QTabWidget, QTextEdit, QGridLayout, QLabel, QListWidget, QListWidgetItem
from PyQt5.QtGui import QFont, QPixmap, QMovie, QColor
from PyQt5.QtCore import Qt, QThread, pyqtSignal # pyqtSignal is correctly imported here
from QSharpTools import SharpButton
from GoogleSentiment import getSentiment
from compliments import compliments
from motivators import motivators

endSentThread = False
documentScore = 0
documentMag = 0

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.width = 615
        self.height = 900
        screenSizeX = 1920
        screenSizeY = 1080
        self.xPos = int((screenSizeX/2) - (self.width/2))
        self.xPos -= 2000
        self.yPos = int((screenSizeY/2) - (self.height/2))
        self.sentThread = sentimentThread()
        self.initUI()
        # NOTE: The connection to the signal is REMOVED from __init__ 
        # and moved to initUI to ensure 'update_speech_label' is defined
        # and all UI elements are fully initialized.

    def initUI(self):
        self.setGeometry(self.xPos, self.yPos, self.width, self.height)
        self.setFixedSize(self.width, self.height)
        self.setWindowTitle("Stability Journal")

        windowBG = "rgb(66, 133, 129)"
        selectedColor = "rgb(33, 82, 79)"
        self.setStyleSheet(f"background-color: {windowBG}; font-size: 15px;")
        colorBG = "rgb(143, 219, 215)"
        self.tabWidget = QTabWidget()
        self.tabWidget.setStyleSheet(f"QTabBar::tab:selected {{color: white; background-color: {colorBG};}};")
        self.journalTab = QWidget()
        self.journalTab.setStyleSheet(f"background-color: {colorBG};")
        self.memoriesTab = QWidget()
        self.memoriesTab.setStyleSheet(f"background-color: {colorBG};")

        self.journalLayout = QGridLayout()
        self.journalEdit = QTextEdit()
        journalFont = QFont("Century Gothic")
        self.journalEdit.setFont(journalFont)
        self.journalEdit.setStyleSheet("background-image: url(img/linedpaper.png); background-repeat: no-repeat; background-position: center; font-size: 24px;")
        self.journalEdit.setText("Dear Self,\n\n")
        self.journalLayout.addWidget(self.journalEdit, 0, 0, 1, 4)

        self.speechLabel = QLabel()
        self.speechLabel.setText("\t    Hi! I'm Renji")
        self.speechLabel.setStyleSheet("background-image: url(img/speechbubble.png); background-repeat: no-repeat; font-size: 20px;")
        self.journalLayout.addWidget(self.speechLabel, 1, 0, 1, 3)

        self.hachikoLabel = QLabel()
        self.hachikoMovie = QMovie("img/HachikoHappyGif")
        self.hachikoLabel.setMovie(self.hachikoMovie)
        self.hachikoMovie.start()
        self.journalLayout.addWidget(self.hachikoLabel, 1, 3)

        # NOTE: SharpButton calls now work because QSharpTools.py was updated
        self.saveButton = SharpButton(primaryColor = windowBG, secondaryColor = colorBG)
        self.saveButton.setText("Save Journal")
        self.saveButton.clicked.connect(self.save)
        self.journalLayout.addWidget(self.saveButton, 2, 0)

        self.wagButton = SharpButton(primaryColor = windowBG, secondaryColor = colorBG)
        self.wagButton.setText("Wag tail!")
        self.wagButton.clicked.connect(self.wag)
        self.journalLayout.addWidget(self.wagButton, 2, 1)

        self.howlButton = SharpButton(primaryColor = windowBG, secondaryColor = colorBG)
        self.howlButton.setText("Howl!")
        self.howlButton.clicked.connect(self.howl)
        self.journalLayout.addWidget(self.howlButton, 2, 2)

        self.headTiltButton = SharpButton(primaryColor = windowBG, secondaryColor = colorBG)
        self.headTiltButton.setText("Do a head tilt!")
        self.headTiltButton.clicked.connect(self.tilt)
        self.journalLayout.addWidget(self.headTiltButton, 2, 3)

        self.journalTab.setLayout(self.journalLayout)

        self.tabWidget.addTab(self.journalTab, "Journal")
        self.tabWidget.addTab(self.memoriesTab, "Memories")
        self.setCentralWidget(self.tabWidget)

        self.memoriesLayout = QGridLayout()
        self.journalsListLabel = QLabel()
        self.journalsListLabel.setText("Past Journals")
        self.memoriesLayout.addWidget(self.journalsListLabel, 0, 0, 1, 1)

        self.openButton = SharpButton(primaryColor = windowBG, secondaryColor = colorBG)
        self.openButton.setText("Open Journal")
        self.openButton.clicked.connect(self.open)
        self.memoriesLayout.addWidget(self.openButton, 0, 3, 1, 1)

        self.journalsList = QListWidget()
        self.journalsList.setStyleSheet(f"color: rgb(193, 193, 240); background-color: rgb(0, 13, 51); selection-color: rgb(0, 13, 51); selection-background-color: rgb(193, 193, 240)")
        for journal in os.listdir("journals/"):
            item = QListWidgetItem(journal)
            if journal[-6] == "1":
                item.setBackground(QColor(57, 172, 57))
            self.journalsList.addItem(item)
        self.memoriesLayout.addWidget(self.journalsList, 1, 0, 1, 4)

        self.memoriesTab.setLayout(self.memoriesLayout)

        # NOTE: Signal connection is safely done AFTER all UI setup
        self.sentThread.speech_update.connect(self.update_speech_label) 
        
        self.sentThread.start()

        self.show()

    # NOTE: New method to safely update the GUI from the main thread
    def update_speech_label(self, text):
        self.speechLabel.setText(text)

    def save(self):
        global documentScore
        global documentMag
        savefilepath = str(datetime.datetime.now())
        savefilepath = savefilepath.replace(" ", "-")
        savefilepath = savefilepath.replace(".", "-")
        savefilepath = savefilepath.replace(":", "-")
        sentiment = "1" if documentScore > 0 and documentMag > 3 else "0"
        savefilepath = "journals/" + savefilepath + "-" + sentiment + ".jrnl"
        with open(savefilepath, "w+") as savefile:
            savefile.write(self.journalEdit.toPlainText())

    def wag(self):
        self.hachikoMovie.stop()
        self.hachikoMovie = QMovie("img/HachikoHappyGif")
        self.hachikoLabel.setMovie(self.hachikoMovie)
        self.hachikoMovie.start()

    def howl(self):
        self.hachikoMovie.stop()
        self.hachikoMovie = QMovie("img/HachikoHowlingGif")
        self.hachikoLabel.setMovie(self.hachikoMovie)
        self.hachikoMovie.start()

    def tilt(self):
        self.hachikoMovie.stop()
        self.hachikoMovie = QMovie("img/HachikoHeadTiltGif")
        self.hachikoLabel.setMovie(self.hachikoMovie)
        self.hachikoMovie.start()

    def open(self):
        currItem = self.journalsList.currentItem()
        if currItem:
            with open("journals/" + str(currItem.text()), "r") as jrnlFile:
                self.journalEdit.setText(jrnlFile.read())

class sentimentThread(QThread):
    # NOTE: Defined a signal to safely send updates to the main thread
    speech_update = pyqtSignal(str) 

    def __init__(self):
        super().__init__()

    def run(self):
        global endSentThread
        global documentScore
        global documentMag
        wrapper = textwrap.TextWrapper(width=25)
        while not endSentThread:
            time.sleep(10)
            
            # NOTE: Added try...except block to prevent crashes from network errors
            try:
                score, mag = getSentiment(myWin.journalEdit.toPlainText())
                documentScore = score
                documentMag = mag

                if score < 0 and mag > 1:
                    newText = str(random.choice(motivators))
                else:
                    newText = str(random.choice(compliments))
                
                newText = "\t" + "\n\t".join(wrapper.wrap(text = newText))
                
                # NOTE: Replaced direct GUI call (myWin.speechLabel.setText) with signal emission
                self.speech_update.emit(newText) 

            except Exception as e:
                print(f"Sentiment Analysis Error: {e}")
                default_text = "Renji needs a coffee break... Sentiment analysis failed."
                default_text = "\t" + "\n\t".join(wrapper.wrap(text = default_text))
                self.speech_update.emit(default_text) # Report error via signal
                
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = Window()
    sys.exit(app.exec_())

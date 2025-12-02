from curses import wrapper
import os
import sys
import time
import random
import textwrap
import datetime
import re
from openai import OpenAI
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QTabWidget, QTextEdit, QGridLayout, QLabel, QListWidget, QListWidgetItem
from PyQt5.QtGui import QFont, QPixmap, QMovie, QColor
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from QSharpTools import SharpButton

endSentThread = False
documentScore = 0
documentMag = 0

# Set your OpenAI API key

def get_personalized_affirmation(journal_text):
    """Generate affirmation that matches the journal content"""
    # Use the global client object defined above
    global client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    if client is None:
        return "Arf! Renji can't talk right now because the connection failed."

    # Check if the journal text is too short to be useful
    if len(journal_text.strip()) < 50:
        return "You're doing great! Keep writing down your thoughts, Renji is listening."
    
    try:
        # Use the client object and the new method call syntax
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"""You are Renji, a caring companion dog. Read this journal 
                and give a personalized 2-3 sentence affirmation that references 
                specific things they wrote. Start with 'Arf, Arf!'.
                Journal entry: "{journal_text}" """
            }]
        )
        # The result object structure has also slightly changed for accessing content
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        return "Woof woof! Renji couldn't fetch a new message right now due to an API error!"


class sentimentThread(QThread):
    speech_update = pyqtSignal(str) 

    def __init__(self):
        super().__init__()

    def run(self):  # THIS WAS THE FIX - properly indented inside class
        global endSentThread
        global documentScore
        global documentMag
        wrapper = textwrap.TextWrapper(width=25)
        
        while not endSentThread:
            time.sleep(10)
            
            newText = "Woof woof! Renji is thinking..." 
            
            try:
                score, mag = 0, 0
                documentScore = score
                documentMag = mag

                # Use personalized AI affirmation instead of random choice
                newText = get_personalized_affirmation(myWin.journalEdit.toPlainText())
                
            except Exception as e:
                print(f"Error in sentimentThread: {e}")
                newText = "Woof Woof! Renji had trouble connecting to the network."

            newText = "\t" + "\n\t".join(wrapper.wrap(text=newText))
            self.speech_update.emit(newText)


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.width = 615
        self.height = 900
        screenSizeX = 1920
        screenSizeY = 1080
        self.xPos = int((screenSizeX/2) - (self.width/2))
        self.yPos = int((screenSizeY/2) - (self.height/2))
        self.sentThread = sentimentThread()
        self.initUI()

    def initUI(self):
        self.setGeometry(self.xPos, self.yPos, self.width, self.height)
        self.setFixedSize(self.width, self.height)
        self.setWindowTitle("Stability Journal")

        windowBG = "rgb(170, 51, 106)"
        self.setStyleSheet(f"background-color: {windowBG}; font-size: 12px;")
        colorBG = "rgb(244, 194, 194)"
        
        self.tabWidget = QTabWidget()
        self.tabWidget.setStyleSheet(f"QTabBar::tab:selected {{color: white; background-color: {colorBG};}};")
        
        self.journalTab = QWidget()
        self.journalTab.setStyleSheet(f"background-color: {colorBG};")
        self.memoriesTab = QWidget()
        self.memoriesTab.setStyleSheet(f"background-color: {colorBG};")

        self.journalLayout = QGridLayout()
        self.journalEdit = QTextEdit()
        journalFont = QFont("Times New Roman", 14)
        self.journalEdit.setFont(journalFont)
        self.journalEdit.setStyleSheet("background-image: url(img/journal.png); background-repeat: no-repeat; background-position: center; font-size: 24px;")
        self.journalEdit.setText("Dear Self,\n\n")
        self.journalLayout.addWidget(self.journalEdit, 0, 0, 1, 4)

        self.speechLabel = QLabel()
        self.dogName = "Renji"
        self.speechLabel.setText(f"\t Hi! I'm {self.dogName}!")
        self.speechLabel.setStyleSheet("background-image: url(img/speechbubble.png); background-repeat: no-repeat; font-size: 20px;")
        self.journalLayout.addWidget(self.speechLabel, 1, 0, 1, 3)

        self.hachikoLabel = QLabel()
        self.hachikoMovie = QMovie("img/HachikoHappyGif")
        self.hachikoLabel.setMovie(self.hachikoMovie)
        self.hachikoMovie.start()
        self.journalLayout.addWidget(self.hachikoLabel, 1, 3)

        self.saveButton = SharpButton(primaryColor=windowBG, secondaryColor=colorBG)
        self.saveButton.setText("Save Journal")
        self.saveButton.clicked.connect(self.save)
        self.journalLayout.addWidget(self.saveButton, 2, 0)

        self.wagButton = SharpButton(primaryColor=windowBG, secondaryColor=colorBG)
        self.wagButton.setText("Happy Boy!")
        self.wagButton.clicked.connect(self.wag)
        self.journalLayout.addWidget(self.wagButton, 2, 1)

        self.howlButton = SharpButton(primaryColor=windowBG, secondaryColor=colorBG)
        self.howlButton.setText("Good Boy!")
        self.howlButton.clicked.connect(self.howl)
        self.journalLayout.addWidget(self.howlButton, 2, 2)

        self.headTiltButton = SharpButton(primaryColor=windowBG, secondaryColor=colorBG)
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

        self.openButton = SharpButton(primaryColor=windowBG, secondaryColor=colorBG)
        self.openButton.setText("Open Journal")
        self.openButton.clicked.connect(self.open)
        self.memoriesLayout.addWidget(self.openButton, 0, 3, 1, 1)

        self.journalsList = QListWidget()
        self.journalsList.setStyleSheet("color: rgb(193, 193, 240); background-color: rgb(0, 13, 51); selection-color: rgb(0, 13, 51); selection-background-color: rgb(193, 193, 240)")
        
        if os.path.exists("journals/"):
            for journal in os.listdir("journals/"):
                item = QListWidgetItem(journal)
                if journal[-6] == "1":
                    item.setBackground(QColor(57, 172, 57))
                self.journalsList.addItem(item)
        
        self.memoriesLayout.addWidget(self.journalsList, 1, 0, 1, 4)
        self.memoriesTab.setLayout(self.memoriesLayout)

        self.sentThread.speech_update.connect(self.update_speech_label)
        self.sentThread.start()
        self.show()

    def update_speech_label(self, text):
        self.speechLabel.setText(text)

    def save(self):
        global documentScore, documentMag
        savefilepath = str(datetime.datetime.now())
        savefilepath = savefilepath.replace(" ", "-").replace(".", "-").replace(":", "-")
        sentiment = "1" if documentScore > 0 and documentMag > 3 else "0"
        savefilepath = "journals/" + savefilepath + "-" + sentiment + ".jrnl"
        
        os.makedirs("journals", exist_ok=True)
        with open(savefilepath, "w+") as savefile:
            savefile.write(self.journalEdit.toPlainText())

    def wag(self):
        self.hachikoMovie.stop()
        self.hachikoMovie = QMovie("img/HachikoHappyGif")
        self.hachikoLabel.setMovie(self.hachikoMovie)
        self.hachikoMovie.start()

    def howl(self):
        self.hachikoMovie.stop()
        self.hachikoMovie = QMovie("img/HachikoGoodBoy")
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = Window()
    sys.exit(app.exec_())

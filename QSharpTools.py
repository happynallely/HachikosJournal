import re
from PyQt5.QtWidgets import QMainWindow, QPushButton
from PyQt5.QtCore import Qt, QVariantAnimation, QAbstractAnimation
from PyQt5.QtGui import QCursor, QColor, QPalette

def rgbStringToInt(rgbString):
    # Fixed the SyntaxWarning with 'r' prefix
    search = re.search(r"^rgb\(\s*(\d*)\s*,\s*(\d*)\s*,\s*(\d*)\s*\)$", rgbString)
    return int(search.group(1)), int(search.group(2)), int(search.group(3))

def rgbIntToString(redInt, greenInt, blueInt):
    return "rgb(" + str(redInt) + ", " + str(greenInt) + ", " + str(blueInt) + ")"

class SharpButton(QPushButton):
    def __init__(self, primaryColor = "rgb(66, 133, 129)", secondaryColor = "rgb(66, 133, 129)", font_family = "Verdana", font_size = "13px", font_weight = "normal", border_style = "solid", border_width = "2px", border_radius = "0px"):
        super().__init__()
        self.setCursor(QCursor(Qt.PointingHandCursor))

        self.primaryColor = primaryColor
        self.secondaryColor = secondaryColor 
        
        # Get RGB values for Primary color (start)
        p1, p2, p3 = rgbStringToInt(self.primaryColor)
        
        # Get RGB values for Secondary color (end/hover)
        s1, s2, s3 = rgbStringToInt(self.secondaryColor)
        
        # Initial text color set to white for visibility
        self.color = "white" 
        self.background_color = self.primaryColor
        
        # Setup animation from Primary (p) to Secondary (s)
        self.animation = QVariantAnimation(startValue = QColor(p1, p2, p3), endValue = QColor(s1, s2, s3), valueChanged = self.onHover, duration = 400)

        self.font_family = font_family
        self.font_size = font_size
        self.font_weight = font_weight

        self.border_style = border_style
        self.border_color = primaryColor
        self.border_width = border_width
        self.border_radius = border_radius

        self.renderStyleSheet()

    def renderStyleSheet(self):
        self.styleSheet = "QPushButton{"
        self.styleSheet += "color: " + self.color + ";"
        self.styleSheet += "background-color: " + self.background_color + ";"

        self.styleSheet += "border-style: " + self.border_style + ";"
        self.styleSheet += "border-color: " + self.border_color + ";"
        self.styleSheet += "border-width: " + self.border_width + ";"
        self.styleSheet += "border-radius: " + self.border_radius + ";"

        self.styleSheet += "font-family: " + self.font_family + ";"
        self.styleSheet += "font-size: " + self.font_size + ";"
        self.styleSheet += "font-weight: " + self.font_weight + ";"
        self.styleSheet += "}"

        self.setStyleSheet(self.styleSheet)
    
    def onHover(self, color):
        # Update the background color based on animation progress
        self.background_color = color.name()
        self.renderStyleSheet()

    def enterEvent(self, event):
        # When mouse enters, play animation Forward (Primary -> Secondary)
        self.animation.setDirection(QAbstractAnimation.Forward)
        self.animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        # When mouse leaves, play animation Backward (Secondary -> Primary)
        self.animation.setDirection(QAbstractAnimation.Backward)
        self.animation.start()
        super().leaveEvent(event)
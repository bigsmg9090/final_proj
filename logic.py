from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import QColor
from gui import *


class Logic(QMainWindow, Ui_Final):
    """
    Creates a Logic Object that can be applied to a GUI
    QMainWindow: main window object in the QtWidgets
    Ui_Final: Name of the GUI application created by the programmer
    """
    text1 = ("Four score and seven years ago our fathers brought forth on this continent, a new nation, conceived in "
             "Liberty, and dedicated to the proposition that all men are created equal. Now we are engaged in a great "
             "civil war, testing whether that nation, or any nation so conceived and so dedicated, can long endure. "
             "We are met on a great battle-field of that war. We have come to dedicate a portion of that field, "
             "as a final resting place for those who here gave their lives that that nation might live. It is "
             "altogether fitting and proper that we should do this.")

    text2 = ("But, in a larger sense, we can not dedicate -- we can not consecrate -- we can not hallow -- this "
             "ground. The brave men, living and dead, who struggled here, have consecrated it, far above our "
             "poor power to add or detract. The world will little note, nor long remember what we say here, "
             "but it can never forget what they did here. It is for us the living, rather, to be dedicated here "
             "to the unfinished work which they who fought here have thus far so nobly advanced.")

    text3 = ("It is rather for us to be here dedicated to the great task remaining before us -- that from these "
             "honored dead we take increased devotion to that cause for which they gave the last full measure of "
             "devotion -- that we here highly resolve that these dead shall not have died in vain -- that this "
             "nation, under God, shall have a new birth of freedom -- and that government of the people, "
             "by the people, for the people, shall not perish from the earth.")
    pages = [text1, text2, text3]

    def __init__(self) -> None:
        """
       Initializes the logic for the GUI
       """
        super().__init__()
        self.setupUi(self)

        self.begin_button.clicked.connect(self.begin)
        self.quit_button.clicked.connect(self.quit)

        self.current_position = 0
        self.current_page = 0
        self.text_to_type = ""

        self.highlighted_labels = {}
        self.previous_incorrect = False

        self.timer = QTimer(self)
        self.timer_count = 60000  # 60 seconds countdown in milliseconds
        self.timer.timeout.connect(self.update_timer_label)

    def begin(self) -> None:
        """
        Sets the screen to the text page; sets the timer to 60 seconds.
        """
        self.installEventFilter(self)
        self.begin_button.setText("Restart")
        self.current_page = 0
        self.text_box.setText(self.pages[self.current_page])
        self.text_to_type = self.pages[self.current_page]
        self.current_position = 0
        self.previous_incorrect = False
        self.timer_count = 60000  # 60 seconds countdown in milliseconds
        self.start_timer()

    def start_timer(self) -> None:
        """
        Starts the countdown for your time to type.
        """
        self.update_timer_label()
        self.timer.start(100)  # Start timer with 0.1-second interval

    def update_timer_label(self) -> None:
        """
        Updates the time on the timer every 1 deci second and the words per minute achieved once the time has finished.
        """
        seconds = int((self.timer_count / 1000) % 60)
        milliseconds = int((self.timer_count % 1000) / 100)
        self.timer_label.setText(f"Timer: {seconds:02d}.{milliseconds}")

        self.timer_count -= 100
        if self.timer_count < 0:
            self.timer.stop()
            total_words = self.calculate_total_words()
            elapsed_time_in_minutes = (60000 - self.timer_count) / 1000 / 60
            if elapsed_time_in_minutes != 0:
                wpm = int(total_words)
            else:
                wpm = 0
            self.wpm_label.setText(f"WPM: {wpm:.2f}")

            self.removeEventFilter(self)

    def calculate_words_within_page(self) -> int:
        """
        Calculates how far into the page the person got.

        Returns the total words within the page the person last went through.
        """
        words_within_page = 0

        for i in range(self.current_page):
            words_within_page += len(self.pages[i].split())
        words_within_page += len(self.text_to_type[:self.current_position].split())
        return words_within_page

    def calculate_total_words(self) -> int:
        """
        Calculates the total words the person typed.

        Returns the total number of words the person types
        """
        if self.current_page == 0:
            return self.calculate_words_within_page()
        elif self.current_page == 1:
            return self.calculate_words_within_page() + len(self.text1.split())
        elif self.current_page == 2:
            return self.calculate_words_within_page() + len(self.text1.split()) + len(self.text2.split())

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """
        Filters key events to handle typing and backspace
        obj: A QObject in PyQt; The object that triggered the event.
        event: A QEvent in PyQt; The event triggered.

        Returns bool if True (if the event is handled), otherwise None.
        """
        if obj == self and event.type() == QEvent.Type.KeyPress:
            if self.begin_button.text() == "Restart":
                if self.current_position < len(self.text_to_type):
                    key = event.text().upper()
                    expected_char = self.text_to_type[self.current_position].upper()
                    if key == expected_char:
                        if self.previous_incorrect:
                            return True  # Return True to prevent further processing of the key event
                        self.highlight_label(self.current_position, QColor("green"))
                        self.current_position += 1
                        self.previous_incorrect = False
                    elif event.key() == Qt.Key.Key_Backspace:  # Added elif to handle
                        # backspace
                        if self.current_position == 0:
                            self.highlight_label(self.current_position, QColor("white"))  # Remove highlighting
                        else:
                            self.highlight_label(self.current_position, QColor("white"))  # Remove highlighting

                        self.previous_incorrect = False
                        return True
                    else:
                        if self.previous_incorrect:
                            return True  # Return True to prevent further processing of the key event
                        self.previous_incorrect = True
                        self.highlight_label(self.current_position, QColor("red"))
                        return True  # Return True for any incorrect key press to prevent further processing
                elif self.current_position == len(self.text_to_type):
                    self.next_page()
                    return True
        return super().eventFilter(obj, event)

    def highlight_label(self, index: int, color: QColor) -> None:
        """
        Highlights the character at the specified index in the text box with the given color.
        index: The index (int) of the current letter the person should be typing.
        color: A QColor object in PyQt; The color to use for highlighting.
        """
        if index < len(self.text_to_type):
            highlighted_text = (
                    self.text_to_type[:index] +
                    f"<span style='background-color: {color.name()}'>{self.text_to_type[index]}</span>" +
                    self.text_to_type[index + 1:]
            )
            self.text_box.setTextFormat(Qt.TextFormat.RichText)
            self.text_box.setText(highlighted_text)

    def next_page(self) -> None:
        """
        Changes the text prompt to the next paragraph once the person has reached the end of a prompt. There are
        three total.
        """
        self.current_page = (self.current_page + 1) % len(self.pages)
        self.text_box.setText(self.pages[self.current_page])
        self.text_to_type = self.pages[self.current_page]
        self.current_position = 0
        self.previous_incorrect = False

    def quit(self) -> None:
        """
        Re-sets the screen to the home screen with the instructions. Stops timer and resets button texts.
        """
        self.text_box.setText("Text will appear when you press begin" + "\n" + "\n" + "Do not press shift for CAPS, "
                              "or enter--simply type the expected letters.")
        self.begin_button.setText("Begin")
        self.timer.stop()
        self.timer_label.setText("Timer:")



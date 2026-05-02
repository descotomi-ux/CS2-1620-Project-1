from PyQt6.QtWidgets import *

from new_user_Window import Ui_new_userWindow
from welcome_Window import Ui_MainWindow
from past_inquiries_Window import Ui_pastInquiriesWindow
import csv

class Logic(QMainWindow, Ui_MainWindow):
    def __init__(self):
        """
        The init method since we're working with classes,
        sets/defines initial class attributes. Also allows
        both button on start up page to function.
        """
        super().__init__()
        self.setupUi(self)

        self.setFixedSize(self.size())

        self.welcomeScreen_mainLabel.setStyleSheet("color: black;")
        self.welcomeScreen_infoLabel.setStyleSheet("color: black;")
        self.user_status = None
        self.is_submitted = False

        self.new_userButton.clicked.connect(self.open_new_user_window)
        self.returning_userButton.clicked.connect(self.open_returning_user_window)

    def open_new_user_window(self) -> None:
        """
        Open the 'New User window' and sets the user status
        """
        self.setup_new_user_window()

        self.user_status = "New User"
        self.is_submitted = False

        self.hide()
        self.new_window.show()

    def open_returning_user_window(self) -> None:
        """
        Opens returning user window. After clicking the 'returning user' button,
        they'll be redirected to this window. It also defines the user status, and the setReadOnly
        allows users to type in their info to look up their account
        """
        self.pastInquiries_window = QMainWindow()
        self.pastInquiries_new_ui = Ui_pastInquiriesWindow()
        self.pastInquiries_new_ui.setupUi(self.pastInquiries_window)
        self.pastInquiries_window.setFixedSize(self.pastInquiries_window.size())

        self.user_status = "Returning User"

        self.pastInquiries_new_ui.pastInquries_newInquiry_Button.setEnabled(False)
        self.pastInquiries_new_ui.pastInjuries_firstName_input.setReadOnly(False)
        self.pastInquiries_new_ui.pastInquiries_lastName_input.setReadOnly(False)
        self.pastInquiries_new_ui.pastInquries_studentID_input.setReadOnly(False)

        self.pastInquiries_new_ui.returning_user_lookUp_Submit_Button.clicked.connect(self.lookup_returning_user)
        self.pastInquiries_new_ui.pastInquries_newInquiry_Button.clicked.connect(self.inquiries_to_new_inquiry_screen_change)
        self.pastInquiries_new_ui.pastInquiries_to_new_user_Button.clicked.connect(self.past_inquiries_to_new_user_screen_change)

        self.hide()
        self.pastInquiries_window.show()

    def lookup_returning_user(self) -> None:
        """
        Gets the text from the input boxes for returning users and validates, then checks to see if that
        student's data/info is in the CSV file
        """
        first_name = self.pastInquiries_new_ui.pastInjuries_firstName_input.text()
        last_name = self.pastInquiries_new_ui.pastInquiries_lastName_input.text()
        student_id = self.pastInquiries_new_ui.pastInquries_studentID_input.text()

        if first_name == "":
            self.show_error(self.pastInquiries_new_ui.pastInjuries_infoLabel, "Please enter first name")
            return
        if not first_name.isalpha():
            self.show_error(self.pastInquiries_new_ui.pastInjuries_infoLabel,"First name must only use letters")
            return

        if last_name == "":
            self.show_error(self.pastInquiries_new_ui.pastInjuries_infoLabel,"Please enter last name")
            return
        if not last_name.isalpha():
            self.show_error(self.pastInquiries_new_ui.pastInjuries_infoLabel,"Last name must only use letter")
            return

        if student_id == "":
            self.show_error(self.pastInquiries_new_ui.pastInjuries_infoLabel,"Please enter student ID")
            return
        if not student_id.isdigit():
            self.show_error(self.pastInquiries_new_ui.pastInjuries_infoLabel,"Student ID must only use numbers")
            return

        self.display_student_info_table(first_name, last_name, student_id)

    def new_user_inquiry_to_home(self) -> None:
        """
        Changes window from new user inquiry screen to home screen
        """
        self.new_window.close()
        self.show()

    def setup_new_user_window(self) -> None:
        """
        Connects widgets/UI elements
        """
        self.new_window = QMainWindow()
        self.new_ui = Ui_new_userWindow()
        self.new_ui.setupUi(self.new_window)
        self.new_window.setFixedSize(self.new_window.size())

        self.score_inputs: list[QLineEdit] = []
        self.new_ui.test_total_input.textChanged.connect(self.create_score_inputs)

        #AI HELP
        self.new_ui.other_course_input_lineEdit.setEnabled(False)
        self.new_ui.other_radioButton.toggled.connect(self.toggle_other_course_input)

        inputs = [
            self.new_ui.firstName_input,
            self.new_ui.lastName_input,
            self.new_ui.studentID_input,
            self.new_ui.test_total_input,
            self.new_ui.passingGrade_input
        ]

        for input in inputs:
            input.textChanged.connect(self.clear_error)

        self.new_ui.submit_Button.clicked.connect(self.new_user_inquiry)
        self.new_ui.save_exitButton.clicked.connect(self.new_user_inquiry_to_home)
        self.new_ui.past_inquiriesButton.clicked.connect(self.past_inquiries_page_display)

    #AI HELP TO CREATE INPUT BOXES AFTER ONLY HAD LINE EDIT WIDGET
    def create_score_inputs(self) -> None:
        """
        Creates score input boxes based on amount of test taken
        """
        for score_input in self.score_inputs:
            self.new_ui.scores_layout.removeWidget(score_input)
            score_input.deleteLater()

        self.score_inputs = []
        total_tests_text = self.new_ui.test_total_input.text().strip()

        if not total_tests_text.isdigit():
            return

        total_tests = int(total_tests_text)
        if total_tests < 1 or total_tests > 5:
            return

        for index in range(total_tests):
            score_input = QLineEdit()
            score_input.setPlaceholderText(f'Score #{index + 1}')
            score_input.textChanged.connect(self.clear_error)

            self.new_ui.scores_layout.addWidget(score_input)
            self.score_inputs.append(score_input)

    #AI HELP, ORIGINALLY WANTED OPTIONAL TEXT BOX, EVEN IF 'OTHER' SELECTED
    #AI SUGGESTED THIS AND DECIDED TO IMPLEMENT SUGGESTION
    def toggle_other_course_input(self) -> None:
        """
        Enables/disables "other" input box
        """
        if self.new_ui.other_radioButton.isChecked():
            self.new_ui.other_course_input_lineEdit.setEnabled(True)
        else:
            self.new_ui.other_course_input_lineEdit.setEnabled(False)
            self.new_ui.other_course_input_lineEdit.clear()

    def new_user_inquiry(self) -> None:
        """
        Processes and validates user input
        """
        first_name = str(self.new_ui.firstName_input.text().strip())
        if first_name == "":
            self.show_error(self.new_ui.passingGrade_label_2, "Please enter first name")
            return
        if not first_name.isalpha():
            self.show_error(self.new_ui.passingGrade_label_2,"First name must use letters only")
            return
        self.new_ui.firstName_input.setText(first_name.title())

        last_name = str(self.new_ui.lastName_input.text().strip())
        if last_name == "":
            self.show_error(self.new_ui.passingGrade_label_2,"Please enter last name")
            return
        if not last_name.isalpha():
            self.show_error(self.new_ui.passingGrade_label_2,"Last name must use letters only")
            return
        self.new_ui.lastName_input.setText(last_name.title())

        student_id = self.new_ui.studentID_input.text().strip()
        if student_id =="":
            self.show_error(self.new_ui.passingGrade_label_2,"Please enter a student ID")
            return
        if not student_id.isdigit():
            self.show_error(self.new_ui.passingGrade_label_2,"Student ID must use numbers only")
            return
        if int(student_id) == 0:
            self.show_error(self.new_ui.passingGrade_label_2,"Student ID cannot be all zeros")
            return

        #AI HELP, NEEDED ASSISTANCE TO FIGURE OUT HOW TO GET TEXT TO FROM RADIO BUTTON'S INPUT BOX &
        #SUGGESTED USING TWO SEPARATE VARIABLES THAT ALSO REQUIRES INPUT BOX TO BE FILLED, ORIGINALLY
        #PLANNED FOR IT TO BE OPTIONAL(162-174)
        course_button = self.new_ui.courseButton_Group.checkedButton()
        if course_button:
            if course_button.text() == "Other":
                other_course_input =self.new_ui.other_course_input_lineEdit.text().strip()
                if other_course_input == "":
                    self.show_error(self.new_ui.passingGrade_label_2,"Please enter a course name")
                    return
            else:
                other_course_input = course_button.text()
        else:
            self.show_error(self.new_ui.passingGrade_label_2, "Please select a course")
            return
        other_course_input = other_course_input.title()
        self.new_ui.other_course_input_lineEdit.setText(other_course_input)


        total_tests_text = self.new_ui.test_total_input.text().strip()
        if total_tests_text == "":
            self.show_error(self.new_ui.passingGrade_label_2,"Please enter total tests")
            return
        if not total_tests_text.isdigit():
            self.show_error(self.new_ui.passingGrade_label_2,"Invalid input, numbers only")
            return

        total_tests = int(total_tests_text)
        if total_tests == 0:
            self.show_error(self.new_ui.passingGrade_label_2,"0 is not a valid input")
            return
        if total_tests > 5:
            self.show_error(self.new_ui.passingGrade_label_2,"5 test max")
            return

        scores = []
        for score_input in self.score_inputs:
            score_text = score_input.text().strip()

            if score_text == "":
                self.show_error(self.new_ui.passingGrade_label_2,"Please enter score(s)")
                return

            if not score_text.isdigit():
                self.show_error(self.new_ui.passingGrade_label_2,"Invalid input, numbers only")
                return

            score_number = int(score_text)

            if score_number < 0 or score_number > 100:
                self.show_error(self.new_ui.passingGrade_label_2,f"Score number must be between 0 and 100")
                return

            scores.append(score_number)

        if len(scores) != total_tests:
            self.show_error(self.new_ui.passingGrade_label_2,f"You entered {len(scores)} scores, expected {total_tests} scores")
            return

        passing_grade_text = self.new_ui.passingGrade_input.text().strip()

        if passing_grade_text == "":
            self.show_error(self.new_ui.passingGrade_label_2,"Please enter a passing grade")
            return
        if not passing_grade_text.isdigit():
            self.show_error(self.new_ui.passingGrade_label_2,"Invalid input, numbers only")
            return

        passing_grade = int(passing_grade_text)
        first_name = first_name.title()
        last_name = last_name.title()
        other_course_input = other_course_input.title()

        grade_needed_to_pass, current_grade = self.calculate_test_scores(
            scores,
            total_tests,
            passing_grade
        )
        self.display_score_and_save_to_file(first_name,
                                            last_name,
                                            student_id,
                                            other_course_input,
                                            current_grade,
                                            passing_grade,
                                            grade_needed_to_pass
        )

    def calculate_test_scores(self, scores: list[int], total_tests: int, passing_grade: int) -> tuple[int, int]:
        """
        Calculates the students current grade and the score the need to pass (based on their input)
        :param tests_scores: String of test scores
        :param total_tests: Total number of tests
        :param passing_grade: Grade needed to_pass
        :return: (Tuple containing grade_needed_to_pass, current_grade)
        """
        total = sum(scores)

        current_grade = int(total/len(scores))
        grade_needed_to_pass = (passing_grade * (total_tests + 1)) - total
        return grade_needed_to_pass, current_grade

    def display_score_and_save_to_file(self,
                                       first_name: str,
                                       last_name: str,
                                       student_id: str,
                                       course: str,
                                       current_grade: int,
                                       passing_grade: int,
                                       grade_needed_to_pass: int
    )-> None:
        """
        Displays the score needed to pass the class and saves info to CSV file
        :param first_name: Student's first name
        :param last_name: Student's last name
        :param student_id: Student's school ID
        :param course: Name of the course
        :param current_grade: Current test average
        :param passing_grade: Overall passing grade for course
        :param grade_needed_to_pass: Grade needed on final to pass course
        """
        #AI HELP (LINE 265), SET DEFAULT COLOR SO IT CAN BE CHANGED LATER TO RED FOR ERROR MESSAGES
        self.new_ui.passingGrade_label_2.setStyleSheet("color: black;")
        self.show_success(self.new_ui.passingGrade_label_2, f'You need a {grade_needed_to_pass}% on your final to pass {course} with a {passing_grade}%')
        self.is_submitted = True

        row_two = [
            first_name,
            last_name,
            student_id,
            course,
            current_grade,
            passing_grade,
            grade_needed_to_pass
        ]
        with open('student_info.csv', 'a', newline='') as file:
            content = csv.writer(file)

            content.writerow(row_two)

    def past_inquiries_page_display(self) -> None:
        """
        Sets up the past inquiries window for Returning user
        """
        if not self.is_submitted:
            self.show_error(self.pastInquiries_new_ui.pastInjuries_infoLabel, "Submit an inquiry first to view history.")
            return

        else:
            first_name = self.new_ui.firstName_input.text()
            last_name = self.new_ui.lastName_input.text()
            student_id = self.new_ui.studentID_input.text()

            self.pastInquiries_window = QMainWindow()
            self.pastInquiries_new_ui = Ui_pastInquiriesWindow()
            self.pastInquiries_new_ui.setupUi(self.pastInquiries_window)

            self.pastInquiries_new_ui.pastInquries_newInquiry_Button.clicked.connect(self.inquiries_to_new_inquiry_screen_change)
            self.pastInquiries_new_ui.pastInquiries_to_new_user_Button.clicked.connect(self.past_inquiries_to_new_user_screen_change)

            self.pastInquiries_new_ui.pastInjuries_firstName_input.setText(first_name)
            self.pastInquiries_new_ui.pastInquiries_lastName_input.setText(last_name)
            self.pastInquiries_new_ui.pastInquries_studentID_input.setText(student_id)
            self.pastInquiries_new_ui.pastInjuries_firstName_input.setReadOnly(True)
            self.pastInquiries_new_ui.pastInquiries_lastName_input.setReadOnly(True)
            self.pastInquiries_new_ui.pastInquries_studentID_input.setReadOnly(True)

            self.display_student_info_table(first_name, last_name, student_id)

            self.new_window.close()
            self.pastInquiries_window.show()

    def inquiries_to_new_inquiry_screen_change(self) -> None:
        """
        Capitalizes first/last, even if multiple first/last names,
        Prefills first/last/student ID inputs now that user is in system
        """
        first_name = self.pastInquiries_new_ui.pastInjuries_firstName_input.text().title()
        last_name = self.pastInquiries_new_ui.pastInquiries_lastName_input.text().title()
        student_id = self.pastInquiries_new_ui.pastInquries_studentID_input.text()

        self.setup_new_user_window()
        self.user_status = "Returning User"

        self.new_ui.firstName_input.setText(first_name)
        self.new_ui.lastName_input.setText(last_name)
        self.new_ui.studentID_input.setText(student_id)

        # AI HELP TO FIGURE OUT HOW TO ALLOW ONLY RETURNING USER INFO TO BE PREFILLED (329-332)
        self.new_ui.firstName_input.setReadOnly(True)
        self.new_ui.lastName_input.setReadOnly(True)
        self.new_ui.studentID_input.setReadOnly(True)

        self.is_submitted = False

        self.pastInquiries_window.close()
        self.new_window.show()

    def past_inquiries_to_new_user_screen_change(self) -> None:
        """
        Changes window from 'past inquiries' to 'new user' inquiry
        """
        self.pastInquiries_window.close()
        self.open_new_user_window()

    def retrieve_students_cvs_file(self) -> list:
        """
        Reads student data from CSV file
        :return: list of students cvs data, including first, last, ID, course,
        current grade in class, overall passing grade for class, and grade needed,
        on final to pass
        """
        student_data = []
        try:
            with open('student_info.csv', 'r', newline='') as file:
                content = csv.reader(file)

                for row in content:
                    student_data.append(row)
        except FileNotFoundError:
            self.pastInquiries_new_ui.pastInquiries_firstName_label.setText('File Error!')
            self.pastInquiries_new_ui.pastInquiries_firstName_label.setStyleSheet("color: red")

        return student_data

    def display_student_info_table(self, first_name: str, last_name: str, student_id: str) -> None:
        """
        Searches and displays student data based on first/last name and ID
        :param first_name: Student's first name
        :param last_name: Student's last name
        :param student_id: Student's School ID
        """
        data = self.retrieve_students_cvs_file()
        student_matches = []
        for row in data:
            if len(row) < 7:
                continue

            if (
                    row[0].strip().lower() == first_name.strip().lower()
                    and row[1].strip().lower() == last_name.strip().lower()
                    and row[2].strip() == student_id.strip()
            ):
                student_matches.append(row)

        #AI HELP FOR TO DISPLAY THE HEADERS AND INFO TABLE ITSELF (371-382)
        table = self.pastInquiries_new_ui.pastInquiries_table
        table.setRowCount(0)
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Course", "Current Grade", "Passing Grade", "Needed on Final"])

        for row_index, row_data in enumerate(student_matches):
            table.insertRow(row_index)

            table.setItem(row_index, 0, QTableWidgetItem(row_data[3]))
            table.setItem(row_index, 1, QTableWidgetItem(row_data[4]))
            table.setItem(row_index, 2, QTableWidgetItem(row_data[5]))
            table.setItem(row_index, 3, QTableWidgetItem(row_data[6]))

        if len(student_matches) == 0:
            self.show_error(self.pastInquiries_new_ui.pastInjuries_infoLabel, "Account not found!")
            self.pastInquiries_new_ui.pastInquries_newInquiry_Button.setEnabled(False)
        else:
            self.show_success(self.pastInquiries_new_ui.pastInjuries_infoLabel, "Account found!")
            self.pastInquiries_new_ui.pastInquries_newInquiry_Button.setEnabled(True)

    def clear_error(self) -> None:
        """
        Clears error messages when user picks widget/element/input to edit input
        """
        self.new_ui.passingGrade_label_2.setText('')

    #AI HELP, WANTED TEXT TO CHANGE COLOR FOR ERROR MESSAGES, BUT ONLY WORK ON
    #ONE SCREEN, SUGGESTED ADDING ARGUMENT 'LABEL' SO IT WOULD WORK FOR ALL FUNCTIONS
    #(396-398)
    def show_error(self, label: QLabel, message: str) -> None:
        """
        Shows error messages in red
        :param label: the label name of each element/widget
        :param message: The message that displays on the screen
        """
        label.setStyleSheet("color: red;")
        label.setText(message)

    def show_success(self, label : QLabel, message: str) -> None:
        """
        Message without errors detected display in green
        """
        label.setStyleSheet("color: green;")
        label.setText(message)
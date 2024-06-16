import time

from airway_genius_gui.connector import CalculationThread
from airway_genius_gui.globals import MarkerType, set_cur_marker_type, GUI_DIR, MapType, AlgoType, get_bounding_box, \
    OtherColor
from airway_genius_gui.scalable_graphics_view import ScalableGraphicsView

from PySide6.QtCore import (QCoreApplication, QMetaObject, Qt, QThread, Signal)
from PySide6.QtGui import (QBrush, QColor, QIcon, QPalette)
from PySide6.QtWidgets import (QFrame, QGraphicsView, QHBoxLayout, QLayout, QSizePolicy,
                               QSpacerItem, QVBoxLayout, QWidget, QButtonGroup)

from qfluentwidgets import (CheckBox, ComboBox, PrimaryPushButton, PushButton, FluentIcon, TransparentToolButton,
                            TransparentPushButton, TeachingTip, TeachingTipTailPosition, RadioButton, CompactSpinBox,
                            StrongBodyLabel, CaptionLabel,
                            IndeterminateProgressBar, InfoBar, InfoBarPosition, ProgressBar, BodyLabel,
                            CompactDoubleSpinBox, MessageBox)


class UiMainWindow(object):
    """
    This class is used to generate the main window of the application.
    It implements most UI design and logic of the main window.
    """

    def __init__(self):
        self.is_input_able = True  # a flag to indicate whether the input(button click, input box, etc.) is able

    def setup_ui(self, main_window):
        if not main_window.objectName():
            main_window.setObjectName(u"MainWindow")
        main_window.resize(1200, 800)
        # color style
        palette = QPalette()
        brush = QBrush(QColor(255, 255, 255, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Base, brush)
        palette.setBrush(QPalette.Active, QPalette.Window, brush)
        brush1 = QBrush(QColor(233, 233, 233, 255))
        brush1.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.AlternateBase, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Window, brush)
        palette.setBrush(QPalette.Inactive, QPalette.AlternateBase, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush)
        palette.setBrush(QPalette.Disabled, QPalette.Window, brush)
        palette.setBrush(QPalette.Disabled, QPalette.AlternateBase, brush1)
        main_window.setPalette(palette)
        icon = QIcon(f'{GUI_DIR}/src/fighter_jet.svg')
        main_window.setWindowIcon(icon)
        self.central_widget = QWidget(main_window)
        self.central_widget.setObjectName(u"central_widget")
        palette1 = QPalette()
        palette1.setBrush(QPalette.Active, QPalette.Window, brush)
        brush2 = QBrush(QColor(241, 241, 241, 255))
        brush2.setStyle(Qt.SolidPattern)
        palette1.setBrush(QPalette.Active, QPalette.AlternateBase, brush2)
        palette1.setBrush(QPalette.Inactive, QPalette.Window, brush)
        palette1.setBrush(QPalette.Inactive, QPalette.AlternateBase, brush2)
        palette1.setBrush(QPalette.Disabled, QPalette.Base, brush)
        palette1.setBrush(QPalette.Disabled, QPalette.Window, brush)
        palette1.setBrush(QPalette.Disabled, QPalette.AlternateBase, brush2)
        self.central_widget.setPalette(palette1)
        self.central_widget.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.central_widget.setAutoFillBackground(False)

        self.horizontal_layout = QHBoxLayout(self.central_widget)
        self.horizontal_layout.setObjectName(u"horizontal_layout")
        self.horizontal_layout_2 = QHBoxLayout()
        self.horizontal_layout_2.setObjectName(u"horizontal_layout_2")
        self.vertical_layout = QVBoxLayout()
        self.vertical_layout.setObjectName(u"vertical_layout")
        self.vertical_layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)

        self.vertical_spacer_2 = QSpacerItem(20, 5, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        # a spacer to make the left side of the window show completely
        self.horizontal_spacer_3 = QSpacerItem(125, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.vertical_layout.addSpacerItem(self.horizontal_spacer_3)
        self.vertical_layout.addItem(self.vertical_spacer_2)

        # -----------------Map and Algorithm combo box-----------------
        self.map_check_box = ComboBox(self.central_widget)
        self.map_check_box.setObjectName(u"map_check_box")
        for map_type in MapType:
            self.map_check_box.addItem(map_type.value, userData=map_type)

        self.algorithm_combo_box = ComboBox(self.central_widget)
        self.algorithm_combo_box.setObjectName(u"algorithm_combo_box")
        for algo_type in AlgoType:
            self.algorithm_combo_box.addItem(algo_type.value, userData=algo_type)

        self.map_label = StrongBodyLabel("Map")
        self.vertical_layout.addWidget(self.map_label)
        self.vertical_layout.addWidget(self.map_check_box)

        self.algorithm_label = StrongBodyLabel("Algorithm")
        self.vertical_layout.addWidget(self.algorithm_label)
        self.vertical_layout.addWidget(self.algorithm_combo_box)

        self.vertical_spacer_3 = QSpacerItem(20, 5, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.vertical_layout.addItem(self.vertical_spacer_3)

        # -----------------Radio buttons for markers-----------------
        marker_radio_button_widget = QWidget()

        self.radio_button_1 = RadioButton(self.central_widget)
        self.radio_button_2 = RadioButton(self.central_widget)
        self.radio_button_3 = RadioButton(self.central_widget)
        self.radio_button_4 = RadioButton(self.central_widget)
        self.radio_button_1.setObjectName(u"radio_button_1")
        self.radio_button_2.setObjectName(u"radio_button_2")
        self.radio_button_3.setObjectName(u"radio_button_3")
        self.radio_button_4.setObjectName(u"radio_button_4")

        self.radio_button_group = QButtonGroup(marker_radio_button_widget)
        self.radio_button_group.addButton(self.radio_button_1)
        self.radio_button_group.addButton(self.radio_button_2)
        self.radio_button_group.addButton(self.radio_button_3)
        self.radio_button_group.addButton(self.radio_button_4)

        self.radio_button_1.setChecked(True)

        layout = QVBoxLayout(marker_radio_button_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.radio_button_1, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.radio_button_2, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.radio_button_3, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.radio_button_4, 0, Qt.AlignmentFlag.AlignLeft)

        self.add_marker_label = StrongBodyLabel("Add Marker")
        self.vertical_layout.addWidget(self.add_marker_label)
        self.vertical_layout.addWidget(marker_radio_button_widget)

        self.horizontal_spliter_1 = QFrame(self.central_widget)
        self.horizontal_spliter_1.setObjectName(u"horizontalSpliter")
        self.horizontal_spliter_1.setFrameShape(QFrame.Shape.HLine)
        self.horizontal_spliter_1.setFrameShadow(QFrame.Shadow.Raised)

        self.vertical_layout.addWidget(self.horizontal_spliter_1)

        self.vertical_spacer_5 = QSpacerItem(20, 1, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self.vertical_layout.addItem(self.vertical_spacer_5)

        # -----------------Fighter Jet Setting-----------------
        self.fighter_jet_label = StrongBodyLabel("Fighter Jet")
        self.vertical_layout.addWidget(self.fighter_jet_label)
        # start position and end position
        self.start_pos_label = CaptionLabel("Start Position")
        self.vertical_layout.addWidget(self.start_pos_label)

        self.horizontal_layout_3 = QHBoxLayout()

        self.start_pos_coord_label = BodyLabel("undefined")
        self.start_pos_transparent_tool_button = TransparentToolButton(FluentIcon.EDIT, parent=self.central_widget)
        self.start_pos_transparent_tool_button.setObjectName(u"start_pos_transparent_tool_button")
        self.horizontal_layout_3.addWidget(self.start_pos_coord_label)
        self.horizontal_layout_3.addWidget(self.start_pos_transparent_tool_button)
        self.vertical_layout.addLayout(self.horizontal_layout_3)

        self.end_pos_label = CaptionLabel("Destination")
        self.vertical_layout.addWidget(self.end_pos_label)

        self.horizontal_layout_4 = QHBoxLayout()
        self.end_pos_coord_label = BodyLabel("undefined")
        self.end_pos_transparent_tool_button = TransparentToolButton(FluentIcon.EDIT, parent=self.central_widget)
        self.end_pos_transparent_tool_button.setObjectName(u"end_pos_transparent_tool_button")
        self.horizontal_layout_4.addWidget(self.end_pos_coord_label)
        self.horizontal_layout_4.addWidget(self.end_pos_transparent_tool_button)
        self.vertical_layout.addLayout(self.horizontal_layout_4)

        # fuel and fuel cost setting
        self.max_fuel_spin_box = CompactSpinBox(self.central_widget)
        self.max_fuel_spin_box.setObjectName(u"max_fuel_spin_box")
        self.horizontal_layout_5 = QHBoxLayout()
        min_max_fuel = 5
        max_max_fuel = 40
        self.max_fuel_spin_box.setMinimum(min_max_fuel)
        self.max_fuel_spin_box.setMaximum(max_max_fuel)
        self.max_fuel_spin_box.setValue(12)
        self.unit_label_1 = BodyLabel("ton")

        self.fuel_label = CaptionLabel(f"Max Fuel [{min_max_fuel}, {max_max_fuel}]")
        self.horizontal_layout_5.addWidget(self.max_fuel_spin_box)
        self.horizontal_layout_5.addWidget(self.unit_label_1)
        self.vertical_layout.addWidget(self.fuel_label)
        self.vertical_layout.addLayout(self.horizontal_layout_5)

        self.fuel_cost_spin_box = CompactDoubleSpinBox(self.central_widget)
        self.fuel_cost_spin_box.setObjectName(u"fuel_cost_spin_box")
        self.horizontal_layout_6 = QHBoxLayout()
        min_fuel_cost = 1
        max_fuel_cost = 10
        self.fuel_cost_spin_box.setMinimum(min_fuel_cost)
        self.fuel_cost_spin_box.setMaximum(max_fuel_cost)
        self.fuel_cost_spin_box.setValue(2.18)
        self.unit_label_2 = BodyLabel("kg/km")

        with open(f"{GUI_DIR}/src/fighter_jet_setting_spin_box.qss", "r") as f:
            self.max_fuel_spin_box.setStyleSheet(f.read())
            self.fuel_cost_spin_box.setStyleSheet(f.read())

        self.fuel_cost_label = CaptionLabel(f"Fuel Cost [{min_fuel_cost}.00, {max_fuel_cost}.00]")
        self.horizontal_layout_6.addWidget(self.fuel_cost_spin_box)
        self.horizontal_layout_6.addWidget(self.unit_label_2)
        self.vertical_layout.addWidget(self.fuel_cost_label)
        self.vertical_layout.addLayout(self.horizontal_layout_6)

        # -----------------Clear Map Button-----------------
        self.clear_map_push_button = PushButton(self.central_widget)
        self.clear_map_push_button.setObjectName(u"clear_map_push_button")

        self.vertical_spacer_6 = QSpacerItem(20, 5, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self.horizontal_spliter_2 = QFrame(self.central_widget)
        self.horizontal_spliter_2.setObjectName(u"horizontalSpliter")
        self.horizontal_spliter_2.setFrameShape(QFrame.Shape.HLine)
        self.horizontal_spliter_2.setFrameShadow(QFrame.Shadow.Raised)

        self.vertical_layout.addItem(self.vertical_spacer_6)

        self.vertical_layout.addWidget(self.horizontal_spliter_2)

        # -----------------Other-----------------
        self.other_label = StrongBodyLabel("Other")
        self.vertical_layout.addWidget(self.other_label)
        self.vertical_layout.addWidget(self.clear_map_push_button)

        # antialiasing and help button
        self.antialiasing_check_box = CheckBox(self.central_widget)
        self.antialiasing_check_box.setObjectName(u"antialiasing_check_box")

        self.vertical_layout.addWidget(self.antialiasing_check_box)

        self.help_transparent_push_button = TransparentPushButton(FluentIcon.QUESTION, u"help")
        self.help_transparent_push_button.setObjectName(u"help_transparent_push_button")

        self.vertical_layout.addWidget(self.help_transparent_push_button)

        self.vertical_spacer_4 = QSpacerItem(20, 5, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.vertical_layout.addItem(self.vertical_spacer_4)

        # -----------------Start Button-----------------
        self.start_push_button = PrimaryPushButton(self.central_widget)
        self.start_push_button.setObjectName(u"start_push_button")

        self.vertical_layout.addWidget(self.start_push_button)

        self.vertical_spacer = QSpacerItem(20, 5, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.vertical_layout.addItem(self.vertical_spacer)

        self.horizontal_layout_2.addLayout(self.vertical_layout)

        self.horizontalSpacer_2 = QSpacerItem(5, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontal_layout_2.addItem(self.horizontalSpacer_2)

        # -----------------Stop Button-----------------
        self.stop_push_button = PushButton(self.central_widget)
        with open(f"{GUI_DIR}/src/stop_push_button.qss", "r") as f:
            self.stop_push_button.setStyleSheet(f.read())
        self.stop_push_button.setObjectName(u"stop_push_button")

        self.vertical_layout.addWidget(self.stop_push_button)
        self.stop_push_button.setEnabled(False)

        # -----------------Vertical Line Spliter-----------------
        self.vertical_spliter = QFrame(self.central_widget)
        self.vertical_spliter.setObjectName(u"vertical_spliter")
        self.vertical_spliter.setFrameShape(QFrame.Shape.VLine)
        self.vertical_spliter.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontal_layout_2.addWidget(self.vertical_spliter)

        self.horizontal_spacer = QSpacerItem(5, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontal_layout_2.addItem(self.horizontal_spacer)

        # -----------------Graphics View(Map)-----------------
        self.vertical_layout_2 = QVBoxLayout()
        self.vertical_layout_2.setObjectName(u"vertical_layout_2")
        self.graphics_view = ScalableGraphicsView(self.central_widget)
        self.graphics_view.setObjectName(u"graphics_view")
        self.graphics_view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.graphics_view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.graphics_view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.graphics_view.setRubberBandSelectionMode(Qt.ItemSelectionMode.IntersectsItemShape)

        self.vertical_layout_2.addWidget(self.graphics_view)

        # -----------------Progress Bar-----------------
        self.progress_bar = ProgressBar(self.central_widget)
        self.progress_bar.setObjectName(u"progress_bar")
        self.progress_bar.setValue(0)
        self.progress_bar.hide()

        self.indeterminate_progress_bar = IndeterminateProgressBar(self.central_widget)
        self.indeterminate_progress_bar.setObjectName(u"indeterminate_progress_bar")
        self.indeterminate_progress_bar.setPaused(True)

        self.vertical_layout_2.addWidget(self.indeterminate_progress_bar)

        self.vertical_layout_2.addWidget(self.progress_bar)

        self.horizontal_layout_2.addLayout(self.vertical_layout_2)

        self.horizontal_layout.addLayout(self.horizontal_layout_2)

        main_window.setCentralWidget(self.central_widget)

        self.retranslate_ui(main_window)

        QMetaObject.connectSlotsByName(main_window)

        self.connect_signals()

    def connect_signals(self):
        """
        Connect signals to slots.
        """
        self.radio_button_1.clicked.connect(lambda: set_cur_marker_type(MarkerType.NONE_TYPE))
        self.radio_button_2.clicked.connect(lambda: set_cur_marker_type(MarkerType.CARRIER))
        self.radio_button_3.clicked.connect(lambda: set_cur_marker_type(MarkerType.TANKER))
        self.radio_button_4.clicked.connect(lambda: set_cur_marker_type(MarkerType.AIRPORT))

        self.radio_button_group.buttonClicked.connect(lambda button: print(button.text()))
        self.start_pos_transparent_tool_button.clicked.connect(self.switch_disable_input_state)
        self.start_pos_transparent_tool_button.clicked.connect(
            lambda: self.start_pos_transparent_tool_button.setEnabled(True))

        self.end_pos_transparent_tool_button.clicked.connect(self.switch_disable_input_state)
        self.end_pos_transparent_tool_button.clicked.connect(
            lambda: self.end_pos_transparent_tool_button.setEnabled(True))

        self.clear_map_push_button.clicked.connect(self.reset_start_end_pos)

        self.antialiasing_check_box.stateChanged.connect(
            lambda state: self.graphics_view.set_antialiasing(self.antialiasing_check_box.checkState()))

        self.help_transparent_push_button.clicked.connect(self.show_teaching_tip)

        self.start_push_button.clicked.connect(self.start)

        self.stop_push_button.clicked.connect(self.terminate_calculation)

        self.start_pos_transparent_tool_button.clicked.connect(self.graphics_view.switch_set_start_pos)
        self.end_pos_transparent_tool_button.clicked.connect(self.graphics_view.switch_set_end_pos)

        self.graphics_view.start_pos_set.connect(self.set_start_pos_label)
        self.graphics_view.end_pos_set.connect(self.set_end_pos_label)

        self.graphics_view.start_pos_set.connect(self.switch_disable_input_state)
        self.graphics_view.end_pos_set.connect(self.switch_disable_input_state)

        self.graphics_view.reset_start_pos.connect(self.reset_start_pos)
        self.graphics_view.reset_end_pos.connect(self.reset_end_pos)

        self.graphics_view.error_signal.connect(self.error_message)
        self.graphics_view.success_signal.connect(self.success_message)

        self.clear_map_push_button.clicked.connect(self.graphics_view.clear_map)

        self.map_check_box.currentIndexChanged.connect(
            lambda: self.graphics_view.change_map(self.map_check_box.currentData()))

    def retranslate_ui(self, main_window):
        """
        Set the text of the widgets.
        :param main_window: the main window
        """
        main_window.setWindowTitle(QCoreApplication.translate("MainWindow", u"Airway Genius", None))
        self.antialiasing_check_box.setText(QCoreApplication.translate("MainWindow", u"Antialiasing", None))
        self.clear_map_push_button.setText(QCoreApplication.translate("MainWindow", u"Clear Map", None))
        self.start_push_button.setText(QCoreApplication.translate("MainWindow", u"start", None))
        self.stop_push_button.setText(QCoreApplication.translate("MainWindow", u"stop", None))
        self.radio_button_1.setText(QCoreApplication.translate("MainWindow", u"None", None))
        self.radio_button_2.setText(QCoreApplication.translate("MainWindow", u"Carrier", None))
        self.radio_button_3.setText(QCoreApplication.translate("MainWindow", u"Tanker", None))
        self.radio_button_4.setText(QCoreApplication.translate("MainWindow", u"Airport", None))

    def show_teaching_tip(self):
        """
        Show the teaching tip.
        """
        carrier = MarkerType.CARRIER.value
        carrier_color = f"{carrier.red()}, {carrier.green()}, {carrier.blue()}"
        tanker = MarkerType.TANKER.value
        tanker_color = f"{tanker.red()}, {tanker.green()}, {tanker.blue()}"
        airport = MarkerType.AIRPORT.value
        airport_color = f"{airport.red()}, {airport.green()}, {airport.blue()}"
        forbidden = OtherColor.FORBIDDEN_AREA_COLOR.value
        forbidden_color = f"{forbidden.red()}, {forbidden.green()}, {forbidden.blue()}"
        path = OtherColor.PATH_COLOR.value
        path_color = f"{path.red()}, {path.green()}, {path.blue()}"
        TeachingTip.create(
            target=self.help_transparent_push_button,
            icon=FluentIcon.QUESTION,
            title='help\n-----',
            content=f"""
            <p>1. Click the start button to start calculation.</p>
            <p>2. Toggle radio buttons to switch marker type to be added on the map.</p>
            <p>3. Right-click to add marker on the map</p>
            <p>4. Middle-click elements to delete it.</p>
            <p>5. Drag the map with left mouse button to move it.</p>
            <p>6. Use mouse wheel to zoom in/out.</p>
            <p>7. Hold 'ctrl' key on keyboard and use left mouse button to draw a polygon.</p>
            <p>8. Use the edit button shaped as pen to set start and end positions(left click carrier or airport).</p>
            <p>9. Carrier can only be put on sea and airport can only be put on land, and they both can refuel the jet.</p>
            <p>10. In most cases, calculation time is within 30s, but DFS may be very slow in some cases(may be minutes).</p>
            <p>
                Legend:&nbsp;&nbsp;
                <span style='color:rgb({carrier_color});'>&#11044;</span> Carrier&nbsp;&nbsp;
                <span style='color:rgb({tanker_color});'>&#11044;</span> Tanker&nbsp;&nbsp;
                <span style='color:rgb({airport_color});'>&#11044;</span> Airport&nbsp;&nbsp;
                <span style='color:rgb({forbidden_color});'>&#11044;</span> Forbidden Area&nbsp;&nbsp;
                <span style='color:rgb({path_color});'>&#11044;</span> Path
            </p>
            <p>Note: 1 pixel is 8.47km in real world.</p>
            """,
            isClosable=True,
            tailPosition=TeachingTipTailPosition.LEFT,
            duration=20000,
            parent=self.central_widget
        )

    def start(self):
        """
        Use separate thread to collect data and start the calculation thread.
        """

        class DataCollector(QThread):
            """
            A thread to collect data from the main window.
            """
            data_signal = Signal(list)
            error_signal = Signal(str, str)
            collecting_time_signal = Signal(float)

            def __init__(self, main_window: UiMainWindow):
                super().__init__()
                self.main_window = main_window

            def run(self):
                # record the time of data collection
                start_time = time.time()
                data = self.main_window.collect_data()
                end_time = time.time()
                if len(data) == 1:
                    if data[0] == -1:
                        self.error_signal.emit("Data Collection Error", "Please set the start and end positions first.")
                    elif data[0] == -2:
                        self.error_signal.emit("Data Collection Error", "Please set at least 2 carrier or airport.")
                    elif data[0] == -3:
                        self.error_signal.emit("Data Collection Error",
                                               "Invalid start or end position: no such carrier or airport.")
                    return
                get_bounding_box(data)
                self.collecting_time_signal.emit(end_time - start_time)
                self.data_signal.emit(data)

        self.data_collector = DataCollector(self)
        self.data_collector.started.connect(self.switch_disable_input_state)
        self.data_collector.started.connect(self.enable_indeterminate_progress_bar)
        self.data_collector.finished.connect(self.switch_disable_input_state)
        self.data_collector.finished.connect(self.disable_indeterminate_progress_bar)
        self.data_collector.error_signal.connect(self.error_message)
        self.data_collector.collecting_time_signal.connect(self.handle_collecting_time)
        self.data_collector.data_signal.connect(self.construct_and_start_search_thread)
        self.data_collector.finished.connect(self.data_collector.deleteLater)
        self.data_collector.start()

    def collect_data(self):
        start_pos, end_pos = self.graphics_view.get_start_end_pos()
        carrier_airport_list, tanker_list = self.graphics_view.get_marker_list()
        if start_pos == (-1, -1) or end_pos == (-1, -1):
            return [-1]
        elif len(carrier_airport_list) < 2:
            return [-2]
        elif start_pos not in carrier_airport_list or end_pos not in carrier_airport_list:
            return [-3]
        max_fuel = self.max_fuel_spin_box.value()
        fuel_cost = self.fuel_cost_spin_box.value()
        max_fuel = int(max_fuel * 1000 / fuel_cost / 8.47)
        fuel_cost = 1
        cur_algorithm = self.algorithm_combo_box.currentData()
        forbidden_area_coords_list = self.graphics_view.get_polygon_contain_coord_list()
        map_size = self.graphics_view.get_map_size()
        return [max_fuel, fuel_cost, cur_algorithm, forbidden_area_coords_list, carrier_airport_list, tanker_list,
                start_pos, end_pos, map_size]

    def construct_and_start_search_thread(self, data: list):
        """
        Construct the calculation thread and start it.
        :param data: the data collected from the main window
        """
        if data[2] == AlgoType.DFS or data[2] == AlgoType.ALL:
            # remind that DFS algorithm may cause stack overflow, if user still choose DFS algorithm, then continue
            warning = MessageBox("<p style=\"color:red;\">WARNING</p>",
                                 "The DFS algorithm here uses recursion strategy and may cause stack over flow! "
                                 "Especially when the distance is long! "
                                 "The recursion limit has been set to 2500 to prevent the program from crashing. "
                                 "However, it may still cause the program to crash and report a error message like "
                                 "\'Process finished with exit code -1073741571 (0xC00000FD)\' "
                                 "due to your computer's hardware and runtime settings.\n"
                                 "Are you sure to launch it?",
                                 self.central_widget)
            if warning.exec():
                pass
            else:
                return
        self.sub_thread = CalculationThread(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7],
                                            data[8], data[9])
        self.sub_thread.started.connect(self.switch_disable_input_state)
        self.sub_thread.started.connect(self.enable_indeterminate_progress_bar)
        self.sub_thread.finished.connect(self.disable_indeterminate_progress_bar)
        self.sub_thread.finished.connect(self.sub_thread.deleteLater)
        self.sub_thread.finished.connect(self.switch_disable_input_state)
        self.sub_thread.finished_signal.connect(self.handle_running_time)
        self.sub_thread.finished_signal.connect(lambda: self.stop_push_button.setEnabled(False))
        self.sub_thread.result_signal.connect(self.graphics_view.draw_path)
        self.sub_thread.all_signal.connect(self.compare_all_algorithms)
        self.sub_thread.error_signal.connect(self.error_message)

        self.stop_push_button.setEnabled(True)
        self.sub_thread.start()

    def terminate_calculation(self):
        """
        Terminate the calculation thread.
        """
        self.sub_thread.terminate()
        self.stop_push_button.setEnabled(False)

    def switch_disable_input_state(self):
        """
        Switch the input state.
        """
        if self.is_input_able:
            self.is_input_able = False
            self.graphics_view.set_unchangeable()
            self.algorithm_combo_box.setEnabled(False)
            self.map_check_box.setEnabled(False)
            self.start_push_button.setEnabled(False)
            self.radio_button_1.setEnabled(False)
            self.radio_button_2.setEnabled(False)
            self.radio_button_3.setEnabled(False)
            self.radio_button_4.setEnabled(False)
            self.clear_map_push_button.setEnabled(False)
            self.max_fuel_spin_box.setEnabled(False)
            self.fuel_cost_spin_box.setEnabled(False)
            self.start_pos_transparent_tool_button.setEnabled(False)
            self.end_pos_transparent_tool_button.setEnabled(False)
        else:
            self.is_input_able = True
            self.graphics_view.set_changeable()
            self.algorithm_combo_box.setEnabled(True)
            self.map_check_box.setEnabled(True)
            self.start_push_button.setEnabled(True)
            self.radio_button_1.setEnabled(True)
            self.radio_button_2.setEnabled(True)
            self.radio_button_3.setEnabled(True)
            self.radio_button_4.setEnabled(True)
            self.clear_map_push_button.setEnabled(True)
            self.max_fuel_spin_box.setEnabled(True)
            self.fuel_cost_spin_box.setEnabled(True)
            self.start_pos_transparent_tool_button.setEnabled(True)
            self.end_pos_transparent_tool_button.setEnabled(True)

    def enable_indeterminate_progress_bar(self):
        self.indeterminate_progress_bar.start()

    def disable_indeterminate_progress_bar(self):
        self.indeterminate_progress_bar.stop()

    def handle_running_time(self, running_time: float):
        """
        Handle the running time of the calculation thread.
        :param running_time: the running time of the calculation thread
        """
        self.success_message(f'{self.algorithm_combo_box.currentText()} Algorithm',
                             f"Search Finished! Time Cost: {running_time:.2f} s", 5000)

    def handle_collecting_time(self, collecting_time: float):
        """
        Handle the collecting time of the data collector thread.
        :param collecting_time: the collecting time of the data collector thread
        """
        self.success_message("Data Collection", f"Data Collection Finished! Time Cost: {collecting_time:.2f} s", 4000)

    def set_start_pos_label(self, coords: list[2]):
        """
        Set the start position label.
        :param coords: the coordinates of the start position
        """
        if coords[0] == -1 and coords[1] == -1:
            self.error_message("Start Position Set Error",
                               f"The start position can't be set to the destination. Please reset the start position.")
            self.start_pos_coord_label.setText(f"undefined")
            return
        self.success_message("Start Position Set", f"({coords[0]}, {coords[1]})")
        self.start_pos_coord_label.setText(f"({coords[0]}, {coords[1]})")

    def set_end_pos_label(self, coords: list[2]):
        """
        Set the end position label.
        :param coords: the coordinates of the end position
        """
        if coords[0] == -1 and coords[1] == -1:
            self.error_message("Destination Set Error",
                               f"The end position can't be set to the start position. Please reset the destination.")
            self.end_pos_coord_label.setText(f"undefined")
            return
        self.success_message("Destination Set", f"({coords[0]}, {coords[1]})")
        self.end_pos_coord_label.setText(f"({coords[0]}, {coords[1]})")

    def reset_start_end_pos(self):
        """
        Reset the start and end positions.
        """
        self.start_pos_coord_label.setText("undefined")
        self.end_pos_coord_label.setText("undefined")

    def success_message(self, success_title: str, message: str, duration: int = 3000):
        """
        Show the success message.
        """
        InfoBar.success(
            title=success_title,
            content=message,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=duration,
            parent=self.central_widget
        )

    def error_message(self, error_title: str, message: str, duration: int = 3000):
        """
        Show the error message.
        """
        InfoBar.error(
            title=error_title,
            content=message,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=duration,
            parent=self.central_widget
        )

    def reset_start_pos(self):
        """
        Reset the start position.
        """
        self.start_pos_coord_label.setText("undefined")

    def reset_end_pos(self):
        """
        Reset the end position.
        """
        self.end_pos_coord_label.setText("undefined")

    def compare_all_algorithms(self,
                               dij_len: int,
                               dij_time: float,
                               astar_len: int,
                               astar_time: float,
                               bfs_len: int,
                               bfs_time: float,
                               dfs_len: int,
                               dfs_time: float, ):
        """
        Compare the results of all algorithms.
        """
        if dfs_len == -1:
            dfs_message = "DFS: Recursion Error\n"
        elif dfs_len == -2:
            dfs_message = "DFS: Not launch\n"
        else:
            dfs_message = f"DFS: length = {round(dfs_len * 8.47, 2)} km, time = {dfs_time:.2f} s\n"
        result = MessageBox("<p>Running Result</p>",
                            "The result of BFS, DFS, A* and Dijkstra algorithms are as follows:\n"
                            f"BFS: length = {round(bfs_len * 8.47, 2)} km, time = {bfs_time:.2f} s\n"
                            f"A*: length = {round(astar_len * 8.47, 2)} km, time = {astar_time:.2f} s\n"
                            f"Dijkstra: length = {round(dij_len * 8.47, 2)} km, time = {dij_time:.2f} s\n"
                            f"{dfs_message}",
                            self.central_widget)
        result.exec()

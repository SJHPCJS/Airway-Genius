from airway_genius_gui.globals import get_cur_marker_type, MarkerType

from PySide6.QtCore import Qt, Signal, QPointF, QTimer, QMutex, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtWidgets import QGraphicsView, QGraphicsEllipseItem, QGraphicsScene, QGraphicsPolygonItem, \
    QGraphicsPathItem
from PySide6.QtGui import QColor, QPixmap, QPolygonF, QPainter, QPainterPath, QPen, QPainterPathStroker, QImage, \
    QTransform

from airway_genius_gui.globals import GUI_DIR, MapType, OtherColor


class ScalableGraphicsView(QGraphicsView):
    start_pos_set = Signal(list)
    end_pos_set = Signal(list)
    animation_finished = Signal()
    error_signal = Signal(str, str)
    success_signal = Signal(str, str, int)
    clear_queue_signal = Signal()
    reset_start_pos = Signal()
    reset_end_pos = Signal()

    def getZoomLevel(self):
        return self.transform().m11()

    def setZoomLevel(self, zoomLevel):
        self.setTransform(QTransform().scale(zoomLevel, zoomLevel))

    zoomLevel = Property(float, getZoomLevel, setZoomLevel)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.drawing_polygon = False
        self.drawing_path = False
        self.current_polygon = QPolygonF()
        self.current_polygon_item = None
        self.polygons = {}
        self.markers = []
        self.marker_radius = 3
        self.changeable = True
        self.fighter_jet_start_pos = [-1, -1]
        self.fighter_jet_end_pos = [-1, -1]
        self.select_start_pos = False
        self.select_end_pos = False
        self.paths = []
        self.animation_queue = AnimationQueue(self)
        self.map_mask = QImage(f'{GUI_DIR}/src/China_mask.png')
        self.mutex = QMutex()

        scene = QGraphicsScene()
        self.map_img = QPixmap(f'{GUI_DIR}/src/China.png')
        scene.addPixmap(self.map_img)
        super().setScene(scene)

    def set_unchangeable(self):
        self.changeable = False

    def set_changeable(self):
        self.changeable = True

    def set_antialiasing(self, antialiasing: Qt.CheckState):
        if antialiasing is Qt.CheckState.Checked:
            self.setRenderHints(QPainter.RenderHint.Antialiasing)
        else:
            self.setRenderHints(QPainter.RenderHint(0))

    def wheelEvent(self, event):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor
        # zoom in or out when current scale is within (0.5, 5)
        if event.angleDelta().y() > 0 and self.transform().m11() < 5:
            self.animateZoom(self.transform().m11(), self.transform().m11() * zoom_in_factor)
        elif event.angleDelta().y() < 0 and self.transform().m11() > 0.5:
            self.animateZoom(self.transform().m11(), self.transform().m11() * zoom_out_factor)
        elif event.angleDelta().y() > 0 and self.transform().m11() >= 5:
            self.error_signal.emit("Zoom In Error", "The map is already zoomed in to the maximum level!")
        elif event.angleDelta().y() < 0 and self.transform().m11() <= 0.5:
            self.error_signal.emit("Zoom Out Error", "The map is already zoomed out to the minimum level!")

    def animateZoom(self, start_value, end_value):
        self.animation = QPropertyAnimation(self, b"zoomLevel")
        self.animation.setDuration(175)
        self.animation.setEasingCurve(QEasingCurve.Type.OutExpo)

        # set the start and end values of the animation
        self.animation.setStartValue(start_value)
        self.animation.setEndValue(end_value)

        # start the animation
        self.animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def mousePressEvent(self, event):
        # detect if the ctrl key is pressed
        ctrl_pressed = event.modifiers() & Qt.KeyboardModifier.ControlModifier
        # convert the mouse position to scene coordinates
        scene_pos = self.mapToScene(event.pos())
        if self.changeable:
            if event.button() == Qt.MouseButton.RightButton:
                self.__add_marker(scene_pos)
            elif ctrl_pressed and event.button() == Qt.MouseButton.LeftButton:
                self.set_polygon_drawing()
                self.current_polygon = QPolygonF()
                self.current_polygon.append(self.mapToScene(event.pos()))
                self.current_polygon_item = self.__create_tmp_polygon_item()
            else:
                super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.changeable:
            if self.drawing_polygon:
                self.current_polygon.append(self.mapToScene(event.pos()))
                self.scene().removeItem(self.current_polygon_item)
                self.current_polygon_item = self.__create_tmp_polygon_item()
            else:
                super().mouseMoveEvent(event)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.changeable:
            if event.button() == Qt.MouseButton.LeftButton and self.drawing_polygon:
                self.set_polygon_drawn()
                self.current_polygon_item.setBrush(OtherColor.FORBIDDEN_AREA_COLOR.value)
                self.__create_polygon_item(self.current_polygon_item)
            else:
                super().mouseReleaseEvent(event)
        else:
            super().mouseReleaseEvent(event)

    def __add_marker(self, scene_pos: QPointF):
        if scene_pos.x() < 0 or scene_pos.x() >= self.map_img.width() or scene_pos.y() < 0 or scene_pos.y() >= self.map_img.height():
            return
        cur_marker = get_cur_marker_type()
        if cur_marker == MarkerType.NONE_TYPE:
            return
        elif cur_marker == MarkerType.CARRIER and self.is_land(scene_pos.x(), scene_pos.y()):
            self.error_signal.emit("Invalid Position", "Carrier can only be placed on the sea!")
        elif cur_marker == MarkerType.AIRPORT and not self.is_land(scene_pos.x(), scene_pos.y()):
            self.error_signal.emit("Invalid Position", "Airport can only be placed on the land!")
        else:
            marker = Marker(scene_pos.x() - self.marker_radius, scene_pos.y() - self.marker_radius,
                            self.marker_radius * 2,
                            cur_marker, self)
            self.scene().addItem(marker)
            self.markers.append(marker)
            print("add marker")

    def remove_marker(self, marker):
        if self.changeable:
            if self.markers:
                print("remove marker: " + str(marker.coord_center))
                if marker.coord_center == self.fighter_jet_start_pos:
                    self.fighter_jet_start_pos = (-1, -1)
                    self.reset_start_pos.emit()
                elif marker.coord_center == self.fighter_jet_end_pos:
                    self.fighter_jet_end_pos = (-1, -1)
                    self.reset_end_pos.emit()
                self.scene().removeItem(marker)
                self.markers.remove(marker)
                print("remove marker, current markers:", len(self.markers))

    def __create_tmp_polygon_item(self):
        polygon_item = PolygonItem(self.current_polygon, self)
        self.scene().addItem(polygon_item)
        return polygon_item

    def __create_polygon_item(self, current_polygon_item):
        self.polygons.update({current_polygon_item: self.current_polygon})

    def remove_polygon(self, polygon):
        if self.changeable:
            if self.polygons:
                self.scene().removeItem(polygon)
                self.polygons.pop(polygon)
                print("remove polygon, current polygons:", len(self.polygons))

    def change_map(self, map_type: MapType):
        self.mutex.lock()
        if self.drawing_path:
            self.set_path_drawn()
            self.timer.stop()
        self.__clear_scene()
        self.map_img = QPixmap(f'{GUI_DIR}/src/{map_type.value}.png')
        self.map_mask = QImage(f'{GUI_DIR}/src/{map_type.value}_mask.png')
        self.scene().addPixmap(self.map_img)
        self.mutex.unlock()

    def __clear_scene(self):
        self.scene().clear()
        self.polygons.clear()
        self.markers.clear()
        self.paths.clear()
        self.current_polygon = QPolygonF()
        self.current_polygon_item = None
        print("clear scene")

    def clear_map(self):
        if self.changeable:
            self.mutex.lock()
            if self.drawing_polygon:
                self.set_path_drawn()
                self.drawing_path = False
                self.timer.stop()
                print("drawing_path set False")
            self.fighter_jet_end_pos = [-1, -1]
            self.fighter_jet_start_pos = [-1, -1]
            self.__clear_scene()
            self.scene().addPixmap(self.map_img)
            self.mutex.unlock()

    def switch_set_start_pos(self):
        self.select_start_pos = not self.select_start_pos
        self.select_end_pos = False

    def set_start_pos(self, x, y):
        if self.fighter_jet_end_pos[0] == x and self.fighter_jet_end_pos[1] == y:
            self.select_start_pos = False
            self.fighter_jet_start_pos = (-1, -1)
            self.start_pos_set.emit((-1, -1))
            return
        self.fighter_jet_start_pos = (x, y)
        self.select_start_pos = False
        self.start_pos_set.emit(self.fighter_jet_start_pos)

    def cancel_set_start_pos(self):
        self.select_start_pos = False

    def switch_set_end_pos(self):
        self.select_start_pos = False
        self.select_end_pos = not self.select_end_pos

    def set_end_pos(self, x, y):
        if self.fighter_jet_start_pos[0] == x and self.fighter_jet_start_pos[1] == y:
            self.select_end_pos = False
            self.fighter_jet_end_pos = (-1, -1)
            self.end_pos_set.emit((-1, -1))
            return
        self.fighter_jet_end_pos = (x, y)
        self.select_end_pos = False
        self.end_pos_set.emit(self.fighter_jet_end_pos)

    def cancel_set_end_pos(self):
        self.select_end_pos = False

    def get_polygon_contain_coord_list(self):
        # traverse all the polygons and get the coordinates that are contained in the polygons
        polygon_contain_coord_list = set()
        for polygon in self.polygons.values():
            polygon: QPolygonF
            bounding_rect = polygon.boundingRect()
            for x in range(int(bounding_rect.x()), int(bounding_rect.x() + bounding_rect.width())):
                for y in range(int(bounding_rect.y()), int(bounding_rect.y() + bounding_rect.height())):
                    if self.__point_in_polygon(x, y, polygon):
                        polygon_contain_coord_list.add((x, y))
        # print("polygon_contain_coord_list:", polygon_contain_coord_list)
        return list(polygon_contain_coord_list)

    def __point_in_polygon(self, x, y, polygon: QPolygonF):
        if x < 0 or y < 0 or x >= self.map_img.width() or y >= self.map_img.height():
            return False
        return polygon.containsPoint(QPointF(x, y), Qt.FillRule.WindingFill)

    def get_marker_list(self):
        carrier_airport_list = []
        tanker_list = []
        for marker in self.markers:
            if marker.coord_center[0] < 0 or marker.coord_center[0] >= self.map_img.width() or \
                    marker.coord_center[1] < 0 or marker.coord_center[1] >= self.map_img.height():
                continue
            if marker.marker_type == MarkerType.CARRIER or marker.marker_type == MarkerType.AIRPORT:
                carrier_airport_list.append(marker.coord_center)
            elif marker.marker_type == MarkerType.TANKER:
                tanker_list.append(marker.coord_center)
        return carrier_airport_list, tanker_list

    def get_start_end_pos(self):
        # return tuple rather than list
        return tuple(self.fighter_jet_start_pos), tuple(self.fighter_jet_end_pos)

    def get_map_size(self) -> tuple[int, int]:
        return tuple((self.map_img.width(), self.map_img.height()))

    def draw_path(self, points):
        if hasattr(self, 'timer'):
            if self.timer.isActive():
                self.animation_queue.add_animation(points)
                return
        path_len = len(points)
        if path_len == 0:
            self.error_signal.emit("Invalid Search Result", "No path found!")
            return
        else:
            self.success_signal.emit("Path found", f"Total distance: {round(path_len * 8.47, 2)}km", 5000)
        self.points = points
        self.path = QPainterPath()
        # if the point is out of the map
        if points[0][0] < 0 or points[0][0] >= self.map_img.width() or points[0][1] < 0 or points[0][
            1] >= self.map_img.height():
            self.error_signal.emit("Invalid Search Result", "The start point is out of the map!")
            return
        self.path.moveTo(points[0][0], points[0][1])
        self.path_item = PathItem(self.path, self)
        self.path_item.setPen(QPen(OtherColor.PATH_COLOR.value, 3))
        self.set_path_drawing()
        self.scene().addItem(self.path_item)

        self.timer = QTimer()
        self.timer.timeout.connect(self.add_next_point_to_path)
        self.timer.start(int(1000 / 120))

    def add_next_point_to_path(self):
        self.mutex.lock()
        if self.points and len(self.points) > 0 and self.drawing_path:
            next_point = self.points.pop(0)
            if next_point[0] < 0 or next_point[0] >= self.map_img.width() or next_point[1] < 0 or next_point[
                1] >= self.map_img.height():
                self.error_signal.emit("Invalid Search Result", "Point out of map!")
                self.timer.stop()
                self.scene().removeItem(self.path_item)
                return
            self.path.lineTo(QPointF(next_point[0], next_point[1]))
            try:
                self.path_item.setPath(self.path)
            except Exception as e:
                pass
        elif self.drawing_path:
            self.paths.append(self.path_item)
            print("add path, current paths:", len(self.paths))
            self.timer.stop()
            self.path_item.set_drawn()
            self.set_path_drawn()
            self.animation_finished.emit()
        else:
            print("stop drawing path")
            if self.timer.isActive():
                self.timer.stop()
            self.clear_queue_signal.emit()
        self.mutex.unlock()

    def remove_path(self, path):
        if self.changeable:
            if self.paths:
                self.scene().removeItem(path)
                self.paths.remove(path)
                print("remove path, current paths:", len(self.paths))

    def set_polygon_drawing(self):
        self.drawing_polygon = True

    def set_polygon_drawn(self):
        self.drawing_polygon = False

    def set_path_drawing(self):
        self.drawing_path = True

    def set_path_drawn(self):
        self.drawing_path = False

    def is_land(self, x, y):
        return self.map_mask.pixelColor(x, y) == QColor(Qt.GlobalColor.white)


class Marker(QGraphicsEllipseItem):
    """
    A circle marker that can be added to the ScalableGraphicsView
    """

    def __init__(self, x, y, radius, cur_marker: MarkerType, graphics_view: ScalableGraphicsView):
        super().__init__(x - radius, y - radius, radius * 2, radius * 2)
        self.radius = radius
        self.marker_type = cur_marker
        self.setBrush(cur_marker.value)
        self.setPen(QColor(Qt.GlobalColor.white))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.graphics_view = graphics_view
        self.coord_center = (int(x), int(y))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.graphics_view.select_start_pos and (
                    self.marker_type == MarkerType.AIRPORT or self.marker_type == MarkerType.CARRIER):
                self.graphics_view.set_start_pos(self.coord_center[0], self.coord_center[1])
            elif self.graphics_view.select_end_pos and (
                    self.marker_type == MarkerType.AIRPORT or self.marker_type == MarkerType.CARRIER):
                self.graphics_view.set_end_pos(self.coord_center[0], self.coord_center[1])
            return
        if event.button() == Qt.MouseButton.MiddleButton:
            self.graphics_view.remove_marker(self)


class PolygonItem(QGraphicsPolygonItem):
    """
    A polygon item that can be added to the ScalableGraphicsView
    """

    def __init__(self, polygon: QPolygonF, graphics_view: ScalableGraphicsView, parent=None):
        super().__init__(polygon, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.graphics_view = graphics_view

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.graphics_view.remove_polygon(self)


class PathItem(QGraphicsPathItem):
    """
    A path item that can be added to the ScalableGraphicsView
    """

    def __init__(self, path: QPainterPath, graphics_view: ScalableGraphicsView, parent=None):
        super().__init__(path, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.graphics_view = graphics_view
        self.drawing = True

    def shape(self):
        # override the shape method to make the path shape precise
        stroke = QPainterPathStroker()
        stroke.setWidth(5)
        return stroke.createStroke(self.path())

    def set_drawn(self):
        self.drawing = False

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton and not self.drawing:
            self.graphics_view.remove_path(self)


class AnimationQueue:
    def __init__(self, graphics_view: ScalableGraphicsView):
        self.graphics_view = graphics_view
        self.waiting_queue = []
        self.graphics_view.animation_finished.connect(self.start_next_animation)
        self.graphics_view.clear_queue_signal.connect(self.clear_queue)

    def add_animation(self, points):
        self.waiting_queue.append(points)

    def start_next_animation(self):
        if len(self.waiting_queue) > 0:
            self.graphics_view.draw_path(self.waiting_queue.pop(0))

    def clear_queue(self):
        self.waiting_queue.clear()

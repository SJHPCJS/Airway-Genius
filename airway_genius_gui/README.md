### GUI Part

#### Note:
- The GUI is built using the `Pyside6` library in Python, with styled component library `PySide6-Fluent-Widgets`.
- The GUI part demands python version 3.7 or above.
- All the requirements are mentioned in the `requirements.txt` file, 
you can use `pip install -r requirments.txt` in `airway_genius_gui` directory to only install the packages for GUI part.
- To run the GUI, you should run `main.py` in `AirwayGenius` directory rather than `entrance.py` in the `airway_genius_gui` directory.
- Style sheet of certain elements in the GUI is modified from the qfluentwidgets source code(see the .qss file in `airway_genius_gui/src` directory). 
the link of original GitHub repository is: https://github.com/zhiyiYo/PyQt-Fluent-Widgets/tree/PySide6/qfluentwidgets/_rc/qss/light.

#### API & Data Format:
- The GUI part will communicate with the backend part using the in `connector.py`. Backend should provide a function to `connector.py`.
- `max_fuel`: `int` The maximum fuel the fighter jet can carry.
- `fuel_cost`: `int` The fuel cost per unit distance(pixel).
- `cur_algorithm`: `AlgoType` The algorithm selected by the user.
- `forbidden_area`: `set[tuple[int, int]]` The list of forbidden area coordinates(contains tuples composed of x and y). e.g. `[(x1, y1), (x2, y2)]`.
- `carrier_airport_list`: `list[tuple[int, int]]` The list of carrier airport coordinates(contains tuples composed of x and y). e.g. `[(x1, y1), (x2, y2)]`.
- `tanker_list`: `list[tuple[int, int]]` The list of tanker coordinates(contains tuples composed of x and y). e.g. `[(x1, y1), (x2, y2)]`.
- `start_pos`: `tuple[int, int]` The start position of the fighter jet. e.g. `(x, y)`.
- `end_pos`: `tuple[int, int]` The end position of the fighter jet. e.g. `(x, y)`.
- `map_size`: `tuple[int, int]` The size of the map. e.g. `(width, height)`.
- The backend algorithm should return a list of coordinates of the path. Type: `list[tuple[int, int]]` e.g. `[(x1, y1), (x2, y2)]`.

#### Update Information:
- `2024/5/25 14:30`: Added the initial test files. Many parts of the code is hard coded for initial testing, and interfaces haven't been designed.
Important: The image of maps hasn't been segmented yet, so the existing images are not referential.
- `2024/5/28 14:40`: Upgrade GUI. Add start and end position selection, fuel setting, forbidden area coords list getting, marker coords list getting. 
- `2024/5/29 22:20`: Upgrade GUI. Add path drawing. Design interface for backend. Segment the map image. Create map mask. Enable starting from `main.py`.
- `2024/5/30 15:10`: Fix a bug of GUI. Update README.md. Define the `API & Data Format`. Add entrance.py for running the GUI.
- `2024/5/30 23:05`: Fix a bug caused by multi-threading in GUI when drawing the path and as the same time call to clear map.
- `2024/5/31 19:15`: Fix a bug caused by incorrect type of map_mask.
- `2024/5/31 19:45`: Modify fighter jet data to J20.
- `2024/5/31 20:15`: Add AlgoType in global.py.
- `2024/6/1 1:45`: Add zoom in/out animation.
- `2024/6/1 21:35`: Fix a bug caused by wrong using of a variable in `scalable_graphics_view.py`.
- `2024/6/4 21:10`: Optimize Exception Handling. Connect bfs and dijkstra algorithm to GUI and test.
- `2024/6/5 13:10`: Modify the type of `map_size` in code to make it consistent with the type described in `API & Data Format`. 
Use try catch to handle an unexpected issue caused by multi-thread.
- `2024/6/5 16:00`: Update description of `API & Data Format`. Update some visual effects.
- `2024/6/6 17:35`: Apply bounding box to accelerate the algorithms. Link to DFS algorithm and test. Write warning of DFS algorithm when try to use it. 
Change appearance of map 'China'. Change passed parameter 'forbidden_area_coords_list' to a set.
- `2024/6/8 22:05`: Change the logic of adding, deleting elements and draw forbidden area(see new features in help page in GUI). 
Rename many things to fit Python naming conventions. Fix an error caused by close window when the sub thread is calculating. 
Add a stop button in GUI to terminate the calculation. Add two qss file to modify elements' style. Modify `connector.py` to link to the new backend.
- `2024/6/10 18:40`: Add hard-coded code for demonstration of rl algorithm. Add 'ALL' mode in GUI.
- `2024/6/12 13:30`: Remove rl part in GUI.
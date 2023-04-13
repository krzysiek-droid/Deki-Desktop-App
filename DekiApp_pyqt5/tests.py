import json

with open(fr'D:\CondaPy - Projects\PyGUIs\DekiApp_pyqt5\db_settings.json', 'r') as readObject:
    database_settings = json.load(readObject)

print(database_settings['subConstructions_columns'])
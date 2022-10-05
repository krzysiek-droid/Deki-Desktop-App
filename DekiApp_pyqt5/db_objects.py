import PyQt5.Qt
from PyQt5 import QtGui
from PyQt5.QtWidgets import *
import gnrl_database_con as database
import datetime
import shutil
import pathlib
import sys

'''
Podcza instalacji aplikacji, należy ją połączyc z konkretną bazą danych i serwerem tzn. znać nazwę bazy i kody dostępu.
'''
srv_files_filepath = r'D:\dekiApp\Deki_ServerFiles\constructions_database'
srv_wps_files_path = r'D:\dekiApp\Deki_ServerFiles\wps_database'
weld_specification = ['id', 'belonging_construction_tag', 'belonging_construction_ID', 'wps_number', 'weld_id_prefix',
                   'weld_id_generated', 'weld_id_suffix', 'joint_type', 'weld_continuity_type', 'all_around',
                   'field_weld', 'upper_sizeType', 'upper_size', 'upper_weld_type', 'upper_weld_face',
                   'upper_weld_quant', 'upper_length', 'upper_weld_spacing', 'double_sided', 'sided_sizeType',
                   'sided_size', 'sided_weld_type', 'sided_weld_face', 'sided_weld_quant', 'sided_length',
                   'sided_weld_spacing', 'tail_info', 'first_material', 'second_material', 'first_welded_part',
                   'second_welded_part', 'testing_methods']

class Construction:
    def __init__(self, companyName='deki', connected_database=None):
        print(f"\n-----------------------------------------------------------------{type(self)} INITIALIZED")
        self.table_name = None
        self.picture = None
        self.picturePath = None  # Path
        self.info = {}  # Dict
        self.stpModelPath = None
        self.pdfDocsPath = None
        self.db = database.Database() if connected_database is None else connected_database
        self.db_records = None
        self.company_name = companyName
        self.folderPath = None

    # returns number of rows in database table (self.table_name)
    def update_records_amount(self):
        if self.db.is_table(self.table_name):
            self.db_records = 0 if self.db.check_records_number(
                self.table_name) is None else self.db.check_records_number(
                self.table_name)
            return self.db_records
        else:
            print(f'Could not find table {self.table_name} in database.')
            self.db_records = 0
            return 0


class MainConstruction(Construction):
    def __init__(self, connected_database=None):
        super(MainConstruction, self).__init__(connected_database=connected_database)
        self.table_name = f"{self.company_name}_2022_mainConstructions"
        self.update_records_amount()
        self.mainConstruction = self

    def save_main_construction(self):
        if not self.db.is_table(self.table_name):
            self.db.create_table(self.table_name, list(self.info.keys()))
            print('database created.')
            self.save_main_construction()
        else:
            print('database found, adding...')
            self.folderPath = srv_files_filepath + fr'\{self.info["tag"]}'
            try:
                pathlib.Path.mkdir(pathlib.Path(self.folderPath))
                print(f'Directory {self.info["tag"]} created. ')
            except FileExistsError:
                print(f'Directory {self.info["tag"]} already exists.')

            dst_stpModelPath = self.folderPath + fr'\{self.info["tag"]}_cad.stp'
            self.stpModelPath = shutil.copy2(self.stpModelPath, dst_stpModelPath)
            print(f'STEP model copied and saved.-----', end=" ")
            dst_pdfDocsPath = self.folderPath + fr'\{self.info["tag"]}_docs.pdf'
            self.pdfDocsPath = shutil.copy2(self.pdfDocsPath, dst_pdfDocsPath)
            print(f'Docs copied and saved.-----', end=" ")
            self.picturePath = self.folderPath + fr'\{self.info["tag"]}_picture.png'
            self.picture.save(self.picturePath, 'png')
            # TODO add file creation confirmation notification with pathlib.Path.exist()
            print(f'CAD model picture saved.-----')
            self.db.insert(self.table_name, list(self.info.values()))

    def load_info(self, construct_id):
        print(f'Loading data for mainConstruction from: {self.table_name} - Construction ID: {construct_id}....',
              end=" ")
        keys = self.db.get_columns_names(self.table_name)
        values = self.db.get_row(self.table_name, 'id', f'{str(construct_id)}')[0]
        self.info = {k: v for k, v in zip(keys, values)}
        self.folderPath = srv_files_filepath + fr'\{self.info["tag"]}'
        self.picturePath = pathlib.Path(self.folderPath + fr'\{self.info["tag"]}_picture.png')
        # checks if picture is available
        if not pathlib.Path(self.folderPath + fr'\{self.info["tag"]}_picture.png').exists():
            print(f"Picture not found at given location!")
            raise FileNotFoundError
        self.picture = QtGui.QPixmap()
        self.picture.load(str(self.picturePath))
        self.stpModelPath = self.folderPath + fr'\{self.info["tag"]}_cad.stp'
        self.pdfDocsPath = self.folderPath + fr'\{self.info["tag"]}_docs.pdf'
        print(f'Construction {self.info["name"]}-{self.info["tag"]} loaded.')


class SubConstruction(Construction):
    def __init__(self, parentConstruction=None, connected_database=None):
        super(SubConstruction, self).__init__(connected_database=connected_database)
        self.table_name = f'{self.company_name}_2022_SubConstructions'
        self.parent_construction = parentConstruction
        self.mainConstruction = parentConstruction.mainConstruction if parentConstruction is not None else None

    def save_subConstruction(self):
        if not self.db.is_table(self.table_name):
            self.db.create_table(self.table_name, list(self.info.keys()))
            print('database created.')
            self.save_subConstruction()
        else:
            print('database found, adding...')
            # TODO add folder for main construction creation, for organizing purposes
            self.folderPath = self.parent_construction.folderPath + fr'\{self.info["tag"]}'
            try:
                pathlib.Path.mkdir(pathlib.Path(self.folderPath))
                print(f'Directory {self.info["tag"]} created. ')
            except FileExistsError:
                print(f'Directory {self.info["tag"]} already exists.')
            dst_stpModelPath = self.folderPath + fr'\{self.info["tag"]}_cad.stp'
            self.stpModelPath = shutil.copy2(self.stpModelPath, dst_stpModelPath)
            print(f'STEP model copied and saved.-----', end=" ")
            dst_pdfDocsPath = self.folderPath + fr'\{self.info["tag"]}_docs.pdf'
            self.pdfDocsPath = shutil.copy2(self.pdfDocsPath, dst_pdfDocsPath)
            print(f'Docs copied and saved.-----', end=" ")
            self.picturePath = self.folderPath + fr'\{self.info["tag"]}_picture.png'
            self.picture.save(self.picturePath, 'png')
            # TODO add file creation confirmation notification with pathlib.Path.exist()
            print(f'CAD model picture saved.-----')
            self.db.insert(self.table_name, list(self.info.values()))

    def load_info(self, construct_id):
        print(f'Loading data for subConstruction from: {self.table_name}, id: {construct_id}.....', end=" ")
        keys = self.db.get_columns_names(self.table_name)
        values = self.db.get_row(self.table_name, 'id', f'{str(construct_id)}')[0]
        self.info = {k: v for k, v in zip(keys, values)}
        self.mainConstruction = MainConstruction(connected_database=self.db)
        self.mainConstruction.load_info(self.info['main_construction_id'])
        print(f'mainConstruction loaded in Subconstruction object.')
        self.parent_construction = self.mainConstruction if self.info['parent_construction_id'] is None \
            else SubConstruction(self.info['parent_construction_id'])
        self.folderPath = self.parent_construction.folderPath + fr'\{self.info["tag"]}'
        self.picturePath = pathlib.Path(self.folderPath + fr'\{self.info["tag"]}_picture.png')
        # checks if picture is available
        if not pathlib.Path(self.folderPath + fr'\{self.info["tag"]}_picture.png').exists():
            print(f"Picture not found at given location!")
            raise FileNotFoundError
        self.picture = QtGui.QPixmap()
        self.picture.load(str(self.picturePath))
        self.stpModelPath = self.folderPath + fr'\{self.info["tag"]}_cad.stp'
        self.pdfDocsPath = self.folderPath + fr'\{self.info["tag"]}_docs.pdf'
        print(f'SubConstruction {self.info["name"]}-{self.info["tag"]} loaded.')


class weldObject:
    def __init__(self, parentConstructName='deki', connected_database=None, table_name=None):
        print(f"\n-----------------------------------------------------------------{type(self)} INITIALIZED")
        self.table_name = f"{parentConstructName}_modelWelds" if table_name is None else table_name
        self.db = database.Database() if connected_database is None else connected_database
        self.db_records = self.update_records_amount()
        self.wps_filepath = None

        if self.db.is_table(self.table_name):
            self.info = dict.fromkeys(self.db.get_columns_names(self.table_name))
        else:
            print(f'{self} -- table {self.table_name} not found. Creating a table...')
            self.info = dict.fromkeys(weld_specification)
            self.db.create_table(self.table_name, self.info)
            print(f'{self} -- {self. table_name} created.')

    # returns number of rows in database table (self.table_name)
    def update_records_amount(self):
        print(f'updating records amount in table {self.table_name}')
        if self.db.is_table(self.table_name):
            self.db_records = 0 if self.db.check_records_number(
                self.table_name) is None else self.db.check_records_number(
                self.table_name)
            return self.db_records
        else:
            print(f'Could not find table {self.table_name} in database.')
            self.db_records = None
            return None

    def load_info(self, weld_id):
        print(f'Loading data for weld from: {self.table_name} - Weld ID: {weld_id}....',
              end=" ")
        keys = self.db.get_columns_names(self.table_name)
        values = self.db.get_row(self.table_name, 'id', f'{str(weld_id)}')[0]
        self.info = {k: v for k, v in zip(keys, values)}
        self.wps_filepath = srv_wps_files_path + fr'\{self.info["wps_number"]}.pdf'
        print(f'Weld info loaded')

    def save_weld(self, new_weld_DbName, pathToWpsFile):
        dst_wpsDocsPath = srv_wps_files_path + fr'\{self.info["wps_number"]}.pdf'
        if self.db.is_table(new_weld_DbName):
            print('Database for welds found. Adding new weld...')
            # Do not update db_records to avoid multpile inserting of same weldObject into db
            print(f'Columns/Values length check:  '
                  f'{len(self.db.get_columns_names(new_weld_DbName))} == {len(self.info.values())}?')
            self.info['id'] = int(self.db_records) + 1
            self.db.insert(new_weld_DbName, list(self.info.values()))
            print(f'Weld inserted with id: {self.info["id"]}')
            if pathToWpsFile is not None:
                self.wps_filepath = shutil.copy2(pathToWpsFile, dst_wpsDocsPath)
        else:
            print('Database for welds not found. Creating new table in Database...')
            self.db.create_table(new_weld_DbName, self.info.keys())
            print(f'Table {new_weld_DbName} created. Adding weld...')
            self.info['id'] = int(self.db_records) + 1
            self.db.insert(new_weld_DbName, list(self.info.values()))
            print(f'Weld inserted with id: {self.info["id"]}')
            if pathToWpsFile is not None:
                self.wps_filepath = shutil.copy2(pathToWpsFile, dst_wpsDocsPath)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    subCons = weldObject('test1_modelWelds')
    subCons.info['wps_number'] = '135_2020_5'
    subCons.save_weld('test1_modelWelds', r'D:/dekiApp/DKI_MVP_01/WPSy/135_2020_5.pdf')

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting the App")

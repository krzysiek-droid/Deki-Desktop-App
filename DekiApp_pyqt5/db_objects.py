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
        # self.parent_construction = MainConstruction().load_info(1) if parentConstruction is None else
        # parentConstruction
        self.parent_construction = parentConstruction
        self.mainConstruction = parentConstruction.mainConstruction if parentConstruction is not None else None

        # if parentConstruction is None:
        #     self.load_info(1)

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
    def __init__(self, companyName='deki', connected_database=None, table_name=None):
        print(f"\n-----------------------------------------------------------------{type(self)} INITIALIZED")
        self.table_name = f"{companyName}_2022_modelWelds" if table_name is None else table_name
        self.info = {}  # Dict
        self.db = database.Database() if connected_database is None else connected_database
        self.db_records = self.update_records_amount()

        print(f'Columns in the database: ')
        print(self.db.get_columns_names(self.table_name))

    # returns number of rows in database table (self.table_name)
    def update_records_amount(self):
        print('updating records amount')
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
        print(f'Loading data for modelWeld from: {self.table_name} - Wled ID: {weld_id}....',
              end=" ")
        keys = self.db.get_columns_names(self.table_name)
        values = self.db.get_row(self.table_name, 'id', f'{str(weld_id)}')[0]
        self.info = {k: v for k, v in zip(keys, values)}
        print(f'Construction {self.info["name"]}-{self.info["tag"]} loaded.')


if __name__ == "__main__":

    app = QApplication(sys.argv)
    subCons = weldObject()

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting the App")

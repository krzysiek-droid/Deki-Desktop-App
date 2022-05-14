import PyQt5.Qt
from PyQt5 import QtGui

import gnrl_database_con as database
import datetime
import shutil
import pathlib

'''
Podcza instalacji aplikacji, należy ją połączyc z konkretną bazą danych i serwerem tzn. znać nazwę bazy i kody dostępu.
Następnie tworzona jest baza danych dla wszystkich konstrukcji głównych o tagach: 
<Nazwa firmy>_<rok założenia>_constructions
Wszystkie kolejne tabele muszą mieć nazwę firmy jako pierwszy String w nazwa tj.: <nazwa firmy>_<...>
'''
srv_files_filepath = r'D:\dekiApp\Deki_ServerFiles\constructions_database'


class Construction:
    def __init__(self):
        self.company_name = 'deki'
        self.table_name = f'{self.company_name}_2022_constructions'
        self.picture = None
        self.picturePath = None  # Path
        self.info = {}  # Dict
        self.stpModelPath = None
        self.pdfDocsPath = None
        self.subassemblies = None  # List
        self.db = database.Database()
        self.db_records = None

        self.update_records()

    def update_records(self):
        table_name = f'{self.company_name}_2022_constructions'
        if self.db.is_table(table_name):
            self.db_records = 0 if self.db.check_records_number(table_name) is None else self.db.check_records_number(
                table_name)
            return self.db_records
        else:
            print(f'Could not find table {table_name} in database')
            self.db_records = 0
            return 0

    def save_construction(self):
        if not self.db.is_table(f'{self.company_name}_2022_constructions'):
            self.db.create_table(f'{self.company_name}_2022_constructions', list(self.info.keys()))
            print('database created.')
            self.save_construction()
            self.update_records()
        else:
            print('database found, adding...')
            dst_stpModelPath = srv_files_filepath + fr'\{self.info["tag"]}_cad.stp'
            print(self.stpModelPath)
            self.stpModelPath = shutil.copy2(self.stpModelPath, dst_stpModelPath)
            print(f'STEP model copied and saved.')
            dst_pdfDocsPath = srv_files_filepath + fr'\{self.info["tag"]}_docs.pdf'
            self.pdfDocsPath = shutil.copy2(self.pdfDocsPath, dst_pdfDocsPath)
            print(f'Docs copied and saved.')
            self.picturePath = srv_files_filepath + fr'\{self.info["tag"]}_picture.png'
            self.picture.save(self.picturePath, 'png')
            print(f'CAD model picture saved.')
            self.db.insert(f'{self.company_name}_2022_constructions', list(self.info.values()))
            self.update_records()

    def load_info(self, construct_id):
        print(f'loading data from: {self.table_name}, id: {construct_id}')
        keys = self.db.get_columns_names(self.table_name)
        values = self.db.get_row(self.table_name, 'id', f'{str(construct_id)}')[0]
        self.info = {k: v for k, v in zip(keys, values)}
        self.picturePath = pathlib.Path(srv_files_filepath + fr'\{self.info["tag"]}_picture.png')
        self.picture = QtGui.QPixmap()
        self.picture.load(str(self.picturePath))
        self.stpModelPath = srv_files_filepath + fr'\{self.info["tag"]}_cad.stp'
        self.pdfDocsPath = srv_files_filepath + fr'\{self.info["tag"]}_docs.pdf'
        print(f'picture loaded.')


class SubConstruction(Construction):
    def __init__(self):
        super(SubConstruction, self).__init__()


if __name__ == "__main__":
    const = Construction()
    const.load_info(2)

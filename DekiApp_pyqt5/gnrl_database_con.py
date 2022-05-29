import mariadb
import sys
import pandas as pd


with open(r"D:\CondaPy - Projects\PyGUIs\DekiApp_pyqt5\DekiResources\database_con.txt",
          'r', encoding="UTF-8") as f:
    db_credentials = f.read().split("\n")
    for i in range(len(db_credentials)):
        tmp = db_credentials[i].split(" = ")[1]
        db_credentials[i] = tmp

DATABASE_HOST = db_credentials[0]
DATABASE_USER = db_credentials[1]
DATABASE_PASSWORD = db_credentials[2]
DATABASE_NAME = db_credentials[3]
PORT = int(db_credentials[4])


def validate_text(text):
    tmp_text = text
    if text.isalnum():
        print(f"Text is valid: {text}")
        return text
    else:
        for letter in text:
            if not letter.isalnum():
                tmp_text = tmp_text.replace(letter, '_')
        return tmp_text


class Database:
    def __init__(self):
        try:
            self.conn = mariadb.connect(
                user=DATABASE_USER,
                password=DATABASE_PASSWORD,
                host=DATABASE_HOST,
                port=PORT,
                database=DATABASE_NAME
            )
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(1)

        self.cur = self.conn.cursor()
        self.cur.execute("SELECT version();")
        print(f'Database connection established, db version: {self.cur.fetchone()[0]}')

    def __del__(self):
        self.cur.close()
        self.conn.close()
        print(f'Database connection closed')

    def insert(self, table_name, values: list):
        table_name = validate_text(table_name)
        try:
            self.cur.execute(f"INSERT INTO {table_name} ({','.join([_ for _ in self.get_columns_names(f'{table_name}')])})"
                             f" VALUES ({','.join(['%s' for _ in values])})", values)
        except ValueError:
            print(f'Values has to be inserted as a py list (not any other arrays!).')
        self.conn.commit()

    # returns a pandas DataFrame from given table and columns (as a list of strings)
    # returns all columns if given '*'
    def get_by_column(self, table_name, *columns):
        if len(columns) > 1:
            columns_txt = ','.join(columns)
        elif columns[0] == '*':
            columns_txt = columns[0]
            columns = self.get_columns_names(table_name)
            cols_names = []
            for name in columns:
                cols_names.append(name)
            columns = cols_names
        else:
            columns_txt = ''.join(columns)

        qry = f'SELECT {columns_txt} FROM {table_name}'
        print(qry)
        self.cur.execute(qry)

        output_list = []
        minor_list = []
        for tuple_value in self.cur.fetchall():
            for value in tuple_value:
                minor_list.append(value)
            output_list.append(minor_list)
            minor_list = []

        df = pd.DataFrame(columns=columns)
        for record in output_list:
            series = pd.Series(record, index=columns)
            df = df.append(series, ignore_index=True)

        return df

    # Load data from xlsx file (excel) to given table
    def insertDB_from_xls(self, table_name, xls_path):
        df_ISO = pd.read_excel(xls_path)
        for index, row in df_ISO.iterrows():
            text_records = ','.join(map(str, row)).replace(" ", '')
            self.insert(table_name, text_records)
        self.table_into_DF(table_name)

    def insertDB_from_csv(self, table_name, csv_path, csv_separator):
        table_name = validate_text(table_name)
        df = pd.read_csv(csv_path, sep=csv_separator)
        if self.is_table(table_name):
            print(f"Table {table_name} already exist. Inserting data....")
        else:
            self.create_table(table_name, df.columns.tolist())
            print(f"Table {table_name} created. Inserting data....")

        for index, row in df.iterrows():
            text_records = ','.join(map(str, row)).replace(" ", '')
            self.insert(table_name, text_records)

        self.table_into_DF(table_name)

    def delete_records(self, table_name):
        qry = f'DELETE FROM {table_name}'
        self.cur.execute(qry)
        self.conn.commit()
        print(f"Table {table_name} fully cleared.")

    def table_into_DF(self, table_name):
        table_name = validate_text(table_name)
        qry = f'SELECT * FROM {table_name}'
        self.cur.execute(qry)
        records = self.cur.fetchall()
        table_cols = self.get_columns_names(table_name)

        df = pd.DataFrame(columns=table_cols)
        for record in records:
            series = pd.Series(record, index=table_cols)
            df = df.append(series, ignore_index=True)
        return df

    def get_row(self, table_name: str, col_name: str, row_pos: str):
        table_name = validate_text(table_name)
        qry = f'SELECT * FROM {table_name} WHERE {col_name} = {row_pos}'
        self.cur.execute(qry)
        row_data = self.cur.fetchall()
        return row_data

    def get_columns_names(self, table_name):
        table_cols = f"SELECT column_name FROM information_schema.columns WHERE table_name='{table_name}' " \
                     f"ORDER BY ORDINAL_POSITION"
        self.cur.execute(table_cols)
        columns = []
        for column in self.cur.fetchall():
            columns.append(column[0])

        return columns

    def create_table(self, table_name, columns):
        columnList = []
        table_name = validate_text(table_name)
        for columnName in columns:
            if not columnName.isalpha():
                print(f"Wrong column name: {columnName}", end=", ")
                if columnName == ' ' or columnName == "id":
                    raise ValueError(f'Wrong column name: {columnName}')
                tmp_columnName = str(columnName)
                for letter in columnName:
                    if not letter.isalpha():
                        if letter == ".":
                            tmp_columnName = tmp_columnName.replace(letter, '')
                        tmp_columnName = tmp_columnName.replace(letter, '_')
                        print(f"Changed for: {tmp_columnName}")
                columnList.append(tmp_columnName + ' VARCHAR(200)')
                continue

            columnList.append(columnName + ' VARCHAR(200)')

        cols = ','.join([column for column in columnList])
        print(f"Proceeding table creation with columns: {cols}")
        if not self.is_table(table_name):
            id_column = columnList[0].split(' ')[0]
            qry = f"CREATE TABLE {table_name} ({cols}, PRIMARY KEY({id_column}))"
            self.cur.execute(qry)
            self.conn.commit()
            print(f"Table {table_name} has been created.")
        else:
            print(f"Table could not been created, because another table with the same name exists")
            return 0

    # searches if given table name exists in SQL server tables with table_schema=public
    # Boolean
    def is_table(self, table_name):
        table_name = validate_text(table_name).lower()
        tables_list = self.show_tables(DATABASE_NAME)
        for table in tables_list:
            if table[0] == table_name:
                # print(f"Table {table_name} found in database.")
                # print(f"Tables list in database: {tables_list}")
                return True
        print(f"Table {table_name} not found in database. Tab list: {tables_list}")
        return False

    def show_tables(self, database_name):
        qry = f"SHOW TABLES FROM {database_name}"
        self.cur.execute(qry)
        return self.cur.fetchall()

    def add_column(self, table_name, column_name, data_type, values):
        qry = f"ALTER TABLE {table_name} ADD {column_name} {data_type}"
        self.cur.execute(qry)
        print(f"Column {column_name} has been added to table {table_name}")

    def check_records_number(self, table_name):

        self.cur.execute(f'SELECT * from {table_name}')
        records = self.cur.fetchall()
        if records is not None:
            return len(records)
        else:
            return 0


if __name__ == "__main__":
    db = Database()

    print(db.show_tables(DATABASE_NAME))
    dct = {
        'name': 'Zbiornik LNG',
        'tag': 'self.constructTagLine.text()',
        'number': 'DKI_LNG3200_MS_000',
        'owner': 'self.constructOwnerLine.text()',
        'localization': 'self.constructLocalizationLine.text()',
        'material': 'self.constructMaterialLine.text()',
        'additional_info': 'NaN',
        'subcontractor': "NaN",
        'sub_contact': "NaN",
        'construct_type': 'str(self.constructTypeCombo.currentText())',
        'quality_norm': 'str(self.constructQualityNormCombo.currentText())',
        'quality_class': 'str(self.constructQualityClassCombo.currentText())',
        'tolerances_norm': 'str(self.constructTolerancesNormCombo.currentText())',
        'tolerances_level': 'str(self.constructTolerancesLevelCombo.currentText())'}

    db.create_table('test_2022_constructions',
                    ['tag', 'number', 'name', 'owner', 'localization',
                     'material', 'additional_info', 'subcontractor', 'sub_contact', 'construct_type',
                     'quality_norm', 'quality_class', 'tolerances_norm', 'tolerances_level'])
    db.insert('test_2022_constructions', dct.values())

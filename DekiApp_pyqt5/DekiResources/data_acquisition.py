import pandas as pd

import gnrl_database_con as database

construction_info = {
    "name": "",
    "owner": "",
    "tag": "",
    "localization": "",
    "general Tolerances": "",
    "construction_type": "",
    "main_material": "",
    "subassemblies": "",
    "quality_norm": "",
    "quality_class": "",
}


db = database.Database()
dataframe = db.get_by_column('CL01_MVP', '*')

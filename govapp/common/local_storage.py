# Standard
import os
import pathlib
import tempfile
import shutil

# Third-Party
from django import conf

class LocalStorage():
    def __init__(self):
            self.pending_import_path = conf.settings.PENDING_IMPORT_PATH
            self.data_storage_path = conf.settings.DATA_STORAGE        

    def get_pending_import_path(self):
            return self.pending_import_path
    
    def get_data_storage_path(self):
            return self.data_storage_path

    def get_path(self, filepath):                      
            return self.pending_import_path+filepath
    def get_path_suffix(self,filepath):
            return pathlib.Path(filepath).suffix
    
    def move_to_storage(self, from_file_location, to_file_location):
        try:
            #os.rename(from_file_location,to_file_location)
            shutil.move(from_file_location,to_file_location)
        except Exception as e:
            print (e)
            return False
        return True
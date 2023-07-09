import os


#get the project directory
CURRENT_FILE_PATH = os.path.abspath(__file__)
PARENT_DIRECTORY = os.path.dirname(CURRENT_FILE_PATH)
PROJECT_DIRECTORY = os.path.abspath(os.path.join(PARENT_DIRECTORY, '..'))




class PictureUploader:

    def __init__(self,target,target_name):
        self.target = target
        self.target_name = target_name
        self.images_users_folder = os.path.join(PROJECT_DIRECTORY, 'images',self.target,self.target_name)

    def delete_file(self,filepath):
        
        path_to_delete = f"{PROJECT_DIRECTORY}/images/{filepath}"
        if os.path.exists(path_to_delete):
            os.remove(path_to_delete) 
        

    def load_file(self,file):
        filename = file.filename
        filepath = os.path.join(self.images_users_folder, filename)

  
        # Read the file contents and save it
        file_contents = file.read()
        with open(filepath, 'wb') as f:
            f.write(file_contents) 

        return filename
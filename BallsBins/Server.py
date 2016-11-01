class Server:
    """Define the server class"""

#    files_list = []
#    load = 0
#    id = [] # server identifier


    def __init__(self,identity):
        self.id = identity # server identifier
        self.load = 0 # number of balls in the server
        self.files_list = [] # list of available files in the server


    def set_files_list(self,list):
        self.files_list = list


    def get_files_list(self):
        return self.files_list


    def add_load(self):
        self.load = self.load + 1


    def get_load(self):
        return self.load


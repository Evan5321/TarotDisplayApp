import os
import numpy as np

class FileFunction:

    def  save_whole_array(self,Cards,file_path):
        print(Cards,file_path)
        file_obj = open(file_path, 'w')
        for i in range(len(Cards)):
            text = str(Cards[i][1]) + ' ' + str(Cards[i][2]) + " " + str(Cards[i][3]) + " " + str(Cards[i][4]) + ' ' + str(Cards[i][5]) + " "  '\n'
            #将text追加到文件中
            file_obj.write(text)
        file_obj.close()
        

    def read_whole_array(self,file_path):
        pass


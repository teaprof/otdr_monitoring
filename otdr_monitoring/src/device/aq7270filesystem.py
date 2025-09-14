from aq7270protocol import AQ7270protocol

class AQ7270filesystem(AQ7270protocol):
    '''This class is not tested after major changes, but I hope it works!'''
    def __init__(self, dev = None):
        super().__init__(dev)
        pass

    def downloadFile(self, filename):
        print(F"Downloading file {filename}")
        self.cmd(self.cmdFileFileName, '"' + filename + '"')
        filesize = self.cmd(self.askFileFileSize)
        print(filesize)

        self.send(self.askFileFileGet)
        data = self.receivefile()
        return data

    def listFiles(self):
        filelist = self.cmd(self.askFileFolderList)
        filelist = filelist.split(',')
        filelist = filelist[1:] #remove the first record which contains the number of files

        #Parse respond
        subfolders = []
        files = []
        for f in filelist:
            if f[-1] == chr(0x0A):
                f = f[0:-1]
            if f[-1] == '/':
                subfolders.append(f)
            else:
                files.append(f)
        return [subfolders, files]

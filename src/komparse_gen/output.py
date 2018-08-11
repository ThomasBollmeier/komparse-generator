import os

class Output(object):
    
    def __init__(self):
        pass
    
    def open(self):
        pass
    
    def close(self):
        pass
    
    def write(self, text):
        raise NotImplementedError

    def writeln(self, text):
        self.write(text + "\n")
        

class StdOut(Output):
    
    def __init__(self):
        Output.__init__(self)
    
    def write(self, text):
        print(text, end="")
        
        
class FileOut(Output):
    
    def __init__(self, filepath):
        Output.__init__(self)
        self._filepath = filepath
        self._fp = None
        
    def open(self):
        self._fp = open(self._filepath, "w")
        
    def close(self):
        if self._fp:
            self._fp.close()
            self._fp = None
    
    def write(self, text):
        self._fp.write(text)
    
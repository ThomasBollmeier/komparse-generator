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
        self.write(text + os.linesep)
        

class StdOut(Output):
    
    def __init__(self):
        Output.__init__(self)
    
    def write(self, text):
        print(text, end="")
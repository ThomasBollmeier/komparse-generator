import sys
import os

def read_file_content(filepath):
    content = ""
    fp = open(filepath, "r")
    lines = fp.readlines()
    fp.close()
    for line in lines:
        content += line
    return content

bindir = os.path.dirname(__file__)
srcdir = bindir + os.path.sep + ".." + os.path.sep + "src"
srcdir = os.path.abspath(srcdir)
sys.path.insert(0, srcdir)
from komparse_gen import Generator, StdOut, FileOut

num_args = len(sys.argv) - 1
if num_args == 1:
    grammar_file = sys.argv[1]
    output = StdOut()
elif num_args == 2:
    grammar_file = sys.argv[1]
    output = FileOut(sys.argv[2])
else:
    print("Syntax: python komparsegen.py <grammar_file> [<output_file>]")
    exit(1)

prefix = os.path.basename(grammar_file).split(".")[0]
code = read_file_content(grammar_file)

Generator().generate(code, prefix, output)

exit(0)
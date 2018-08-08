from komparse import Parser
from grammar import Grammar
from output import StdOut


class Generator(object):
    
    def __init__(self, tabsize=4):
        self._parser = Parser(Grammar())
        self._tabsize = tabsize
    
    def generate(self, grammar_source, grammar_clsname, output=StdOut()):
        ast = self._parser.parse(grammar_source)
        if not ast:
            raise Exception(self._parser.error())
        self._output = output
        self._indent_level = 0
        
        self._wrt_imports()
        self._writeln()
        self._writeln()
        self._writeln("class {}(Grammar):".format(grammar_clsname))
        self._indent()
        self._writeln()
        self._writeln("def __init__(self):")
        self._indent()
        self._writeln("Grammar.__init__(self)")
        self._writeln("self._init_tokens()")
        self._writeln("self._init_rules()")
        self._dedent()
        self._writeln()
        self._wrt_init_tokens()
        self._writeln()
        self._wrt_init_rules()
        
    def _wrt_init_tokens(self):
        self._writeln("def _init_tokens(self):")
        self._indent()
        self._writeln("pass")
        self._dedent()
        
    def _wrt_init_rules(self):
        self._writeln("def _init_rules(self):")
        self._indent()
        self._writeln("pass")
        self._dedent()
        
    def _wrt_imports(self):
        self._writeln("from komparse import Grammar, Sequence, OneOf, \\")
        self._indent()
        self._writeln("Optional, OneOrMore, Many")
        self._dedent()
        
    def _writeln(self, line=""):
        self._output.writeln(" " * self._indent_level * self._tabsize + line)
        
    def _indent(self):
        self._indent_level += 1
        
    def _dedent(self):
        self._indent_level -= 1
        
        
        
if __name__ == "__main__":
    
    grammar_source = """
    -- Test grammar
    
    -- tokens:
    
    comment '//' '\\n';
    
    string '#'' '#'' STR;
    string '{' '}' '\\' TEMPLATE_STR;
    
    token PLUS '\+';
    token MULT '\*';
    token LPAR '\(';
    token RPAR '\)';
    token INT '\d+';
    
    -- production rules:
    
    @start
    expr -> p#prod (PLUS p#prod)*;
    
    prod -> f#factor (MULT f#factor)*;
    
    factor -> val#INT | LPAR val#expr RPAR;
    """
    
    Generator().generate(grammar_source, "ExprGrammar", StdOut())

from komparse import Parser
from grammar import Grammar

class Generator(object):
    
    def __init__(self):
        self._parser = Parser(Grammar())
    
    def generate(self, grammar_source, output):
        ast = self._parser.parse(grammar_source)
        if ast:
            print(ast.to_xml())
        else:
            raise Exception(self._parser.error())
        
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
    
    Generator().generate(grammar_source, None)

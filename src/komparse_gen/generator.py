from komparse import Parser
from grammar import Grammar
from output import StdOut


class Generator(object):
    
    def __init__(self, tabsize=4):
        self._parser = Parser(Grammar())
        self._tabsize = tabsize
    
    def generate(self, grammar_source, prefix, output=StdOut()):
        
        ast = self._parser.parse(grammar_source)
        if not ast:
            raise Exception(self._parser.error())
        
        self._output = output
        self._indent_level = 0
        
        tokens, rules = self._get_tokens_and_rules(ast)
        
        self._wrt_imports()
        self._writeln()
        self._writeln()
        self._writeln("class {}Grammar(Grammar):".format(prefix.capitalize()))
        self._indent()
        self._writeln()
        self._writeln("def __init__(self):")
        self._indent()
        self._writeln("Grammar.__init__(self)")
        self._writeln("self._init_tokens()")
        self._writeln("self._init_rules()")
        self._dedent()
        self._writeln()
        self._wrt_init_tokens(tokens)
        self._writeln()
        self._wrt_init_rules(rules)
        self._writeln()
        self._writeln()
        self._dedent()
        self._writeln("class {}Parser(Parser):".format(prefix.capitalize()))
        self._indent()
        self._writeln()
        self._writeln("def __init__(self):")
        self._indent()
        self._writeln("Parser.__init__(self, {}Grammar())".format(prefix.capitalize()))
        self._writeln()
        self._dedent()
        
    def _get_tokens_and_rules(self, ast):
        tokens = []
        rules = []
        for child in ast.get_children():
            if child.name == "ruledef":
                rules.append(child)
            else:
                tokens.append(child)
        return tokens, rules
        
    def _wrt_init_tokens(self, tokens):
        self._writeln("def _init_tokens(self):")
        self._indent()
        for token in tokens:
            if token.name == "commentdef":
                self._wrt_commentdef(token)
            elif token.name == "stringdef":
                self._wrt_stringdef(token)
            elif token.name == "tokendef":
                self._wrt_tokendef(token)
        self._dedent()
        
    def _wrt_commentdef(self, commentdef):
        start, end = commentdef.get_children()
        line = "self.add_comment('{}', '{}')".format(start.value, end.value)
        self._writeln(line)
        
    def _wrt_stringdef(self, stringdef):
        children = stringdef.get_children()
        if len(children) == 3:
            id_, start, end = map(lambda it: it.value, children)
            line = "self.add_string('{}', '{}', name='{}')".format(start, end, id_)
        else:
            id_, start, end, esc = map(lambda it: it.value, children)
            line = "self.add_string('{}', '{}', '{}', '{}')".format(start, end, esc, id_)
        self._writeln(line)
        
    def _wrt_tokendef(self, tokendef):
        id_, regex = tokendef.get_children()
        line = "self.add_token('{}', '{}')".format(id_.value, regex.value)
        self._writeln(line)
        
    def _wrt_init_rules(self, rules):
        self._writeln("def _init_rules(self):")
        self._indent()
        self._writeln("pass")
        self._dedent()
        
    def _wrt_imports(self):
        self._writeln("from komparse import Parser, Grammar, Sequence, OneOf, \\")
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
    
    string '\#'' '\#'' STR;
    string '{' '}' '\\\\' TEMPLATE_STR;
    
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
    
    Generator().generate(grammar_source, "expr", StdOut())

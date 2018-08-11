from komparse import Parser
from .grammar import Grammar
from .output import StdOut, FileOut


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
        self._num_seqs = 0
        self._sequences = {}
        self._num_oneofs = 0
        self._oneofs = {}
        
        tokens, rules = self._get_tokens_and_rules(ast)
        
        self._output.open()
        
        try:        
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
            self._wrt_sequences()
            self._wrt_oneofs()
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
        except Exception as exc:
            self._output.close()
            raise exc
            
        self._output.close()
        
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
        for rule in rules:
            self._wrt_rule(rule)
        self._dedent()
        
    def _wrt_rule(self, rule):
        id_, content = rule.get_children()
        call = self._get_call(content)
        is_start = rule.has_attr('start') and rule.get_attr('start') == "true"
        if not is_start:
            line = "self.rule('{}', {})".format(id_.value, call)
        else:
            line = "self.rule('{}', {}, is_root=True)".format(id_.value, call)
        self._writeln(line)
        
    def _wrt_internal_funcs(self, fn_dict):
        names = list(fn_dict.keys())
        names.sort()
        for name in names:
            self._writeln("def {}(self):".format(name))
            self._indent()
            for line in fn_dict[name]:
                self._writeln(line)
            self._dedent()
            self._writeln()
            
    def _wrt_sequences(self):
        self._wrt_internal_funcs(self._sequences)
        
    def _wrt_oneofs(self):
        self._wrt_internal_funcs(self._oneofs)

    def _get_call(self, content):
        name = content.name
        id_ = ""
        if name == "oneof":
            self._num_oneofs += 1
            func_name = "_oneof_{}".format(self._num_oneofs)
            self._oneofs[func_name] = self._get_func_body(content)
        elif name == "sequence":
            self._num_seqs += 1
            func_name = "_seq_{}".format(self._num_seqs)
            self._sequences[func_name] = self._get_func_body(content)
        elif name in ["ruleref", "tokenref"]:
            func_name = content.value
            if content.has_attr('data-id'):
                id_ = content.get_attr('data-id')
        else:
            raise RuntimeError("Unknown content")
        
        if not id_:
            call = "self." + func_name + "()"
        else:
            call = "self." + func_name + "('" + id_ + "')"
            
        if content.has_attr('cardinality'):
            card = content.get_attr('cardinality')
            call = {
                "optional": "Optional(" + call + ")",
                "one-or-more": "OneOreMore(" + call + ")",
                "many": "Many(" + call + ")"
            }[card]
                
        return call
    
    def _get_func_body(self, content):
        lines = []
        if content.name == "oneof":
            lines.append("return OneOf(")
        elif content.name == "sequence":
            lines.append("return Sequence(")
        else:
            raise RuntimeError("Unknown content")
        children = content.get_children()
        max_idx = len(children) - 1 
        left_pad = " " * self._tabsize
        for idx, child in enumerate(children):
            line = left_pad + self._get_call(child)
            if idx < max_idx:
                line += ","
            else:
                line += ")"
            lines.append(line)
        return lines
            
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
    
    Generator().generate(grammar_source, "expr", FileOut("expr_parser.py"))

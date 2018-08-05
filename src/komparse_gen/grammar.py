"""
Grammar for parser generator
"""

from komparse import Grammar as BaseGrammar, \
    Sequence, OneOf, OneOrMore, Optional, Many, Ast

class Grammar(BaseGrammar):
    
    def __init__(self):
        BaseGrammar.__init__(self)
        self._init_tokens()
        self._init_rules()
        
    def _init_tokens(self):
        
        self.add_comment("--", "\n")
        self.add_string("'", "'", '#', 'STR')
        
        self.add_keyword('comment')
        self.add_keyword('string')
        self.add_keyword('token')
        self.add_keyword('start')
        
        self.add_token('ARROW', "->")
        self.add_token('LPAR', "\(")
        self.add_token('RPAR', "\)")
        self.add_token('QUESTION_MARK', "\?")
        self.add_token('PLUS', "\+")
        self.add_token('ASTERISK', "\*")
        self.add_token('PIPE', "\|")
        self.add_token('SEMICOLON', ";")
        self.add_token('AT', "@")
        self.add_token('TOKEN_ID', "[A-Z][A-Z0-9_]*")
        self.add_token('RULE_ID', "[a-z][a-z0-9_]*")
    
    def _init_rules(self):
        
        self.rule('komparse_grammar', OneOrMore(OneOf(
            self.tokenrule(),
            self.productionrule()
        )), is_root=True)
        
        self.rule('tokenrule', OneOf(
            self.commentdef(),
            self.stringdef(),
            self.tokendef()
        ))
        
        self.rule('commentdef', Sequence(
            self.COMMENT(),
            self.STR('start'),
            self.STR('end'),
            self.SEMICOLON()
        ))
    
        self.rule('stringdef', Sequence(
            self.STRING(),
            self.STR('start'),
            self.STR('end'),
            Optional(self.STR('escape')),
            Optional(self.TOKEN_ID('token_id')),
            self.SEMICOLON()
        ))
        
        self.rule('tokendef', Sequence(
            self.TOKEN(),
            self.TOKEN_ID('token_id'),
            self.STR('regex'),
            self.SEMICOLON()
        ))
        
        self.rule('productionrule', Sequence(
            Optional(self.annotation('annot')),
            self.RULE_ID('rule_id'),
            self.ARROW(),
            self.branches('rhs'), 
            self.SEMICOLON()
        ))
        
        self.rule('annotation', Sequence(
            self.AT(),
            self.START()
        ))
        
        self.rule('branches', Sequence(
            self.branch('branch'),
            Many(Sequence(
                self.PIPE(),
                self.branch('branch')
            ))
        ))
        
        self.rule('branch', Sequence(
            OneOrMore(OneOf(
                self.TOKEN_ID('token_id'),
                self.RULE_ID('rule_id'),
                self.group('group')
            )),
            Optional(self.cardinality('card'))
        ))
        
        self.rule('group', Sequence(
            self.LPAR(),
            self.branches(),
            self.RPAR()
        ))
        
        self.rule('cardinality', OneOf(
            self.QUESTION_MARK(),
            self.PLUS(),
            self.ASTERISK()
        ))
        
        self._init_transforms()
        
    def _init_transforms(self):
        
        self.set_ast_transform('tokenrule', self._trans_tokenrule)
        self.set_ast_transform('commentdef', self._trans_commentdef)
        self.set_ast_transform('stringdef', self._trans_stringdef)
        self.set_ast_transform('tokendef', self._trans_tokendef)
        
        self.set_ast_transform('productionrule', self._trans_productionrule)
        
    def _trans_tokenrule(self, ast):
        return ast.get_children()[0]
    
    def _trans_commentdef(self, ast):
        ret = Ast('commentdef')
        start = ast.find_children_by_id('start')[0]
        end = ast.find_children_by_id('end')[0]
        ret.add_child(Ast('start', start.value))
        ret.add_child(Ast('end', end.value))
        return ret

    def _trans_stringdef(self, ast):
        ret = Ast('stringdef')
        start = ast.find_children_by_id('start')[0]
        end = ast.find_children_by_id('end')[0]
        escs = ast.find_children_by_id('escape')
        esc = escs and escs[0].value or None
        ids = ast.find_children_by_id('token_id')
        token_id = ids and ids[0].value or 'STRING'
        ret.add_child(Ast('id', token_id))
        ret.add_child(Ast('start', start.value))
        ret.add_child(Ast('end', end.value))
        if esc is not None:
            ret.add_child(Ast('escape', esc))
        return ret
    
    def _trans_tokendef(self, ast):
        ret = Ast('tokendef')
        token_id = ast.find_children_by_id('token_id')[0]
        regex = ast.find_children_by_id('regex')[0]
        ret.add_child(Ast('id', token_id.value))
        ret.add_child(Ast('regex', regex.value))
        return ret
    
    def _trans_productionrule(self, ast):
        ret = Ast('ruledef')
        annots = ast.find_children_by_id('annot')
        if annots:
            ret.set_attr('start', "true")
        id_ = ast.find_children_by_id('rule_id')[0]
        ret.add_child(Ast('id', id_.value))
        rhs = ast.find_children_by_id('rhs')[0]
        rhs.id = ""
        ret.add_child(rhs)
        return ret
    
    
if __name__ == "__main__":
    
    from komparse import StringStream, Scanner, Parser
    
    code = """
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
    expr -> prod  (PLUS prod)*;
    
    prod -> factor (MULT factor)*;
    
    factor -> INT | LPAR expr RPAR;
    
    """
    
    g = Grammar()
    scanner = Scanner(StringStream(code), g)
    
    while scanner.has_next():
        token = scanner.advance()
        print(token)
    
    parser = Parser(g)
    ast = parser.parse(code)
    
    if ast:
        print(ast.to_xml())
    else:
        print(parser.error())
    
        


"""
Grammar for parser generator
"""

from komparse import Grammar as BaseGrammar

class Grammar(BaseGrammar):
    
    def __init__(self):
        BaseGrammar.__init__(self)
        self._init_tokens()
        self._init_grammar()
        
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
        self.add_token('LSQB', "\[")
        self.add_token('RSQB', "\]")
        self.add_token('QUESTION_MARK', "\?")
        self.add_token('PLUS', "\+")
        self.add_token('ASTERISK', "\*")
        self.add_token('PIPE', "\|")
        self.add_token('SEMICOLON', ";")
        self.add_token('AT', "@")
        self.add_token('TOKEN_ID', "[A-Z][A-Z0-9_]*")
        self.add_token('RULE_ID', "[a-z][a-z0-9_]*")
    
    def _init_rules(self):
        pass
    
    
    
if __name__ == "__main__":
    
    from komparse import StringStream, Scanner
    
    
    code = """
    -- Test grammar
    
    string '#'' '#'' '\\' SINGLE_QUOTED;
    
    @start
    command -> (token_def | rule_def)+;
    """
    
    g = Grammar()
    scanner = Scanner(StringStream(code), g)
    
    while scanner.has_next():
        token = scanner.advance()
        print(token)
    
    
    
        


import ply.lex as lex

# =============================================================================
# LEXER
# =============================================================================

class ASPLexer:
    """Lexer for ASP-Core-2 language"""

    tokens = (
        'SYMBOLIC_CONSTANT', 'NUMBER', 'FLOAT_NUMBER', 'VARIABLE', 'STRING',
        'DIRECTIVE_NAME', 'DIRECTIVE_VALUE',
        'AGGR_COUNT', 'AGGR_MAX', 'AGGR_MIN', 'AGGR_SUM',

        'ANNOTATION_RULE_ORDERING', 'ANNOTATION_ORDERING_VALUE',
        'ANNOTATION_RULE_PROJECTION', 'ANNOTATION_RULE_LOOK_AHEAD',
        'ANNOTATION_RULE_ALIGN_SUBSTITUTIONS', 'ANNOTATION_RULE_REWRITING_ARITH',
        'ANNOTATION_RULE_ATOM_INDEXED', 'ANNOTATION_ATOM_INDEXED_ATOM',
        'ANNOTATION_ATOM_INDEXED_ARGUMENTS',
        'ANNOTATION_RULE_PARTIAL_ORDER', 'ANNOTATION_PARTIAL_ORDER_BEFORE',
        'ANNOTATION_PARTIAL_ORDER_AFTER',
        'ANNOTATION_GLOBAL_ORDERING', 'ANNOTATION_GLOBAL_ATOM_INDEXED',
        'ANNOTATION_GLOBAL_PARTIAL_ORDER', 'ANNOTATION_GLOBAL_EXTATOM_CONVERSION',
        'ANNOTATION_EXTATOM_PREDICATE', 'ANNOTATION_EXTATOM_TYPE',
        'ANNOTATION_EXTATOM_TYPE_QCONST', 'ANNOTATION_EXTATOM_TYPE_CONST',
        'ANNOTATION_EXTATOM_TYPE_U_INT', 'ANNOTATION_EXTATOM_TYPE_UT_INT',
        'ANNOTATION_EXTATOM_TYPE_UR_INT', 'ANNOTATION_EXTATOM_TYPE_T_INT',
        'ANNOTATION_EXTATOM_TYPE_R_INT',
        'ANNOTATION_RULE_TO_DECOMPOSE', 'ANNOTATION_RULE_TO_NOT_DECOMPOSE',

        'DOT', 'DDOT', 'COMMA', 'VEL', 'SEMICOLON', 'COLON', 'AT',
        'EXISTS', 'NAF', 'CONS', 'WCONS',
        'PLUS', 'DASH', 'TIMES', 'SLASH', 'BACK_SLASH',
        'PARAM_OPEN', 'PARAM_CLOSE',
        'SQUARE_OPEN', 'SQUARE_CLOSE',
        'CURLY_OPEN', 'CURLY_CLOSE',
        'QUERY_MARK', 'ANON_VAR',
        'EQUAL', 'UNEQUAL', 'LESS', 'GREATER', 'LESS_OR_EQ', 'GREATER_OR_EQ',
        'AMPERSAND',
    )

    t_DOT = r'\.'
    t_COMMA = r','
    t_VEL = r'\|'
    t_SEMICOLON = r';'
    t_COLON = r':'
    t_AT = r'@'
    t_PLUS = r'\+'
    t_DASH = r'-'
    t_TIMES = r'\*'
    t_SLASH = r'/'
    t_BACK_SLASH = r'\\'
    t_PARAM_OPEN = r'\('
    t_PARAM_CLOSE = r'\)'
    t_SQUARE_OPEN = r'\['
    t_SQUARE_CLOSE = r'\]'
    t_CURLY_OPEN = r'\{'
    t_CURLY_CLOSE = r'\}'
    t_QUERY_MARK = r'\?'
    t_ANON_VAR = r'_'
    t_AMPERSAND = r'&'

    t_ignore = ' \t'

    states = (
        ('directivevalue', 'exclusive'),
    )

    def __init__(self):
        self.lexer = None
        self.line_num = 1

    def t_NEWLINE(self, t):
        r'\r?\n'
        t.lexer.lineno += 1
        self.line_num += 1

    def t_COMMENT(self, t):
        r'%[^@\n].*'
        pass

    def t_COMMENT_EMPTY(self, t):
        r'%\n'
        t.lexer.lineno += 1
        self.line_num += 1

    def t_ANNOTATION_RULE_ALIGN_SUBSTITUTIONS(self, t):
        r'%@rule_align_substitutions'
        return t

    def t_ANNOTATION_RULE_LOOK_AHEAD(self, t):
        r'%@rule_look_ahead'
        return t

    def t_ANNOTATION_RULE_PROJECTION(self, t):
        r'%@rule_projection'
        return t

    def t_ANNOTATION_RULE_REWRITING_ARITH(self, t):
        r'%@rule_rewriting_arith'
        return t

    def t_ANNOTATION_RULE_ORDERING(self, t):
        r'%@rule_ordering'
        return t

    def t_ANNOTATION_ORDERING_VALUE(self, t):
        r'@value'
        return t

    def t_ANNOTATION_RULE_ATOM_INDEXED(self, t):
        r'%@rule_atom_indexed'
        return t

    def t_ANNOTATION_ATOM_INDEXED_ATOM(self, t):
        r'@atom'
        return t

    def t_ANNOTATION_ATOM_INDEXED_ARGUMENTS(self, t):
        r'@arguments'
        return t

    def t_ANNOTATION_RULE_PARTIAL_ORDER(self, t):
        r'%@rule_partial_order'
        return t

    def t_ANNOTATION_PARTIAL_ORDER_BEFORE(self, t):
        r'@before'
        return t

    def t_ANNOTATION_PARTIAL_ORDER_AFTER(self, t):
        r'@after'
        return t

    def t_ANNOTATION_EXTATOM_PREDICATE(self, t):
        r'@predicate'
        return t

    def t_ANNOTATION_EXTATOM_TYPE(self, t):
        r'@type'
        return t

    def t_ANNOTATION_EXTATOM_TYPE_QCONST(self, t):
        r'@Q_CONST'
        return t

    def t_ANNOTATION_EXTATOM_TYPE_CONST(self, t):
        r'@CONST'
        return t

    def t_ANNOTATION_EXTATOM_TYPE_U_INT(self, t):
        r'@U_INT'
        return t

    def t_ANNOTATION_EXTATOM_TYPE_UR_INT(self, t):
        r'@UR_INT'
        return t

    def t_ANNOTATION_EXTATOM_TYPE_UT_INT(self, t):
        r'@UT_INT'
        return t

    def t_ANNOTATION_EXTATOM_TYPE_R_INT(self, t):
        r'@R_INT'
        return t

    def t_ANNOTATION_EXTATOM_TYPE_T_INT(self, t):
        r'@T_INT'
        return t

    def t_ANNOTATION_GLOBAL_ORDERING(self, t):
        r'%@global_ordering'
        return t

    def t_ANNOTATION_GLOBAL_ATOM_INDEXED(self, t):
        r'%@global_atom_indexed'
        return t

    def t_ANNOTATION_GLOBAL_PARTIAL_ORDER(self, t):
        r'%@global_partial_order'
        return t

    def t_ANNOTATION_GLOBAL_EXTATOM_CONVERSION(self, t):
        r'%@global_external_predicate_conversion'
        return t

    def t_ANNOTATION_RULE_TO_DECOMPOSE(self, t):
        r'%@rule_to_decompose'
        return t

    def t_ANNOTATION_RULE_TO_NOT_DECOMPOSE(self, t):
        r'%@rule_to_not_decompose'
        return t

    def t_AGGR_COUNT(self, t):
        r'\#count'
        return t

    def t_AGGR_MAX(self, t):
        r'\#max'
        return t

    def t_AGGR_MIN(self, t):
        r'\#min'
        return t

    def t_AGGR_SUM(self, t):
        r'\#sum'
        return t

    def t_EXISTS(self, t):
        r'\\E'
        return t

    def t_NAF(self, t):
        r'not'
        return t

    def t_CONS(self, t):
        r':-'
        return t

    def t_WCONS(self, t):
        r':~'
        return t

    def t_DDOT(self, t):
        r'\.\.'
        return t

    def t_EQUAL(self, t):
        r'(==|=)'
        return t

    def t_UNEQUAL(self, t):
        r'(<>|!=)'
        return t

    def t_LESS_OR_EQ(self, t):
        r'<='
        return t

    def t_GREATER_OR_EQ(self, t):
        r'>='
        return t

    def t_LESS(self, t):
        r'<'
        return t

    def t_GREATER(self, t):
        r'>'
        return t

    def t_DIRECTIVE_NAME(self, t):
        r'\#[A-Za-z_]*'
        t.lexer.begin('directivevalue')
        return t

    def t_directivevalue_DIRECTIVE_VALUE(self, t):
        r'[^\n]+'
        t.lexer.begin('INITIAL')
        return t

    t_directivevalue_ignore = ''
    def t_directivevalue_error(self, t):
        """Error handling for directivevalue state"""
        print(f"Illegal character '{t.value[0]}' in directive value at line {t.lexer.lineno}")
        t.lexer.skip(1)

    def t_directivevalue_NEWLINE(self, t):
        r'\n'
        t.lexer.lineno += 1
        t.lexer.begin('INITIAL')

    def t_FLOAT_NUMBER(self, t):
        r'[0-9]+\.[0-9]+'
        t.value = float(t.value)
        return t

    def t_NUMBER(self, t):
        r'[0-9]+'
        t.value = int(t.value)
        return t

    def t_STRING(self, t):
        r'"[^"]*"'
        return t

    def t_VARIABLE(self, t):
        r'[A-Z][A-Za-z_0-9]*'
        return t

    def t_SYMBOLIC_CONSTANT(self, t):
        r'[a-z][A-Za-z_0-9]*'
        return t

    def t_error(self, t):
        print(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
        t.lexer.skip(1)

    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)
        return self.lexer

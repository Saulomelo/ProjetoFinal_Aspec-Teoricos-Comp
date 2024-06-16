import re

class Token:
    def __init__(self, type_, value, line):
        self.type = type_
        self.value = value
        self.line = line

    def __repr__(self):
        return f'Token({self.type}, {repr(self.value)}, Line {self.line})'

class Lexer:
    def __init__(self, code):
        self.code = code
        self.tokens = []
        self.current_position = 0
        self.line = 1

    def tokenize(self):
        token_specification = [
            ("AND", r'&&'),
            ("OR", r'\|\|'),
            ("TRUE", r'true'),
            ("FALSE", r'false'),
            ("EQ", r'=='),
            ("ASSIGN", r'='),
            ("NEQ", r'!='),
            ("LE", r'<='),
            ("GE", r'>='),
            ("LT", r'<'),
            ("GT", r'>'),
            ("NUMBER", r'\d+'),
            ("IF", r'\bif\b'),
            ("ELSE", r'\belse\b'),
            ("FOR", r'\bfor\b'),
            ("WHILE", r'\bwhile\b'),
            ("RETURN", r'\breturn\b'),
            ("OP", r'[+\-*/]'),
            ("ID", r'[A-Za-z_][A-Za-z0-9_]*'),
            ("SEMI", r';'),
            ("LPAREN", r'\('),
            ("RPAREN", r'\)'),
            ("LCURLY", r'\{'),
            ("RCURLY", r'\}'),
            ("COMMA", r','),
            ("SKIP", r'[ \t\n]+'),
            ("MISMATCH", r'.'),
        ]
        
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
        for mo in re.finditer(tok_regex, self.code):
            kind = mo.lastgroup
            value = mo.group()
            if kind == 'SKIP':
                continue
            elif kind == 'MISMATCH':
                raise RuntimeError(f'Unexpected character {value!r}')
            else:
                self.tokens.append(Token(kind, value, mo.start()))
        
        print("Tokens Gerados:", self.tokens)  # Depuração para verificar os tokens gerados
        return self.tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0
        self.current_token = None
        self.indent_level = 0
        self.advance()

    def advance(self):
        if self.index < len(self.tokens):
            self.current_token = self.tokens[self.index]
            self.index += 1
        else:
            self.current_token = None

    def indent(self):
        return '    ' * self.indent_level

    def parse_expression(self):
        expr = []
        while self.current_token and self.current_token.type not in ["SEMI", "RPAREN", "COMMA", "LCURLY", "RCURLY"]:
            if self.current_token.type == "TRUE":
                expr.append("True")
            elif self.current_token.type == "FALSE":
                expr.append("False")
            elif self.current_token.type == "AND":
                expr.append("and")
            elif self.current_token.type == "OR":
                expr.append("or")
            else:    
                expr.append(str(self.current_token.value))
            self.advance()
        print("Parsed expression:", expr)  # Depuração para ver a expressão
        return " ".join(expr)

    def parse_statement(self):
        statement = ""
        if self.current_token.type == "ID" and self.tokens[self.index].type == "ASSIGN":
            var_name = self.current_token.value
            self.advance()  # Move para '='
            self.advance()  # Move após '='
            expr = self.parse_expression()
            statement = f"{self.indent()}{var_name} = {expr}"
        elif self.current_token.type == "IF":
            statement = self.parse_if_statement()
        elif self.current_token.type == "FOR":
            statement = self.parse_for_statement()
        elif self.current_token.type == "WHILE":
            statement = self.parse_while_statement()
        elif self.current_token.type == "RETURN":
            self.advance()  # Move para a expressão após 'return'
            expr = self.parse_expression()
            statement = f"{self.indent()}return {expr}"
        else:
            self.advance()
        return statement

    def parse_if_statement(self):
        if_conditions = []
        if_bodies = []
        
        self.advance()  # Move após 'if'
        self.advance()  # Move após '('
        condition = self.parse_expression()
        self.advance()  # Move após ')'
        self.advance()  # Move para '{'
        
        body = []
        self.indent_level += 1
        while self.current_token and self.current_token.type != "RCURLY":
            statement = self.parse_statement()
            if statement:
                body.append(statement)
            if self.current_token and self.current_token.type == "SEMI":
                self.advance()  # Move após ';'
        self.indent_level -= 1
        self.advance()  # Move após '}'
        
        if_conditions.append(condition)
        if_bodies.append(body)
        
        while self.current_token and self.current_token.type == "ELSE":
            self.advance()  # Move após 'else'
            if self.current_token and self.current_token.type == "IF":
                self.advance()  # Move após 'if'
                self.advance()  # Move após '('
                condition = self.parse_expression()
                self.advance()  # Move após ')'
                self.advance()  # Move para '{'
                
                body = []
                self.indent_level += 1
                while self.current_token and self.current_token.type != "RCURLY":
                    statement = self.parse_statement()
                    if statement:
                        body.append(statement)
                    if self.current_token and self.current_token.type == "SEMI":
                        self.advance()  # Move após ';'
                self.indent_level -= 1
                self.advance()  # Move após '}'
                
                if_conditions.append(condition)
                if_bodies.append(body)
            else:
                self.advance()  # Move para '{'
                else_body = []
                self.indent_level += 1
                while self.current_token and self.current_token.type != "RCURLY":
                    statement = self.parse_statement()
                    if statement:
                        else_body.append(statement)
                    if self.current_token and self.current_token.type == "SEMI":
                        self.advance()  # Move após ';'
                self.indent_level -= 1
                self.advance()  # Move após '}'
                if_conditions.append(None)
                if_bodies.append(else_body)
                break
        
        # Construir o código Python para if-elif-else
        if_code = []
        for idx, cond in enumerate(if_conditions):
            if idx == 0:
                if_code.append(f"{self.indent()}if {cond}:")
            elif cond is not None:
                if_code.append(f"{self.indent()}elif {cond}:")
            else:
                if_code.append(f"{self.indent()}else:")
            if_code.extend([line for line in if_bodies[idx]])
        
        return "\n".join(if_code)

    def parse_for_statement(self):
        self.advance()  # Move após 'for'
        self.advance()  # Move após '('
        initialization = self.parse_expression()  # Inicialização
        self.advance()  # Move após ';'
        condition = self.parse_expression()  # Condição
        self.advance()  # Move após ';'
        increment = self.parse_expression()  # Incremento
        self.advance()  # Move após ')'
        self.advance()  # Move para '{'
        body = []
        self.indent_level += 1
        while self.current_token and self.current_token.type != "RCURLY":
            statement = self.parse_statement()
            if statement:
                body.append(statement)
            if self.current_token and self.current_token.type == "SEMI":
                self.advance()  # Move após ';'
        self.indent_level -= 1
        self.advance()  # Move após '}'
        
        # Pega a variavel do primerio argumento do for e seu valor
        init_parts = initialization.split('=')
        loop_var = init_parts[0].strip().split()[-1]  # Remove a tipagem e mantenha apenas o nome da variável
        start_value = init_parts[1].strip()
        
        # Pegar o valor a ser percorrido no FOR 
        cond_parts = condition.split('<')
        if len(cond_parts) < 2:
            cond_parts = condition.split('>')
        
        end_value = cond_parts[1].strip()
        
        # Pega o valor do incremento
        increment_parts = increment.split('=')
        
        if (len(increment_parts[0].strip().split()) > 1):
            if (increment_parts[0].strip().split()[1] == "+"
                or increment_parts[0].strip().split()[1] == "-"
                or increment_parts[0].strip().split()[1] == "/"
                or increment_parts[0].strip().split()[1] == "*"):
                increment_value = increment_parts[0].strip().split()[1] + increment_parts[1].strip().split()[-1]
        else:
            increment_value = increment_parts[1].strip().split()[1] + increment_parts[1].strip().split()[-1]
        
        return (f"{self.indent()}for {loop_var} in range({start_value}, {end_value}, {increment_value}):\n" +
                "\n".join(body))

    def parse_while_statement(self):
        self.advance()  # Move após 'while'
        self.advance()  # Move após '('
        condition = self.parse_expression()
        self.advance()  # Move após ')'
        self.advance()  # Move para '{'
        body = []
        self.indent_level += 1
        while self.current_token and self.current_token.type != "RCURLY":
            statement = self.parse_statement()
            if statement:
                body.append(statement)
            if self.current_token and self.current_token.type == "SEMI":
                self.advance()  # Move após ';'
        self.indent_level -= 1
        self.advance()  # Move após '}'
        return f"{self.indent()}while {condition}:\n" + "\n".join(body)

    def parse_function(self):
        ret_type = self.current_token.value
        self.advance()  # Move para o nome da função
        func_name = self.current_token.value
        self.advance()  # Move para '('
        self.advance()  # Move após '('
        params = []
        while self.current_token.type != "RPAREN":
            self.advance()  # Ignorar o tipo do parâmetro
            param_name = self.current_token.value
            self.advance()
            if self.current_token.type == "ASSIGN":
                self.advance()  # Move após '='
                default_value = self.parse_expression()
                params.append(f"{param_name}={default_value}")
            else:
                params.append(param_name)
            if self.current_token.type == "COMMA":
                self.advance()  # Move após a vírgula
        self.advance()  # Move após ')'
        self.advance()  # Move para '{'
        body = []
        self.indent_level += 1
        while self.current_token and self.current_token.type != "RCURLY":
            statement = self.parse_statement()
            if statement:
                body.append(statement)
            if self.current_token and self.current_token.type == "SEMI":
                self.advance()  # Move após ';'
        self.indent_level -= 1
        self.advance()  # Move após '}'
        function_code = f"def {func_name}({', '.join(params)}):\n" + "\n".join(body)
        return function_code

    def parse(self):
        results = []
        while self.current_token:
            if self.current_token.type == "ID" and self.current_token.value in ["int", "void", "boolean"]:
                results.append(self.parse_function())
            else:
                self.advance()
        return results

def generate_python_code(c_code):
    lexer = Lexer(c_code)
    tokens = lexer.tokenize()
    print("Tokens:", tokens)  # Depuração para verificar os tokens
    parser = Parser(tokens)
    python_code = parser.parse()
    return '\n'.join(python_code)

# Código de teste
c_code = """
int main() {
    int a = 5;
    int b = 0;
    for (int i = 20; i > 10; i = i - 1) {
        a = a + i;
    }
    while (a > 0) {
        a = a - 1;
    }
    if (a < 2) {
        a = 200;
    } else if (a <= 50) {
        a = 45000;
    } else if (a != b) {
        a = -1;
    } else {
        a = 96;
    }
    return a;
}

boolean main2() {
    bool c = true;
    bool d = true;
    if (c == true && d == false) {
        return true;
    } else {
        return false;
    }
}

void main3(int a = 1, int b = 2) {
    return a + b;
}
"""

python_code = generate_python_code(c_code)
filename = 'codigoGerado.py'

with open(filename, 'w') as file:
    file.write(python_code)

print(f"Generated Python code has been saved to {filename}")

from dataclasses import dataclass


@dataclass
class Identifier:
    name: str

@dataclass
class SpecialChar:
    char: str

@dataclass
class Keyword:
    word: str

@dataclass
class Integer:
    n: int

type Token = Identifier | Keyword | SpecialChar | Integer

separator_chars = ["(", ")", "{", "}", ";"]
special_chars = ["(", ")", ";", "{", "}", "=", "+", "-", "*", "/"]
keywords = ["AND", "OR", "NOT", "let", "set", "if", "else", "output", "input", "while"]

def tokenise(text: str) -> list[Token]:
    tokens = []
    i = -1
    while i + 1 < len(text):
        i += 1
        char = text[i]

        # Skip spaces
        if char in [" ", "\n"]:
            pass
        # Alphabetic string. Could be a keyword or identifier
        elif char.isalpha():
            string_token = char
            while i + 1 < len(text):
                i += 1
                char = text[i]
                if char.isalpha():
                    string_token += char
                else:
                    i -= 1
                    break
            if string_token in keywords:
                t = Keyword(string_token)
            else:
                t = Identifier(string_token)
            tokens.append(t)
            continue
        elif char.isdigit():
            integer_token = char
            while i + 1 < len(text):
                i += 1
                char = text[i]
                if char.isdigit():
                    integer_token += char
                else:
                    i -= 1
                    break
            tokens.append(Integer(int(integer_token)))
        elif char in special_chars:
            special_char_token = char
            while i + 1 < len(text):
                i += 1
                char = text[i]
                if char in special_chars and char not in separator_chars:
                    special_char_token += char
                else:
                    i -= 1
                    break
            tokens.append(SpecialChar(special_char_token))
        else:
            raise Exception(":(")
    return tokens

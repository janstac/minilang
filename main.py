import parser
import interpreter
import sys

def main():
    # text = ""
    # while True:
    #     try:
    #         line_input = input()
    #     except EOFError:
    #         break
    #     text += line_input + "\n"

    file = open(sys.argv[1])
    text = file.read()
    file.close()
        
    tokens = parser.lexer.tokenise(text)
    print(tokens)
    p = parser.Parser(tokens)
    tree = p.parse_program()
    print(tree)
    print(parser.syntax_string(tree))

    print("Program start\n---")
    i = interpreter.Interpreter(tree)
    i.run()
    print("---\nDone")

    pass



if __name__ == "__main__":
    main()


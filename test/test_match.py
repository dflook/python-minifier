import ast
import sys
import pytest
from python_minifier import unparse
from python_minifier.ast_compare import compare_ast

def test_pep635_unparse():
    if sys.version_info < (3, 10):
        pytest.skip('Match statement not in python < 3.10')

    source = '''
match x:
    case host, port:
        mode = "http"
    case host, port, mode:
        pass
        
match node:
    case BinOp("+", a, BinOp("*", b, c)):
        pass   
        
match json_pet:
    case {"type": "cat", "name": name, "pattern": pattern}:
        return Cat(name, pattern)
    case {"type": "dog", "name": name, "breed": breed}:
        return Dog(name, breed)
    case _:
        raise ValueError("Not a suitable pet")
        
def sort(seq):
    match seq:
        case [] | [_]:
            return seq
        case [x, y] if x <= y:
            return seq
        case [x, y]:
            return [y, x]
        case [x, y, z] if x <= y <= z:
            return seq
        case [x, y, z] if x >= y >= z:
            return [z, y, x]
        case [p, *rest]:
            a = sort([x for x in rest if x <= p])
            b = sort([x for x in rest if p < x])
            return a + [p] + b

def simplify_expr(tokens):
    match tokens:
        case [('('|'[') as l, *expr, (')'|']') as r] if (l+r) in ('()', '[]'):
            return simplify_expr(expr)
        case [0, ('+'|'-') as op, right]:
            return UnaryOp(op, right)
        case [(int() | float() as left) | Num(left), '+', (int() | float() as right) | Num(right)]:
            return Num(left + right)
        case [(int() | float()) as value]:
            return Num(value)
   
def simplify(expr):
    match expr:
        case ('/', 0, 0):
            return expr
        case ('*'|'/', 0, _):
            return 0
        case ('+'|'-', x, 0) | ('+', 0, x) | ('*', 1, x) | ('*'|'/', x, 1):
            return x
    return expr

def simplify(expr):
    match expr:
        case ('+', 0, x):
            return x
        case ('+' | '-', x, 0):
            return x
        case ('and', True, x):
            return x
        case ('and', False, x):
            return False
        case ('or', False, x):
            return x
        case ('or', True, x):
            return True
        case ('not', ('not', x)):
            return x
    return expr

def average(*args):
    match args:
        case [x, y]:           # captures the two elements of a sequence
            return (x + y) / 2
        case [x]:              # captures the only element of a sequence
            return x
        case []:
            return 0
        case a:                # captures the entire sequence
            return sum(a) / len(a)
 
def is_closed(sequence):
   match sequence:
       case [_]:               # any sequence with a single element
           return True
       case [start, *_, end]:  # a sequence with at least two elements
           return start == end
       case _:                 # anything
           return False
 
def handle_reply(reply):
   match reply:
       case (HttpStatus.OK, MimeType.TEXT, body):
           process_text(body)
       case (HttpStatus.OK, MimeType.APPL_ZIP, body):
           text = deflate(body)
           process_text(text)
       case (HttpStatus.MOVED_PERMANENTLY, new_URI):
           resend_request(new_URI)
       case (HttpStatus.NOT_FOUND):
           raise ResourceNotFound()

def change_red_to_blue(json_obj):
    match json_obj:
        case { 'color': ('red' | '#FF0000') }:
            json_obj['color'] = 'blue'
        case { 'children': children }:
            for child in children:
                change_red_to_blue(child)

'''

    expected_ast = ast.parse(source)
    actual_ast = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(actual_ast))

def test_pep646_unparse():
    if sys.version_info < (3, 10):
        pytest.skip('Match statement not in python < 3.10')

    source = '''
match command.split():
    case [action]:
        pass
    case [action, obj]:
        pass

match command.split():
    case ["quit"]:
        print("Goodbye!")
        quit_game()
    case ["look"]:
        current_room.describe()
    case ["get", obj]:
        character.get(obj, current_room)
    case ["go", direction]:
        current_room = current_room.neighbor(direction)

match command.split():
    case ["drop", *objects]:
        for obj in objects:
            character.drop(obj, current_room)

match command.split():
    case ["quit"]: pass
    case ["go", direction]: pass
    case ["drop", *objects]: pass
    case _:
        print(f"Sorry, I couldn't understand {command!r}")

match command.split():

    case ["north"] | ["go", "north"]:
        current_room = current_room.neighbor("north")
    case ["get", obj] | ["pick", "up", obj] | ["pick", obj, "up"]:
        pass

match command.split():
    case ["go", ("north" | "south" | "east" | "west")]:
        current_room = current_room.neighbor(...)

match command.split():
    case ["go", ("north" | "south" | "east" | "west") as direction]:
        current_room = current_room.neighbor(direction)

match command.split():
    case ["go", direction] if direction in current_room.exits:
        current_room = current_room.neighbor(direction)
    case ["go", _]:
        print("Sorry, you can't go that way")

match event.get():
    case Click(position=(x, y)):
        handle_click_at(x, y)
    case KeyPress(key_name="Q") | Quit():
        game.quit()
    case KeyPress(key_name="up arrow"):
        game.go_north()
    case KeyPress():
        pass # Ignore other keystrokes
    case other_event:
        raise ValueError(f"Unrecognized event: {other_event}")

match event.get():
    case Click((x, y)):
        handle_click_at(x, y)

match event.get():
    case Click((x, y), button=Button.LEFT):  # This is a left click
        handle_click_at(x, y)
    case Click():
        pass  # ignore other clicks

match action:
    case {"text": message, "color": c}:
        ui.set_text_color(c)
        ui.display(message)
    case {"sleep": duration}:
        ui.wait(duration)
    case {"sound": url, "format": "ogg"}:
        ui.play(url)
    case {"sound": _, "format": _}:
        warning("Unsupported audio format")

match action:
    case {"text": str(message), "color": str(c)}:
        ui.set_text_color(c)
        ui.display(message)
    case {"sleep": float(duration)}:
        ui.wait(duration)
    case {"sound": str(url), "format": "ogg"}:
        ui.play(url)
    case {"sound": _, "format": _}:
        warning("Unsupported audio format")

match status:
    case 400:
        return "Bad request"
    case 404:
        return "Not found"
    case 418:
        return "I'm a teapot"
    case 401 | 403 | 404:
        return "Not allowed"
    case _:
        return "Something's wrong with the Internet"

match point:
    case (0, 0):
        print("Origin")
    case (0, y):
        print(f"Y={y}")
    case (x, 0):
        print(f"X={x}")
    case (x, y):
        print(f"X={x}, Y={y}")
    case _:
        raise ValueError("Not a point")

match point:
    case Point(x=0, y=0):
        print("Origin")
    case Point(x=0, y=y):
        print(f"Y={y}")
    case Point(x=x, y=0):
        print(f"X={x}")
    case Point():
        print("Somewhere else")
    case _:
        print("Not a point")

match points:
    case []:
        print("No points")
    case [Point(0, 0)]:
        print("The origin")
    case [Point(x, y)]:
        print(f"Single point {x}, {y}")
    case [Point(0, y1), Point(0, y2)]:
        print(f"Two on the Y axis at {y1}, {y2}")
    case _:
        print("Something else")

match point:
    case Point(x, y) if x == y:
        print(f"Y=X at {x}")
    case Point(x, y):
        print(f"Not on the diagonal")

match color:
    case Color.RED:
        print("I see red!")
    case Color.GREEN:
        print("Grass is green")
    case Color.BLUE:
        print("I'm feeling the blues :(")

    '''

    expected_ast = ast.parse(source)
    actual_ast = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(actual_ast))

def test_match_unparse():
    if sys.version_info < (3, 10):
        pytest.skip('Match statement not in python < 3.10')

    source = '''
match a:
    case (0 as a) as b: pass

match a:
    case _:pass
    
match a:
    case 0|(0|0): pass
    case (0|0)|0: pass    
    case 0|0|0: pass

match (lambda: a)():
    case [action, obj]:pass

match a:= h:
    case [action, obj]:pass
    case {**rest}: pass   
    '''

    expected_ast = ast.parse(source)
    actual_ast = unparse(expected_ast)
    compare_ast(expected_ast, ast.parse(actual_ast))

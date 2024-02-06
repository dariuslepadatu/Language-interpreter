from .NFA import NFA


class Regex:
    nr_of_states = 0

    def get_state() -> int:
        state = Regex.nr_of_states
        Regex.nr_of_states += 1
        return state
    
    def thompson(self) -> NFA[int]:
        return self.thompson()


class Character(Regex):
    char: str

    def __init__(self, char: str):
        self.char = char

    def thompson(self) -> NFA[int]:
            start_state = Regex.get_state()
            accept_state = Regex.get_state()

            # Initialize NFA parameters
            nfa_S = {self.char}
            nfa_K = {start_state, accept_state}
            nfa_q0 = start_state
            nfa_d = {(start_state, self.char): {accept_state}}  # Transition on the character
            nfa_F = {accept_state}
            
            # Create a simple NFA for a single character
            return NFA(S=nfa_S, K=nfa_K, q0=nfa_q0, d=nfa_d, F=nfa_F)


class Concat(Regex):
    left: Regex
    right: Regex

    def __init__(self, left: Regex, right: Regex):
        self.left = left
        self.right = right

    def thompson(self) -> NFA[int]:
        # Will combine two NFAs for concatenation
        left_nfa = self.left.thompson()
        right_nfa = self.right.thompson()

        nfa_S = left_nfa.S | right_nfa.S
        nfa_K = left_nfa.K | right_nfa.K
        nfa_q0 = left_nfa.q0
        nfa_F = right_nfa.F

        # Combine the transitions
        nfa_d = left_nfa.d.copy()
        nfa_d.update(right_nfa.d)

        # Connect left NFA's accept states to right NFA's start state with epsilon transitions
        for left_accept in left_nfa.F:
            nfa_d[(left_accept, '')] = {right_nfa.q0}

        return NFA(S=nfa_S, K=nfa_K, q0=nfa_q0, d=nfa_d, F=nfa_F)
    
class Union(Regex):
    left: Regex
    right: Regex

    def __init__(self, left: Regex, right: Regex):
        self.left = left
        self.right = right

    def thompson(self) -> NFA[int]:
        # Combine two NFAs for union
        left_nfa = self.left.thompson()
        right_nfa = self.right.thompson()

        start_state = Regex.get_state()
        accept_state = Regex.get_state()

        nfa_S = left_nfa.S | right_nfa.S
        nfa_q0 = start_state
        nfa_K = left_nfa.K | right_nfa.K | {start_state, accept_state}
        nfa_F = {accept_state}

        # Combine the transitions 
        nfa_d = left_nfa.d.copy()
        nfa_d.update(right_nfa.d)

        # New epsilon transition from the start state to each NFA's start state
        nfa_d[(nfa_q0, '')] = {left_nfa.q0, right_nfa.q0}
  
        # New epsilon transitions from each NFA's accept states to the new accept state
        for left_accept in left_nfa.F:
            nfa_d[(left_accept, '')] = {accept_state}

        for right_accept in right_nfa.F:
            nfa_d[(right_accept, '')] = {accept_state}

        return NFA(S=nfa_S, K=nfa_K, q0=nfa_q0, d=nfa_d, F=nfa_F)
    

class Star(Regex):
    regex: Regex

    def __init__(self, regex: Regex):
        self.regex = regex

    def thompson(self) -> NFA[int]:
        old_nfa = self.regex.thompson()

        start_state = Regex.get_state()
        accept_state = Regex.get_state()

        nfa_S = old_nfa.S
        nfa_q0 = start_state
        nfa_K = old_nfa.K | {start_state, accept_state}
        nfa_F = {accept_state}
        nfa_d = old_nfa.d.copy()

        # Eps transition from the new start state to the old start state and new accept state
        nfa_d[(nfa_q0, '')] = {old_nfa.q0, accept_state}

        # Eps transitions from old accept states to the old start state and new accept state
        for old_accept in old_nfa.F:
            nfa_d[(old_accept, '')] = {old_nfa.q0, accept_state} 

        return NFA(S=nfa_S, K=nfa_K, q0=nfa_q0, d=nfa_d, F=nfa_F)


class Plus:
    def __init__(self, regex):
        self.regex = regex

    def thompson(self) -> NFA[int]:
        old_nfa = self.regex.thompson()
        start_state = Regex.get_state()
        accept_state = Regex.get_state()

        nfa_S = old_nfa.S
        nfa_q0 = start_state
        nfa_K = old_nfa.K | {start_state, accept_state}
        nfa_F = {accept_state}

        nfa_d = old_nfa.d.copy()

        # Eps transition from the new start state to the old start state
        nfa_d[(nfa_q0, '')] = {old_nfa.q0}

        # Eps transitions from old accept states to the old start state and new accept state
        for old_accept in old_nfa.F:
            nfa_d[(old_accept, '')] =  {old_nfa.q0, accept_state} 


        return NFA(S=nfa_S, K=nfa_K, q0=nfa_q0, d=nfa_d, F=nfa_F)
    

class Optional:
    def __init__(self, regex):
        self.regex = regex

    def thompson(self) -> NFA[int]:
        old_nfa = self.regex.thompson()
        start_state = Regex.get_state()
        accept_state = Regex.get_state()

        nfa_S = old_nfa.S
        nfa_q0 = start_state
        nfa_K = old_nfa.K | {start_state, accept_state}
        nfa_F = {accept_state}

        nfa_d = old_nfa.d.copy()

        # Eps transition from the new start state to the old start state and new accept state
        nfa_d[(nfa_q0, '')] = {old_nfa.q0, accept_state}

        # Eps transitions from old accept states to the new accept state
        for old_accept in old_nfa.F:
            nfa_d[(old_accept, '')] =  {accept_state} 


        return NFA(S=nfa_S, K=nfa_K, q0=nfa_q0, d=nfa_d, F=nfa_F)


class Range(Regex):
    start: str
    end: str

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def thompson(self) -> NFA[int]:

        start_state = Regex.get_state()
        accept_state = Regex.get_state()

        nfa_S = set()
        nfa_K = {start_state, accept_state}
        nfa_q0 = start_state
        nfa_d = {}
        nfa_F = {accept_state}
        # Create transitions for each character in the range

        first_int_code = ord(self.start)
        end_int_code = ord(self.end) + 1
        for char_code in range(first_int_code, end_int_code):
            char = chr(char_code)
            nfa_S |= {char}
            # Create a transition for the current character
            if (start_state, char) not in nfa_d:
                nfa_d[(start_state, char)] = set()

            nfa_d[(start_state, char)].add(accept_state)
        return NFA(S=nfa_S, K=nfa_K, q0=nfa_q0, d=nfa_d, F=nfa_F)

        
def parse_range(regex: str) -> tuple[Regex, str]:
    if not regex or regex[0] != '[':
        return None, regex
    
    # Create a Range object; a range looks like [A-Z]
    new_regex = Range(regex[1], regex[3])
    return new_regex, regex[5:]

def parse_concat(regex: str) -> tuple[Regex, str]:
    # Return None if the regex is empty
    if not regex:
        return None, regex

    new_regex = None        
    while regex:
        # Check for regular characters or special characters and create a Character object
        if regex[0].isalnum() or regex[0] in '-._:@\n':
            next_regex = Character(regex[0])
            regex = regex[1:]
        elif regex[0] == '(':
            next_regex, regex = parse_brackets(regex)
        elif regex[0] == '[':
            next_regex, regex = parse_range(regex)
        # If a '\' is encountered, treat the next character as a regular character
        elif regex[0] == '\\':
            next_regex = Character(regex[1])
            regex = regex[2:]
        else:
            break

        # Apply operators '*', '+', '?' if present
        if regex and regex[0] == '*':
            next_regex = Star(next_regex)
            regex = regex[1:]

        if regex and regex[0] == '+':
            next_regex = Plus(next_regex)
            regex = regex[1:]
        
        if regex and regex[0] == '?':
            next_regex = Optional(next_regex)
            regex = regex[1:]

        # Combine the new regex part with the existing one
        if  new_regex is not None:
            new_regex = Concat(new_regex, next_regex)
        else:
            new_regex = next_regex

    return new_regex, regex

def parse_union(regex: str) -> tuple[Regex, str]:

    left, regex = parse_concat(regex)
    # If there's no union operator, return the parsed left part
    if not regex or regex[0] != '|':
        return left, regex

    while regex and regex[0] == '|':
        regex = regex[1:]
        right, regex = parse_concat(regex)
        # Combine left and right parts of the union
        left = Union(left, right)

    return left, regex

def parse_brackets(regex: str) -> tuple[Regex, str]:
    if not regex or regex[0] != '(':
        return None, regex

    # Parse the content inside the brackets
    out1, regex = parse_union(regex[1:])
    # Skip the closing bracket
    regex = regex[1:]  

    return out1, regex


def parse_regex(regex: str) -> Regex:
    # create a Regex object by parsing the string
    # the checker will call this function, then the thompson method of the generated object.
    # the resulting NFA's behaviour will be checked using your implementation form stage 1

    if regex in ['(', ')', '++', 'lambda', ':', "+"]:
        return Character(regex)
    # Get rid of spaces but keep the escaped ones
    regex = regex.replace("\\ ", "\\space")
    regex = regex.replace(" ", "")
    regex = regex.replace("\\space", "\\ ")
    out_regex = parse_union(regex)[0]

    return out_regex
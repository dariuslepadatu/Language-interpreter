from .Regex import Regex, parse_regex
from .DFA import DFA
from .NFA import NFA

class Lexer:
    dfa: DFA
    tokens: [(str, set)]

    def __init__(self, spec: list[tuple[str, str]]) -> None:
        nfa_q0 = Regex.get_state()
        nfa_S = set()
        nfa_K = {nfa_q0}
        nfa_d = {}
        nfa_d[(nfa_q0, '')] = set()
        nfa_F = set()
        # tokens is a list of pairs (TOKEN_NAME:FINAL_STATES), where the final states
        # are those from the NFA represented by token's regex
        self.tokens = []
        # connects all nfas to the same initial state
        for token, regex in spec:
            new_nfa = parse_regex(regex).thompson()
            # add token and nfa final state in tokens list
            self.tokens.append((token, new_nfa.F))
            nfa_d = nfa_d.copy()
            nfa_d.update(new_nfa.d)
            nfa_d[(nfa_q0, '')] |= {new_nfa.q0}
            nfa_S |= new_nfa.S
            nfa_K |= new_nfa.K
            nfa_F |= new_nfa.F

        nfa = NFA(nfa_S, nfa_K, nfa_q0, nfa_d, nfa_F)
        self.dfa = nfa.subset_construction()


    # returns the final state if the dfa accepts the word, otherwise -1
    def finalState(self, word: str) -> int:
        state = self.dfa.q0
        if word == '++' or word == 'lambda':
            next_state = self.dfa.d.get((state, word))
            if next_state is None or next_state not in self.dfa.F:
                return -1
            return next_state

        while word:
            next_state = self.dfa.d.get((state, word[0]))
            if next_state is None:
                return -1
            state = next_state
            word = word[1:]
      
        if state not in self.dfa.F:
            return -1
        return state

    def lex(self, word: str) -> list[tuple[str, str]] | None:
        
        cont_newline = 0
        last_newline = 0
        # checks if all characters in the word are in dfa's alphabet 
        # if a character is not recognized by the lexer stops parsing the word
        i = 0
        while i < len(word):
            char = word[i]
            if char == '\n':
                last_newline = i + 1
                cont_newline += 1
            if word[i : i + 6] == 'lambda' and word[i : i + 6] in self.dfa.S:
                i += 6
                continue
            if char not in self.dfa.S and char.isalnum():
                char_idx = "EOF" if i == len(word) else str(i - last_newline)
                return [("", f"No viable alternative at character {char_idx}, line {cont_newline}")]
            i += 1

        i = 0
        j = len(word)
        result = []
        while i < j:

            final_state = self.finalState(word[i : j])
            if final_state != -1:
                for (token, accept_state) in self.tokens:
                    # token with highest priority
                    if list(accept_state)[0] in final_state:
                        result.append((token, word[i : j]))
                        break
                i = j
                j = len(word)
            else:
                # i == j - 1 means that no lexem can be found for any substring
                # that starts with the character word[i]
                if i == j - 1:
                    last_newline = 0
                    cont_newline = 0
                    for k in range(0, len(word[: j])):
                        if word[k] == '\n':
                            last_newline = k + 1
                            cont_newline += 1
                    char_idx = "EOF" if j == len(word) else str(j - last_newline)

                    return [("", f"No viable alternative at character {char_idx}, line {cont_newline}")]

                j -= 1
        return result
from .DFA import DFA
from dataclasses import dataclass
from collections.abc import Callable

EPSILON = ''  # This is how epsilon is represented by the checker in the transition function of NFAs

@dataclass
class NFA[STATE]:
    S: set[str]  # Set of input symbols
    K: set[STATE]  # Set of states
    q0: STATE  # Initial state
    d: dict[tuple[STATE, str], set[STATE]]  # Transition function
    F: set[STATE]  # Set of final states

    def epsilon_closure(self, state: STATE) -> set[STATE]:
        # Compute the epsilon closure of a state (you will need this for subset construction)
        # See the EPSILON definition at the top of this file
        visiting = [state]
        epsilon_set = {state}
        while visiting:
            first_state = visiting.pop(0)
            for transition, nfa_states in self.d.items():
                # Check if there is a transition to a state consuming EPSILON
                if transition[0] == first_state and transition[1] == EPSILON:
                    for state in nfa_states:
                        if state not in epsilon_set:
                            visiting.append(state)
                            epsilon_set.add(state)
        return epsilon_set

    def subset_construction(self) -> DFA[frozenset[STATE]]:
        all_eps_sets = {}
        for state in self.K:
            all_eps_sets[state] = self.epsilon_closure(state)

        dfa_S = self.S
        dfa_K = set()
        dfa_q0 = frozenset(all_eps_sets[self.q0])
        visiting = [dfa_q0]
        dfa_d = {}
        dfa_F = set()
        sink_state = frozenset(["sink"])
        dfa_K.add(sink_state)

        while visiting:
            current_state = visiting.pop(0)
            dfa_K.add(current_state)

            # Add to the DFA's final states if it is a final state in the NFA
            for nfa_final_state in current_state:
                if nfa_final_state in self.F:
                    dfa_F.add(current_state)
                    break

            for symbol in self.S:
                next_state = frozenset()
                # All states accessible from NFA through the current symbol
                for nfa_state in current_state:
                    transitions = self.d.get((nfa_state, symbol), set())

                    # Union of sets
                    for trans in transitions:
                        next_state |= all_eps_sets[trans]

                dfa_d[current_state, symbol] = next_state or sink_state
                if next_state and next_state not in dfa_K:
                    visiting.append(next_state)

        # Sink state consumes transitions on all symbols
        for symbol in self.S:
            dfa_d[(sink_state, symbol)] = sink_state
        return DFA(S=dfa_S, K=dfa_K, q0=dfa_q0, d=dfa_d, F=dfa_F)

    def remap_nfa_states[OTHER_STATE](self, f: 'Callable[[STATE], OTHER_STATE]') -> 'NFA[OTHER_STATE]':
        # Optional, but may be useful for the second stage of the project. Works similarly to 'remap_nfa_states'
        # from the DFA class. See the comments there for more details.
        pass

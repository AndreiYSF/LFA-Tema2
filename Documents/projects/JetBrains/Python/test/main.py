#!/usr/bin/env python3
import json
from collections import deque, defaultdict

def regex_to_postfix(regex):
    prec = {'*': 3, '+': 3, '?': 3, '.': 2, '|': 1}
    output = []
    stack = []
    new_regex = []
    prev = None
    for c in regex:
        if prev and (prev not in '(|' and c not in ')*+?|'):
            new_regex.append('.')
        new_regex.append(c)
        prev = c
    for c in new_regex:
        if c == '(':
            stack.append(c)
        elif c == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
        elif c in prec:
            while stack and stack[-1] != '(' and prec[stack[-1]] >= prec[c]:
                output.append(stack.pop())
            stack.append(c)
        else:
            output.append(c)
    while stack:
        output.append(stack.pop())
    return ''.join(output)

class State:
    def __init__(self):
        self.edges = []

def build_nfa(postfix):
    stack = []
    for c in postfix:
        if c == '.':
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            nfa1['end'].edges.append((None, nfa2['start']))
            stack.append({'start': nfa1['start'], 'end': nfa2['end']})
        elif c == '|':
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            start = State()
            end = State()
            start.edges += [(None, nfa1['start']), (None, nfa2['start'])]
            nfa1['end'].edges.append((None, end))
            nfa2['end'].edges.append((None, end))
            stack.append({'start': start, 'end': end})
        elif c == '*':
            nfa1 = stack.pop()
            start = State()
            end = State()
            start.edges += [(None, nfa1['start']), (None, end)]
            nfa1['end'].edges += [(None, nfa1['start']), (None, end)]
            stack.append({'start': start, 'end': end})
        elif c == '+':
            nfa1 = stack.pop()
            start = nfa1['start']
            end = State()
            nfa1['end'].edges += [(None, nfa1['start']), (None, end)]
            stack.append({'start': start, 'end': end})
        elif c == '?':
            nfa1 = stack.pop()
            start = State()
            end = State()
            start.edges += [(None, nfa1['start']), (None, end)]
            nfa1['end'].edges.append((None, end))
            stack.append({'start': start, 'end': end})
        else:
            start = State()
            end = State()
            start.edges.append((c, end))
            stack.append({'start': start, 'end': end})

    return stack.pop()

def lambda_area(states):
    stack = list(states)
    closure = set(states)
    while stack:
        st = stack.pop()
        for symbol, nxt in st.edges:
            if symbol is None and nxt not in closure:
                closure.add(nxt)
                stack.append(nxt)
    return closure

def move(states, symbol):
    result = set()
    for st in states:
        for sym, nxt in st.edges:
            if sym == symbol:
                result.add(nxt)
    return result

def nfa_to_dfa(nfa):
    start_cl = frozenset(lambda_area({nfa['start']}))
    unmarked = [start_cl]
    dfa_states = {start_cl: 0}
    dfa_trans = {}
    accept_states = set()
    if nfa['end'] in start_cl:
        accept_states.add(0)
    symbols = set()
    stack = [nfa['start']]
    seen = {nfa['start']}
    while stack:
        st = stack.pop()
        for sym, nxt in st.edges:
            if sym is not None:
                symbols.add(sym)
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    while unmarked:
        T = unmarked.pop()
        tid = dfa_states[T]
        dfa_trans[tid] = {}
        for sym in symbols:
            U = frozenset(lambda_area(move(T, sym)))
            if not U:
                continue
            if U not in dfa_states:
                dfa_states[U] = len(dfa_states)
                unmarked.append(U)
                if nfa['end'] in U:
                    accept_states.add(dfa_states[U])
            dfa_trans[tid][sym] = dfa_states[U]

    # for i in dfa_trans:
    #     for j in dfa_trans[i]:
    #         print(i, dfa_trans[i][j], j)
    return dfa_trans, 0, accept_states

def simulate_dfa(dfa_trans, start, accept, string):
    state = start
    for c in string:
        if c in dfa_trans.get(state, {}):
            state = dfa_trans[state][c]
        else:
            return False
    return state in accept

def main():
    with open('test.json', 'r', encoding='utf-8') as f:
        tests = json.load(f)
    for case in tests:
        name = case['name']
        regex = case['regex']
        print(f'Test set {name}: regex = "{regex}"')
        postfix = regex_to_postfix(regex)
        nfa = build_nfa(postfix)
        dfa_trans, start, accept = nfa_to_dfa(nfa)
        for t in case['test_strings']:
            inp = t['input']
            exp = t['expected']
            res = simulate_dfa(dfa_trans, start, accept, inp)
            status = 'OK' if res == exp else 'FAIL'
            print(f'Input "{inp}": expected={exp}, got={res} -> {status}')
        print()

if __name__ == '__main__':
    main()
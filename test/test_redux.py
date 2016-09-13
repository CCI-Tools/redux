import unittest
from collections import namedtuple

from redux import create_store, combine_reducers

Todo = namedtuple('Todo', ['id', 'text', 'completed'])


class TodoAction:
    def __init__(self, type, id=None, text=None, filter=None):
        self.type = type
        self.id = id
        self.text = text
        self.filter = filter


def todo(state, action):
    if action.type == 'ADD_TODO':
        return Todo(action.id, action.text, False)
    elif action.type == 'TOGGLE_TODO':
        if action.id == state.id:
            return Todo(state.id, state.text, not state.completed)
    return state


def todos(state, action):
    if state is None:
        return []
    elif action.type == 'ADD_TODO':
        return state + [todo(state, action)]
    elif action.type == 'TOGGLE_TODO':
        return list(map(lambda t: todo(t, action), state))
    else:
        return state


def visibility_filter(state, action):
    if state is None:
        return 'SHOW_ALL'
    elif action.type == 'SET_VISIBILITY_FILTER':
        return action.filter
    else:
        return state


class ReduxTodoTest(unittest.TestCase):
    def test_add_todo(self):
        state_before = []
        action = TodoAction('ADD_TODO', id=0, text='Learn Redux')
        state_after = [Todo(0, 'Learn Redux', False)]

        state = todos(state_before, action)
        self.assertEquals(state, state_after)

    def test_toggle_todo(self):
        state_before = [Todo(0, 'Learn Redux', False),
                        Todo(1, 'Go shopping', False)]
        action = TodoAction('TOGGLE_TODO', id=0)
        state_after = [Todo(0, 'Learn Redux', True),
                       Todo(1, 'Go shopping', False)]

        state = todos(state_before, action)
        self.assertEquals(state, state_after)

    def test_set_visibility_filter(self):
        state_before = {'todos': [Todo(0, 'Learn Redux', False),
                                  Todo(1, 'Go shopping', False)],
                        'visibility_filter': 'SHOW_ALL'}
        action = TodoAction('SET_VISIBILITY_FILTER', filter='SHOW_COMPLETED')
        state_after = {'todos': [Todo(0, 'Learn Redux', False),
                                 Todo(1, 'Go shopping', False)],
                       'visibility_filter': 'SHOW_COMPLETED'}

        todo_app = combine_reducers(todos=todos, visibility_filter=visibility_filter)

        state = todo_app(state_before, action)
        self.assertEquals(state, state_after)


CounterAction = namedtuple('CounterAction', ['type'], verbose=True)


def counter(state=None, action=None):
    if state is None:
        return 0
    elif action.type == 'INC_COUNTER':
        return state + 1
    elif action.type == 'DEC_COUNTER':
        return state - 1
    else:
        return state


class CounterListener:
    def __init__(self):
        self.trace = ''

    def __call__(self, old_state, new_state):
        self.trace += '%s->%s; ' % (old_state, new_state)


class ReduxCounterTest(unittest.TestCase):
    def test_counter(self):
        self.assertEquals(counter(0, CounterAction('INC_COUNTER')), 1)
        self.assertEquals(counter(1, CounterAction('INC_COUNTER')), 2)
        self.assertEquals(counter(2, CounterAction('DEC_COUNTER')), 1)
        self.assertEquals(counter(1, CounterAction('DEC_COUNTER')), 0)
        self.assertEquals(counter(0, CounterAction('UNKNOWN')), 0)


class ReduxStoreTest(unittest.TestCase):
    def test_dispatch(self):
        store = create_store(counter)
        self.assertEquals(store.state, 0)
        store.dispatch(CounterAction('INC_COUNTER'))
        self.assertEquals(store.state, 1)
        store.dispatch(CounterAction('INC_COUNTER'))
        self.assertEquals(store.state, 2)
        store.dispatch(CounterAction('DEC_COUNTER'))
        self.assertEquals(store.state, 1)
        store.dispatch(CounterAction('DEC_COUNTER'))
        self.assertEquals(store.state, 0)
        store.dispatch(CounterAction('UNKNOWN'))
        self.assertEquals(store.state, 0)

    def test_subscribe(self):
        listener = CounterListener()

        store = create_store(counter)
        remove_listener = store.subscribe(listener)
        store.dispatch(CounterAction('INC_COUNTER'))
        store.dispatch(CounterAction('INC_COUNTER'))
        store.dispatch(CounterAction('DEC_COUNTER'))
        store.dispatch(CounterAction('DEC_COUNTER'))
        store.dispatch(CounterAction('UNKNOWN'))

        self.assertEquals(listener.trace, '0->1; 1->2; 2->1; 1->0; ')

        listener.trace = ''
        remove_listener()

        store.dispatch(CounterAction('INC_COUNTER'))

        self.assertEquals(listener.trace, '')

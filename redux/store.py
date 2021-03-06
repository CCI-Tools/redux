# The MIT License (MIT)
#
# Copyright (c) 2016 by Norman Fomferra
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from collections import OrderedDict
from typing import Callable, Any, Mapping, Type

StateType = Any
ActionType = Any
VoidType = None
ReducerFunction = Callable[[StateType, ActionType], StateType]
ListenerFunction = Callable[[StateType, StateType], VoidType]
UnsubscribeFunction = Callable[[], VoidType]


class Store:
    """
    Return type of the :py:func:`create_store` function.

    :param reducer: a "pure" function that takes two arguments *state*, *action* and returns a new state.
    """

    def __init__(self, reducer: ReducerFunction):
        self._reducer = reducer
        self._state = None
        self._listeners = []

    @property
    def state(self) -> StateType:
        """
        :return: The store's current (immutable) state (tree).
        """
        return self._state

    def dispatch(self, action: ActionType) -> VoidType:
        """
        Dispatch an *action* to compute a new state from the old one using this store's reducer.
        Notifies subscribed listeners about the state change.

        :param action: An application-specific action object
        """
        prev_state = self._state
        new_state = self._reducer(prev_state, action)
        self._state = new_state
        if prev_state is not new_state:
            for listener in self._listeners:
                listener(prev_state, new_state)

    def subscribe(self, listener: ListenerFunction) -> UnsubscribeFunction:
        """
        Subscribe to this store by given *listener*.
        Calls all registered listeners with two positional arguments: *old_state*, *new_state*.

        :param listener: A callable with two positional arguments
        :return: a function which can be invoked to unregister *listener* from subscription
        """
        if listener not in self._listeners:
            self._listeners.append(listener)

        def remove_listener():
            if listener in self._listeners:
                self._listeners.remove(listener)

        return remove_listener


def create_store(reducer: ReducerFunction) -> Store:
    """
    Create a :py:class`Store` with the initial state set.

    An application typically maintains only a single ``Store`` instance.

    :param reducer: a "pure" function that takes two arguments *state*, *action* and returns a new state.
    :return: an instance of :py:class`Store`
    """
    store = Store(reducer)
    store.dispatch(None)
    return store


def combine_reducers(_state_factory_: Type = None, **reducers: Mapping[str, ReducerFunction]) -> ReducerFunction:
    """
    Return a reducer function that takes two arguments *state*, *action* and returns a new state.
    The new state is computed from the individual reducer functions in the *reducers* dictionary.

    If *state_factory* is given, it is expected to be a callable of the form ``state_factory(**kwargs)``.
    It will be called with *kwargs* being the dictionary resulting from calling individual reducers in
    *reducers*. If *state_factory* is given, all keys in *reducers* are expected to be writable
    attributes / properties of the *state* passed into the combined reducer function.

    If *state_factory* is ``None``, the combined reducer function will generate an ordered dictionary
    and *state* is expected to be a subscriptable object (e.g. ``dict``, ``OrderedDict``) whose keys
    will be set from the keys in *reducers*.

    :param _state_factory_: a factory for new state instances
    :param reducers: mapping from names to reducer functions.
    :return: a new reducer function that combines the results of given *reducers*
    """
    if _state_factory_ is None:
        def reduce(state, action):
            return OrderedDict([(name, reducer(state[name], action)) for name, reducer in reducers.items()])
    else:
        def reduce(state, action):
            kwargs = OrderedDict([(name, reducer(getattr(state, name), action)) for name, reducer in reducers.items()])
            return _state_factory_(**kwargs)
    return reduce

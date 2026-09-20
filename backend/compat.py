"""Compatibilidad de Experta/frozendict con versiones modernas de Python."""
import collections
import collections.abc

for nombre in ("Mapping", "MutableMapping", "Sequence"):
    if not hasattr(collections, nombre):
        setattr(collections, nombre, getattr(collections.abc, nombre))


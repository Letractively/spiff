__all__ = ['DocumentModel']

for module in __all__:
    eval('from %s import %s' % module)

__all__ = ['Parser', 'Reader']

for module in __all__:
    eval('from %s import %s' % module)

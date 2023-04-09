
class Step(object):
    ''' Step class '''

    def __init__(self, name, description, function, *args, **kwargs):
        self.name = name
        self.description = description
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        return self.function(*self.args, **self.kwargs)

    def __str__(self) -> str:
        return f"Step(name={self.name}, description={self.description}, function={self.function}, args={self.args}, kwargs={self.kwargs})"

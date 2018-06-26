
class ArgParser:

    def __init__(self):
        self.arg_schema = {}

    def add(self, name, conversion_function=str, default=None, required=False):
        self.arg_schema[name] = {
            'conversion_function': conversion_function,
            'default': default,
            'required': required
        }
    
    def parse_args(self, request, method):
        args = {}
        request_args = getattr(request, method)
        for arg, schema in self.arg_schema.items():
            if arg not in request_args and schema['required'] == True:
                raise Exception('Missing required argument, {}'.format(arg))
            elif arg not in request_args:
                args[arg] = schema['default']
            else:
                args[arg] = schema['conversion_function'](request_args[arg])
        return args

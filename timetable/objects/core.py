from base import *

''' Register a URL for a function and give it a database session. Intended for use as a function decorator. '''
def register(f):
    f = db_session(f)
    rule = '/' + f.__name__.replace('_', '/')
    methods=('GET', )
    if (rule.endswith('/bearbeiten')):
        rule = rule[:-11] + '/<int:id>'
        methods=('GET', 'POST')
    elif (rule.endswith('/auflisten')):
        rule = rule[:-9]
    elif (rule.endswith('/anlegen')):
        methods=('GET', 'POST')
    else:
        raise Exception("I don't know how to register this type of function!")
    app.add_url_rule(rule, None, f, methods=methods)
    return f

def anzeigen(cls, id):
    result = get(obj for obj in cls if obj.id == id)
    if not result:
        abort(404)
    return str(result)

class ObjectForm(Form):
    vollstrecken = SubmitField()
    def render(self):
        return render_template_string('''
<form action="" method="POST"><table border="0" cellpadding="0" cellspacing="8">
''' + self.renderstring() + '''
<tr><td colspan="2">{{ form.vollstrecken }}{{ form.csrf_token }}</td></tr></table></form>
''', form=self)

    def renderstring(self):
        raise NotImplementedError()

    @property
    def singular(self):
        return self.cls._singular_
    @property
    def plural(self):
        return self.cls._plural_
    @property
    def list(self):
        return select(obj for obj in self.cls)
    @property
    def find(self, id):
        return get(obj for obj in self.cls if obj.id==id)
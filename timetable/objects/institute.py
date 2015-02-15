from .core import *

class InstitutForm(ObjectForm):
    name = StringField('name', validators=[DataRequired()], default='unbenannt')
    code = StringField('code', validators=[Length(min=3, max=3)], default='???')
    cls = Institut
    def renderstring(self):
        return '''
<tr><td>{{form.name.label('Name:')}}</td><td>{{form.name}}</td></tr>
<tr><td>{{form.code.label('Code:')}}</td><td>{{form.code}}</td></tr>
'''

@register
def institute_bearbeiten(id):
    obj = get(o for o in Institut if o.id==id)
    if not obj: abort(404)
    form = InstitutForm(obj=obj)
    if form.validate_on_submit():
        form.populate_obj(obj)
        flash('{} erfolgreich bearbeitet.'.format(obj))
        return redirect(request.url_rule.rule[:-len('<int:id>')])
    else:
        return render_template('objekt_bearbeiten.html', form=form)

@register
def institute_auflisten():
    form = InstitutForm()
    return render_template('objekte_auflisten.html', form=form)

@register
def institute_anlegen():
    form = InstitutForm()
    if form.validate_on_submit():
        obj = Institut(name=form.name.data, code=form.code.data)
        flash('{} erfolgreich angelegt.'.format(obj))
        return redirect(request.url_rule.rule[:-len('anlegen')])
    else:
        return render_template('objekt_anlegen.html', form=form)


class InstitutManager:
    cls = Institut
    def institute_bearbeiten(self, id):
        obj = get(o for o in self.cls if o.id==id)
        if not obj: abort(404)
        form = InstitutForm(obj=obj)
        if form.validate_on_submit():
            form.populate_obj(obj)
            flash('{} erfolgreich bearbeitet.'.format(obj))
            return redirect('/{}/'.format(self.cls.plural))
        else:
            return render_template('objekt_bearbeiten.html', form=form)

    def institute_auflisten(self):
        form = InstitutForm()
        return render_template('objekte_auflisten.html', form=form)

    def institute_anlegen(self):
        form = InstitutForm()
        if form.validate_on_submit():
            obj = Institut(name=form.name.data, code=form.code.data)
            flash('{} erfolgreich angelegt.'.format(obj))
            return redirect('/{}/'.format(self.cls.plural))
        else:
            return render_template('objekt_anlegen.html', form=form)


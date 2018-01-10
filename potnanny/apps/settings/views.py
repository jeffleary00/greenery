from flask import render_template, redirect, request, session, Blueprint
from flask_login import login_required
from potnanny.extensions import db
from .models import Setting
from .forms import SettingForm

settings = Blueprint('settings', __name__,
                        template_folder='templates')


## system settings pages ##
###########################
@settings.route('/settings')
@login_required
def index():
    results = Setting.query.all()
    return render_template('settings/index.html', 
                title='System Settings',
                payload=results)


@settings.route('/settings/<int:pk>/edit', methods=['GET','POST'])
@login_required
def edit(pk):
    title = 'Edit Setting'
    obj = Setting.query.get_or_404(pk)    
    form = SettingForm(obj=obj)  
    if request.method == 'POST' and form.validate_on_submit():
        form.populate_obj(obj)
        db.session.commit()
        return redirect(request.args.get("next", "/settings"))
    
    return render_template('settings/form.html', 
        form=form,
        title=title,
        pk=pk,
        setting=obj,
        name=obj.name)


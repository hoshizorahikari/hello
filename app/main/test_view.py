from ..decorators import admin_required, permission_required
from ..models import Permission
from . import main
from flask_login import login_required


@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return '管理员专享！'


@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE)
def for_moderators_only():
    return '协助管理员专享！'

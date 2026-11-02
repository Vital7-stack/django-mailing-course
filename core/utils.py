from accounts.models import UserProfile

def can_view_mailing(user, mailing):
    """Возвращает True, если пользователь имеет право просматривать рассылку"""
    if not user.is_authenticated:
        return False

    profile = user.profile
    if profile.role == 'manager':
        return True

    # обычный пользователь: только свои рассылки
    return mailing.owner == user
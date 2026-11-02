from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.db import transaction
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.cache import cache_page

# Модели рассылок — из текущего приложения core
from .models import Mailing, Attempt, Recipient

# Профиль — из приложения accounts (именно UserProfile, как у тебя в accounts/models.py)
from accounts.models import UserProfile

from .forms import MailingForm


# --- ХЕЛПЕР: безопасное получение профиля ---
def get_user_profile(user):
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={'role': UserProfile.ROLE_USER}
    )
    return profile


# === ФУНКЦИОНАЛЬНЫЕ ПРЕДСТАВЛЕНИЯ ===

@login_required
def index(request):
    total_mailings = Mailing.objects.count()
    now = timezone.now()
    active_mailings = Mailing.objects.filter(
        start_time__lte=now,
        end_time__gte=now
    ).count()

    # Используем Recipient вместо несуществующего Client
    unique_recipients = Recipient.objects.count()

    context = {
        'total_mailings': total_mailings,
        'active_mailings': active_mailings,
        'unique_recipients': unique_recipients,
    }
    return render(request, 'core/index.html', context)


@login_required
@cache_page(60 * 5)  # Кэш на 5 минут
def user_stats(request):
    user = request.user
    profile = get_user_profile(user)

    if profile.role == UserProfile.ROLE_MANAGER:
        attempts = Attempt.objects.all()
    else:
        attempts = Attempt.objects.filter(mailing__owner=user)

    # Важно: используем константы статусов из модели Attempt (если они там есть)
    # Если в модели их нет — смотри примечание ниже
    context = {
        'total_attempts': attempts.count(),
        'successful': attempts.filter(status=Attempt.STATUS_SUCCESS).count(),
        'failed': attempts.filter(status=Attempt.STATUS_FAILED).count(),
    }
    return render(request, 'core/user_stats.html', context)


@transaction.atomic
@login_required
def start_mailing(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    user = request.user
    profile = get_user_profile(user)

    # Проверка прав на запуск
    if profile.role != UserProfile.ROLE_MANAGER and mailing.owner != user:
        messages.error(request, "Вы не можете запускать чужие рассылки.")
        return redirect('mailing_detail', pk=mailing.pk)

    now = timezone.now()
    if now < mailing.start_time or now > mailing.end_time:
        messages.error(
            request,
            f"Отправка возможна только в интервале: {mailing.start_time} — {mailing.end_time}"
        )
        return redirect('mailing_detail', pk=mailing.pk)

    mailing.update_status()
    sent_count = 0
    failed_count = 0

    if not mailing.message:
        messages.error(request, "У рассылки нет сообщения.")
        return redirect('mailing_detail', pk=mailing.pk)

    for recipient in mailing.recipients.all():
        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email='noreply@example.com',
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            status = Attempt.STATUS_SUCCESS
            server_response = "OK"
            sent_count += 1
        except Exception as e:
            status = Attempt.STATUS_FAILED
            server_response = str(e)
            failed_count += 1

        Attempt.objects.create(
            attempt_time=timezone.now(),
            status=status,
            server_response=server_response,
            mailing=mailing,
        )

    messages.success(request, f"Рассылка завершена: {sent_count} отправлено, {failed_count} ошибок.")
    return redirect('mailing_detail', pk=mailing.pk)


@login_required
def mailing_list(request):
    user = request.user
    profile = get_user_profile(user)

    if profile.role == UserProfile.ROLE_MANAGER:
        mailings = Mailing.objects.all()
    else:
        mailings = Mailing.objects.filter(owner=user)

    return render(request, 'core/mailing_list.html', {'mailings': mailings})


# === КЛАССЫ ПРЕДСТАВЛЕНИЙ (CBV) ===

class OwnerOrManagerMixin(LoginRequiredMixin):
    """Миксин: менеджер видит всё, обычный пользователь — только свои объекты"""
    def dispatch(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if pk:
            obj = get_object_or_404(self.model, pk=pk)
            user = request.user
            profile = get_user_profile(user)
            if profile.role != UserProfile.ROLE_MANAGER and obj.owner != user:
                raise PermissionDenied("У вас нет прав на этот объект")
        return super().dispatch(request, *args, **kwargs)


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'core/mailing_form.html'
    success_url = reverse_lazy('mailing_list')

    def form_valid(self, form):
        mailing = form.save(commit=False)
        mailing.owner = self.request.user
        mailing.save()
        form.save_m2m()
        messages.success(self.request, "Рассылка создана!")
        return super().form_valid(form)


class MailingDetailView(OwnerOrManagerMixin, DetailView):
    model = Mailing
    template_name = 'core/mailing_detail.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        profile = get_user_profile(user)
        if profile.role != UserProfile.ROLE_MANAGER and obj.owner != user:
            raise PermissionDenied("Вы не можете просматривать чужие рассылки")

        # Обновление статуса при заходе на страницу
        obj.update_status()
        return obj


class MailingUpdateView(OwnerOrManagerMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'core/mailing_form.html'
    success_url = reverse_lazy('mailing_list')

    def form_valid(self, form):
        messages.success(self.request, "Рассылка обновлена!")
        return super().form_valid(form)


class MailingDeleteView(OwnerOrManagerMixin, DeleteView):
    model = Mailing
    template_name = 'core/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing_list')

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, "Рассылка удалена.")
        return response
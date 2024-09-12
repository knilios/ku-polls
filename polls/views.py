from .models import Choice, Question, Vote
from django.db.models import F
from django.db.models.query import QuerySet
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import user_logged_in, user_login_failed, user_logged_out
from django.dispatch import receiver, Signal


import logging
logger = logging.getLogger(__name__)


class IndexView(generic.ListView):
    """This class handles the index page"""
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions.
            (not including those set to be published in the future)
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")


class DetailView(generic.DetailView):
    """This class handles the detail page"""
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """
        Excludes any question that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get_context_data(self, **kwargs) -> dict:
        logger.debug("hello")
        _context = super().get_context_data(**kwargs)
        question = self.get_object()
        user = self.request.user
        if not user.is_authenticated:
            return _context
        marked = user.vote_set.filter(choice__question=question)
        logger.debug("The user is authenticated")
        if marked:
            _context["marked"] = marked[0].choice
        return _context

    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        """
        This method redirects the user if the polls does not exists.
        """
        try:
            question = self.get_object()
            if (not question.can_vote()):
                if (not question.is_published()):
                    return redirect(reverse("polls:index"))
                messages.error(request, "This poll is already closed.")
                return redirect(reverse("polls:results", args=[question.id]))
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return redirect(reverse("polls:index"))


class ResultsView(generic.DetailView):
    """This class handles the detail page"""
    model = Question
    template_name = "polls/results.html"

    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        """
        This method redirects the user if the polls does not exists.
        """
        try:
            question = self.get_object()
            if (not question.is_published()):
                return redirect(reverse("polls:index"))
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return redirect(reverse("polls:index"))


def vote(request, question_id):
    logger.info("Vote submitted for poll #{0}".format(question_id))
    """This function handles the POST request from the using voting on the poll"""
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
        logger.info("Question {0} vote for choice {1}".format(question_id, request.POST["choice"]))
    except (KeyError, Choice.DoesNotExist):
        logger.error("The choice has not been selected for the question {0}.".format(question_id))
        messages.error(
            request, "You didn't select a choice. Please consider doing so.")
        return render(
            request,
            "polls/detail.html",
            {
                "question": question
            },
        )
    # Referencing the current user
    this_user = request.user
    if not this_user.is_authenticated:
        next_url = reverse('polls:detail', args=[question_id])
        redirect_url = reverse('login')
        return HttpResponseRedirect(f"{redirect_url}?next={next_url}")
    try:
        # When the user already vote for this option
        vote = this_user.vote_set.get(choice__question=question)
        vote.choice = selected_choice
    except Vote.DoesNotExist:
        vote = Vote.objects.create(user=this_user, choice=selected_choice)

    vote.save()
    # Always return a redirect after a POST request. :D
    return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))

def get_client_ip(request):
    """ Retrieve ip from the user"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@receiver(user_logged_in)
def user_logged_in_successfully(sender, request, user, **kwargs):
    """Log the user loggin in"""
    ip_addr = get_client_ip(request)
    logger.info(f'{user.username} logged in at the ip address: {ip_addr}')
    
@receiver(user_logged_out)
def user_logged_out_successfully(sender, request, user, **kwargs):
    """Log the user loggin in"""
    ip_addr = get_client_ip(request)
    logger.info(f'{user.username} logged out at the ip address: {ip_addr}')
    
@receiver(user_login_failed)
def user_logged_in_successfully(sender, request, credentials, **kwargs):
    """Log the user loggin in"""
    ip_addr = get_client_ip(request)
    logger.warning(f'{credentials["username"]} from {ip_addr} tried to login but failed.')

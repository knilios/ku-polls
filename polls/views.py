from django.db.models import F
from django.db.models.query import QuerySet
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages

from .models import Choice, Question


class IndexView(generic.ListView):
    """This class handles the index page"""
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions.
            (not including those set to be published in the future)
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5]


class DetailView(generic.DetailView):
    """This class handles the detail page"""
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """
        Excludes any question that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        """
        This method redirects the user if the polls does not exists.
        """
        try:
            return super().dispatch(request, *args, **kwargs)
        # get objector404 and now we can do anything with that
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
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return redirect(reverse("polls:index"))


def vote(request, question_id):
    """This function handles the POST request from the using voting on the poll"""
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except Exception:
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
    # TODO
    # Follow this tutorial https://cpske.github.io/ISP/assignment/ku-polls/iteration3-vote-class-and-view
    
    # Get the user's vote
    # try:
    #     # vote = this_user.vote_set.get()
    #     vote = Vote.objects.get(user=this_user, choice=Choice)
    selected_choice.votes = F('votes') + 1
    selected_choice.save()
    # Always return a redirect after a POST request. :D
    return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))

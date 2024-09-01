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
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions.
            (not including those set to be published in the future)
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5]
    
    
class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"
    
    def get_queryset(self):
        """
        Excludes any question that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())
    
    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return redirect(reverse("polls:index"))
    

class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"
    
    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return redirect(reverse("polls:index"))
    

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except Exception:
        messages.error(request, "You didn't select a choice. Please consider doing so.")
        return render(
            request,
            "polls/detail.html",
            {
                "question":question
            },
        )
    else:
        selected_choice.votes = F('votes') + 1
        selected_choice.save()
        # Always return a redirect after a POST request. :D
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
    

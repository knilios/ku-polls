"""Models for polls application"""

import datetime

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Question(models.Model):
    """The question of the poll. Contains the text and publication date.
    """
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published", default=timezone.now)
    end_date = models.DateTimeField(
        "date published", null=True, default=None, blank=True)

    def __str__(self) -> str:
        """
        return question text
        """
        return self.question_text

    def was_published_recently(self) -> bool:
        """check whether the question was published within 24 hours.

        Returns:
            boolean
        """
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def can_vote(self) -> bool:
        """Check whether the poll is still votable"""
        if self.end_date is None:
            return True
        if (self.end_date.date()
                >= timezone.now().date()
                and self.is_published()):
            return True
        else:
            return False

    def is_published(self) -> bool:
        """Check whether the poll has been created
        and ready to be deployed or not."""
        if (self.pub_date.date()
                <= timezone.now().date()):
            return True
        else:
            return False


class Choice(models.Model):
    """
    It's the choice of the poll question.
    It contains the number of votes and the text.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    # votes = models.IntegerField(default=0)

    @property
    def votes(self) -> int:
        """Return the number of votes"""
        return self.vote_set.count()

    def __str__(self):
        """
        Return the text of the choice.
        """
        return self.choice_text


class Vote(models.Model):
    """A bote by a user for a choice in a poll"""

    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

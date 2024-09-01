"""Models for polls application"""

import datetime

from django.db import models
from django.utils import timezone

class Question(models.Model):
    """The question of the poll. Contains the text and publication date.
    """
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    end_date = models.DateTimeField("date published", null=True)
    
    def __str__(self):
        """
        return question text
        """
        return self.question_text
    
    def was_published_recently(self): 
        """check whether the question was published within 24 hours.

        Returns:
            boolean
        """
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now
        
        
class Choice(models.Model):
    """
    It's the choice of the poll question. It contains the number of votes and the text.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    
    def __str__(self):
        """
        Return the text of the choice.
        """
        return self.choice_text

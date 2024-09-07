import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for question that have to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionModelTests(TestCase):
    """This class handle the testing of the Question class."""

    def test_no_question(self):
        """
        If no quesions exist, an appropriate message is displayed
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")

    def test_past_question(self):
        """
        Question with a pub_date in the past are displayed on the
        index page.
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question2, question1],
        )

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)

        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_can_vote_with_end_date_already_passed(self):
        """Test can_vote method with a question that the end_date has already passed"""
        pub_date = timezone.now() + datetime.timedelta(days=-10)
        end_date = timezone.now() + datetime.timedelta(days=-1)
        expired_question = Question.objects.create(
            question_text="Hello", pub_date=pub_date, end_date=end_date)
        self.assertIs(expired_question.can_vote(), False)

    def test_can_vote_with_today_is_not_in_the_voting_range(self):
        """
        Test can_vote method when today is not in the middle of pub_date and end_date.
        It must result in false.
        """
        pub_date = timezone.now() + datetime.timedelta(days=10)
        end_date = timezone.now() + datetime.timedelta(days=20)
        present_question = Question.objects.create(
            question_text="Hello", pub_date=pub_date, end_date=end_date)
        self.assertIs(present_question.can_vote(), False)

    def test_can_vote_with_end_date_in_the_future(self):
        """
        Test can_vote method with a question that the end_date is in the future.
        It must result in true.
        """
        pub_date = timezone.now() + datetime.timedelta(days=-10)
        end_date = timezone.now() + datetime.timedelta(days=10)
        present_question = Question.objects.create(
            question_text="Hello", pub_date=pub_date, end_date=end_date)
        self.assertIs(present_question.can_vote(), True)

    def test_can_vote_with_end_date_is_null(self):
        """
        Test can_vote method with a question that the end_date is null.
        It must result in true.
        """
        pub_date = timezone.now() + datetime.timedelta(days=-10)
        present_question = Question.objects.create(
            question_text="Hello", pub_date=pub_date)
        self.assertIs(present_question.can_vote(), True)

    def test_is_published_pub_date_in_the_past(self):
        """
        Test is_published with a question which pub_date is in the past. It should return true. 
        """
        pub_date = timezone.now() + datetime.timedelta(days=-10)
        end_date = timezone.now() + datetime.timedelta(days=10)
        present_question = Question.objects.create(
            question_text="Hello", pub_date=pub_date, end_date=end_date)
        self.assertIs(present_question.is_published(), True)

    def test_is_published_pub_date_in_the_future(self):
        """
        Test is_published with a question which pub_date is in the past. It should return false. 
        """
        pub_date = timezone.now() + datetime.timedelta(days=10)
        present_question = Question.objects.create(
            question_text="Hello", pub_date=pub_date)
        self.assertIs(present_question.is_published(), False)

    def test_is_published_pub_date_is_not_given(self):
        """
        Test is_published with a question which pub_date is not specified. It should return true.
        """
        present_question = Question.objects.create(question_text="Hello")
        self.assertIs(present_question.is_published(), True)


class QuestionDetailViewTests(TestCase):
    """This class handle the testing of the Question class functionality in the view"""

    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 302 temporary redirects back to the index page.
        """
        future_question = create_question(
            question_text="Future question.", days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(
            question_text="Past Question.", days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_closed_question(self):
        """
        The detail view of a question with a pub_date in the past
        and a end_date in the past.
        """
        create_date = timezone.now() + datetime.timedelta(days=-10)
        end_date = timezone.now() + datetime.timedelta(days=-5)
        question_text = "Is Africa a country?"
        closed_question = Question.objects.create(
            question_text=question_text, pub_date=create_date, end_date=end_date)
        url = reverse("polls:detail", args=(closed_question.id,))
        response = self.client.get(url)
        self.assertRedirects(
            response,
            reverse("polls:results", args=[closed_question.id]),
            status_code=302,
            target_status_code=200
        )
        

class QuestionResultsViewTest(TestCase):
    """Tests the Question class in the Results page"""
    
    def test_future_question(self):
        """
        The results view of a question with a pub_date in the future
        returns a 302 temporary redirects back to the index page.
        """
        future_question = create_question(
            question_text="Future question.", days=5)
        url = reverse("polls:results", args=(future_question.id,))
        response = self.client.get(url)
        self.assertRedirects(
            response,
            reverse("polls:index"),
            status_code=302,
            target_status_code=200
        )

    def test_past_question(self):
        """
        The results view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(
            question_text="Past Question.", days=-5)
        url = reverse("polls:results", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_closed_question(self):
        """
        The results view of a question with a pub_date in the past
        and a end_date in the past.
        """
        create_date = timezone.now() + datetime.timedelta(days=-10)
        end_date = timezone.now() + datetime.timedelta(days=-5)
        question_text = "Is Africa a country?"
        closed_question = Question.objects.create(
            question_text=question_text, pub_date=create_date, end_date=end_date)
        url = reverse("polls:results", args=(closed_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
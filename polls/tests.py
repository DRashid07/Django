import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Question, Choice


def create_question(question_text: str, days: float, choices: list[str] | None = None):
    time = timezone.now() + datetime.timedelta(days=days)
    question = Question.objects.create(question_text=question_text, pub_date=time)
    for choice_text in choices or []:
        Choice.objects.create(question=question, choice_text=choice_text)
    return question


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        future_question = create_question("Gələcək sual", days=30)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        old_question = create_question("Köhnə sual", days=-2)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        recent_question = create_question("Təzə sual", days=-0.5)
        self.assertIs(recent_question.was_published_recently(), True)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hələ yenilik yoxdur.")
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [],
            transform=lambda x: x,
        )

    def test_past_question(self):
        question = create_question("Keçmiş sual", days=-1)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [question],
            transform=lambda x: x,
        )

    def test_future_question(self):
        create_question("Gələcək sual", days=1)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "Hələ yenilik yoxdur.")

    def test_future_question_and_past_question(self):
        question = create_question("Keçmiş sual", days=-1)
        create_question("Gələcək sual", days=1)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [question],
            transform=lambda x: x,
        )

    def test_two_past_questions(self):
        question1 = create_question("Keçmiş sual 1", days=-3)
        question2 = create_question("Keçmiş sual 2", days=-1)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [question2, question1],
            transform=lambda x: x,
        )


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        future_question = create_question("Gələcək sual", days=1)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        past_question = create_question("Keçmiş sual", days=-1)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class VoteViewTests(TestCase):
    def test_vote_increments_choice(self):
        question = create_question("Səs test", days=-1, choices=["A", "B"])
        choice = question.choice_set.first()
        response = self.client.post(
            reverse("polls:vote", args=(question.id,)),
            {"choice": choice.id},
        )
        self.assertRedirects(response, reverse("polls:results", args=(question.id,)))
        choice.refresh_from_db()
        self.assertEqual(choice.votes, 1)

    def test_vote_without_choice_shows_error(self):
        question = create_question("Seçimsiz səs", days=-1, choices=["A"])
        response = self.client.post(reverse("polls:vote", args=(question.id,)), {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Siz seçim etmədiniz.")

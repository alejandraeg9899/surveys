from django.test import Client
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone
from .models import Question

import datetime

def create_question(question_text, days):
    '''
    Publicación de una pregunta junto con el día
    '''
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        '''
        Si la pregunta no existe se lanza un msj
        '''
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No hay encuestas disponibles.')
        self.assertQuerySetEqual(response.content['latest_question_list'], [])

    def test_past_question(self):
        '''
        Las preguntas con fecha de publicación se muestran en el índice.
        '''
        question = create_question(question_text='Encuestas pasadas.', days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerySetEqual(
            response.content['latest_question_list'], [question],
        )

    def test_future_question(self):
        '''
        Las preguntas con fecha de publicación futura no se muestran en la pág del índice.
        '''
        create_question(question_text='Preguntas futuras.', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, 'No hay encuestas disponibles.')
        self.assertQuerySetEqual(response.content['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        '''
        Solo se muestran las preguntas con fecha de publicación vigente
        '''
        question = create_question(question_text='Preguntas pasadas.', days=-30)
        create_question(question_text='Preguntas futuras.', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerySetEqual(
            response.content['latest_question_list'], [question],
        )

    def test_two_past_questions(self):
        '''
        La pág índice puede mostrar varias preguntas.
        '''
        question1 = create_question(question_text='Pregunta pasada 1.', days=-30)
        question2 = create_question(question_text='Pregunta pasada 2.', days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerySetEqual(
            response.content['latest_question_list'], [question2, question1],
        )

class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        '''
        was_published_recently() retorna False para preguntas publicadas en el futuro
        '''
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        '''
        was_published_recently() retorna False para preguntas publicadas en el pasado
        '''
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        '''
        was_published_recently() retorna True para preguntas publicadas dentro del dia actual
        '''
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        '''
        La vista de una pregunta en el futuro devuelve un error 404.
        '''
        future_question = create_question(question_text='Preguntas futuras.', days=5)
        url = reverse('polls:detail', args=(future_question.id, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        '''
        La vista de una pregunta en el pasado muestra el texto de la pregnta.
        '''
        past_question = create_question(question_text='Preguntas pasadas.', days=-5)
        url = reverse('polls:detail', args=(past_question.id, ))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
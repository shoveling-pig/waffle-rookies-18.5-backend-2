from django.contrib.auth.models import User
from django.test import Client, TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
import json

from user.models import User
from seminar.models import Seminar, UserSeminar

class PostSeminarTestCase(TestCase):
    client = Client()

    def setUp(self):
        self.client.post(
            '/api/v1/user/',
            json.dumps({
                "username": "part",
                "password": "password",
                "first_name": "Davin",
                "last_name": "Byeon",
                "email": "bdv111@snu.ac.kr",
                "role": "participant",
                "university": "서울대학교"
            }),
            content_type='application/json'
        )
        self.participant_token = 'Token ' + Token.objects.get(user__username='part').key

        self.client.post(
            '/api/v1/user/',
            json.dumps({
                "username": "inst",
                "password": "password",
                "first_name": "Davin",
                "last_name": "Byeon",
                "email": "bdv111@snu.ac.kr",
                "role": "instructor",
                "university": "서울대학교"
            }),
            content_type='application/json'
        )
        self.instructor_token = 'Token ' + Token.objects.get(user__username='inst').key

        self.client.post(
            '/api/v1/seminar/',
            json.dumps({
                "name": "Backend1",
                "capacity": 10,
                "count": 10,
                "time": "12:12",
                "online": "True"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token
        )

        response = self.client.post(
            '/api/v1/seminar/1/user/',
            json.dumps({
                "role": "participant",
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token
        )

    def test_post_seminar_incomplete_request(self):
        # name이 빠진 경우
        response = self.client.post(
            '/api/v1/seminar/',
            json.dumps({
                "capacity": 10,
                "count": 10,
                "time": "12:12",
                "online": "True"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        seminar_count = Seminar.objects.count()
        self.assertEqual(seminar_count, 1)

    def test_post_seminar_not_positive_integer(self):
        # capacity가 빠진 경우
        response = self.client.post(
            '/api/v1/seminar/',
            json.dumps({
                "name": "Android",
                "count": 10,
                "time": "12:12",
                "online": "True"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # capacity가 음수인 경우
        response = self.client.post(
            '/api/v1/seminar/',
            json.dumps({
                "name": "Android",
                "capacity": -10,
                "count": 10,
                "time": "12:12",
                "online": "True"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # count가 빠진 경우
        response = self.client.post(
            '/api/v1/seminar/',
            json.dumps({
                "name": "Android",
                "capacity": 10,
                "time": "12:12",
                "online": "True"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # count가 음수인 경우
        response = self.client.post(
            '/api/v1/seminar/',
            json.dumps({
                "name": "Android",
                "capacity": 10,
                "count": -10,
                "time": "12:12",
                "online": "True"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        seminar_count = Seminar.objects.count()
        self.assertEqual(seminar_count, 1)

    def test_post_seminar_not_exist(self):
        response = self.client.post(
            '/api/v1/seminar/100/user/',
            json.dumps({
                "name": "Android",
                "capacity": 10,
                "count": 10,
                "time": "12:12",
                "online": "True"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        seminar_count = Seminar.objects.count()
        self.assertEqual(seminar_count, 1)

    def test_post_seminar_normal(self):
        # join
        response = self.client.post(
            '/api/v1/seminar/1/user/',
            json.dumps({
                "role": "participant",
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token
        )

        # create
        response = self.client.post(
            '/api/v1/seminar/',
            json.dumps({
                "name": "Android",
                "capacity": 10,
                "count": 10,
                "time": "12:12",
                "online": "True"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token
        )

class PutSeminarTestCase(TestCase):
    client = Client()

    def setUp(self):
        self.client.post(
            '/api/v1/user/',
            json.dumps({
                "username": "part",
                "password": "password",
                "first_name": "Davin",
                "last_name": "Byeon",
                "email": "bdv111@snu.ac.kr",
                "role": "participant",
                "university": "서울대학교"
            }),
            content_type='application/json'
        )
        self.participant_token = 'Token ' + Token.objects.get(user__username='part').key

        self.client.post(
            '/api/v1/user/',
            json.dumps({
                "username": "inst",
                "password": "password",
                "first_name": "Davin",
                "last_name": "Byeon",
                "email": "bdv111@snu.ac.kr",
                "role": "instructor",
                "university": "서울대학교"
            }),
            content_type='application/json'
        )
        self.instructor_token = 'Token ' + Token.objects.get(user__username='inst').key

        self.client.post(
            '/api/v1/seminar/',
            json.dumps({
                "name": "Backend2",
                "capacity": 10,
                "count": 10,
                "time": "12:12",
                "online": "True"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token
        )

        response = self.client.post(
            '/api/v1/seminar/1/user/',
            json.dumps({
                "role": "participant",
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token
        )

    def test_put_seminar_not_exist(self):
        response = self.client.put(
            '/api/v1/seminar/100/',
            json.dumps({
                "name": "Android",
                "capacity": 10,
                "count": 10,
                "time": "12:12",
                "online": "True"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        seminar_count = Seminar.objects.count()
        self.assertEqual(seminar_count, 1)

    def test_put_seminar_normal(self):
        # update
        response = self.client.put(
            '/api/v1/seminar/2/',
            json.dumps({
                "name": "Android",
                "capacity": 10,
                "count": 10,
                "time": "12:12",
                "online": "True"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token
        )

class GetSeminarTestCase(TestCase):
    client = Client()

    def setUp(self):
        self.client.post(
            '/api/v1/user/',
            json.dumps({
                "username": "part",
                "password": "password",
                "first_name": "Davin",
                "last_name": "Byeon",
                "email": "bdv111@snu.ac.kr",
                "role": "participant",
                "university": "서울대학교"
            }),
            content_type='application/json'
        )
        self.participant_token = 'Token ' + Token.objects.get(user__username='part').key

        self.client.post(
            '/api/v1/user/',
            json.dumps({
                "username": "inst",
                "password": "password",
                "first_name": "Davin",
                "last_name": "Byeon",
                "email": "bdv111@snu.ac.kr",
                "role": "instructor",
                "university": "서울대학교"
            }),
            content_type='application/json'
        )
        self.instructor_token = 'Token ' + Token.objects.get(user__username='inst').key

        response = self.client.post(
            '/api/v1/seminar/',
            json.dumps({
                "name": "Backend3",
                "capacity": 10,
                "count": 10,
                "time": "12:12",
                "online": "True"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token
        )

        response = self.client.post(
            '/api/v1/seminar/1/user/',
            json.dumps({
                "role": "participant",
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token
        )

    def test_get_seminar_not_exist(self):
        response = self.client.get(
            '/api/v1/seminar/100/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        seminar_count = Seminar.objects.count()
        self.assertEqual(seminar_count, 1)

    def test_get_seminar_no_participant(self):
        response = self.client.get(
            '/api/v1/seminar/1/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token
        )

        seminar_count = Seminar.objects.count()
        self.assertEqual(seminar_count, 1)

    def test_get_seminar_normal(self):
        # retrieve
        response = self.client.get(
            '/api/v1/seminar/1/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token
        )

        # list
        response = self.client.get(
            '/api/v1/seminar/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class DeleteSeminarTestCase(TestCase):
    client = Client()

    def setUp(self):
        self.client.post(
            '/api/v1/user/',
            json.dumps({
                "username": "part",
                "password": "password",
                "first_name": "Davin",
                "last_name": "Byeon",
                "email": "bdv111@snu.ac.kr",
                "role": "participant",
                "university": "서울대학교"
            }),
            content_type='application/json'
        )
        self.participant_token = 'Token ' + Token.objects.get(user__username='part').key

        self.client.post(
            '/api/v1/user/',
            json.dumps({
                "username": "inst",
                "password": "password",
                "first_name": "Davin",
                "last_name": "Byeon",
                "email": "bdv111@snu.ac.kr",
                "role": "instructor",
                "university": "서울대학교"
            }),
            content_type='application/json'
        )
        self.instructor_token = 'Token ' + Token.objects.get(user__username='inst').key

        response = self.client.post(
            '/api/v1/seminar/',
            json.dumps({
                "name": "Backend4",
                "capacity": 10,
                "count": 10,
                "time": "12:12",
                "online": "True"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token
        )

    def test_delete_seminar_not_exist(self):
        response = self.client.delete(
            '/api/v1/seminar/100/user/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        seminar_count = Seminar.objects.count()
        self.assertEqual(seminar_count, 1)

    def test_delete_seminar_normal(self):
        response = self.client.delete(
            '/api/v1/seminar/1/user/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token
        )
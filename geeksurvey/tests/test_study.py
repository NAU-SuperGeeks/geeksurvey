from django.test import TestCase

from datetime import datetime, timedelta

from geeksurvey.models import Study, User, Profile

class StudyCreateTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

        self.user_profile = Profile.objects.get(user=self.user)
        
        # set this to True so that user can enroll by default
        self.user_profile.updated_once = True
        self.user_profile.save()

        fruit_study_dict = {
          "title"           : "Fruit Study",
          "description"     : "studying fruit",
          "expiry_date"     : datetime.now() + timedelta(days=1),
          "balance"         : 0,
          "compensation"    : 0,
          "completion_code" : "bananaphone",
          "survey_url"      : "https:/example.com",
          "owner"           : self.user,
          }
        self.fruit_study = Study.objects.create(**fruit_study_dict)

    def test_can_enroll(self):
        self.assertTrue(self.user_profile.can_enroll(self.fruit_study))

    def test_can_enroll_update_profile(self):
        self.user_profile.updated_once = False
        self.assertFalse(self.user_profile.can_enroll(self.fruit_study))

    def test_can_enroll_expiry_date(self):
        self.fruit_study.expiry_date = datetime.now() - timedelta(days=1)
        self.assertFalse(self.user_profile.can_enroll(self.fruit_study))

    def test_can_enroll_min_age(self):
        self.fruit_study.min_age = 19
        self.assertEqual(self.user_profile.age, 18)
        self.assertFalse(self.user_profile.can_enroll(self.fruit_study))

    def test_can_enroll_max_age(self):
        self.fruit_study.max_age = 17
        self.assertEqual(self.user_profile.age, 18)
        self.assertFalse(self.user_profile.can_enroll(self.fruit_study))

    def test_can_enroll_min_yoe(self):
        self.fruit_study.min_yoe = 5
        self.assertEqual(self.user_profile.years_of_experience, 0)
        self.assertFalse(self.user_profile.can_enroll(self.fruit_study))

    def test_can_enroll_max_yoe(self):
        self.fruit_study.max_yoe = 5
        self.user_profile.years_of_experience = 10
        self.assertEqual(self.user_profile.years_of_experience, 10)
        self.assertFalse(self.user_profile.can_enroll(self.fruit_study))



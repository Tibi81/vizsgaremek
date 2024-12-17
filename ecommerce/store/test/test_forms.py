from django.test import TestCase
from django.contrib.auth.models import User
from store.forms import CustomUserCreationForm

class CustomUserCreationFormTest(TestCase):

    def setUp(self):
        """Alapértelmezett tesztadatok."""
        self.valid_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'password1': 'Teszt123!',
            'password2': 'Teszt123!',
        }

    def test_form_valid(self):
        """Ellenőrzi, hogy az űrlap helyes adatokkal validálható."""
        form = CustomUserCreationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())  # Az űrlap érvényes

    def test_form_invalid_password_too_short(self):
        """Ellenőrzi, hogy a túl rövid jelszó hibát ad."""
        invalid_data = self.valid_data.copy()
        invalid_data['password1'] = 'Teszt1!'  # Csak 7 karakter
        invalid_data['password2'] = 'Teszt1!'
        form = CustomUserCreationForm(data=invalid_data)
        self.assertFalse(form.is_valid())  # Az űrlap nem érvényes
        self.assertIn('password1', form.errors)
        self.assertEqual(form.errors['password1'][0], "A jelszónak legalább 8 karakter hosszúnak kell lennie.")

    def test_form_invalid_password_missing_number(self):
        """Ellenőrzi, hogy a szám nélküli jelszó hibát ad."""
        invalid_data = self.valid_data.copy()
        invalid_data['password1'] = 'Teszt!!!'
        invalid_data['password2'] = 'Teszt!!!'
        form = CustomUserCreationForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)
        self.assertEqual(form.errors['password1'][0], "A jelszónak tartalmaznia kell legalább egy számot.")

    def test_form_invalid_password_missing_special_char(self):
        """Ellenőrzi, hogy a speciális karakter nélküli jelszó hibát ad."""
        invalid_data = self.valid_data.copy()
        invalid_data['password1'] = 'Teszt123'
        invalid_data['password2'] = 'Teszt123'
        form = CustomUserCreationForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)
        self.assertEqual(form.errors['password1'][0], "A jelszónak tartalmaznia kell legalább egy speciális karaktert.")

    def test_form_invalid_email(self):
        """Ellenőrzi, hogy a rossz formátumú e-mail hibát ad."""
        invalid_data = self.valid_data.copy()
        invalid_data['email'] = 'notanemail'
        form = CustomUserCreationForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_save_user(self):
        """Ellenőrzi, hogy az űrlap helyesen menti a felhasználót."""
        form = CustomUserCreationForm(data=self.valid_data)
        if form.is_valid():
            user = form.save()
            self.assertEqual(User.objects.count(), 1)  # Egy felhasználó létrejött
            self.assertEqual(user.email, self.valid_data['email'])
            self.assertEqual(user.first_name, self.valid_data['first_name'])
            self.assertEqual(user.last_name, self.valid_data['last_name'])

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django import forms
from django.test import TestCase

from .fields import SecureCharFieldInput
from .fields import SecureMarDownField
from .widgets import WYSIWYGWidget


class ExampleForm(forms.Form):
    text = SecureCharFieldInput()


class ExampleMarkDownForm(forms.Form):
    text = SecureMarDownField()


class ExampleWYSIWYGForm(forms.Form):
    text = SecureCharFieldInput(widget=WYSIWYGWidget)


class SecureTextInputTests(TestCase):

    def setUp(self):
        self.form = ExampleForm

    @property
    def malicious_text(self):
        text = "<script>alert('I am taking over your browser')</script>"
        return text

    @property
    def almost_clean_text(self):
        text = "<p>This tag is valid.</p><aside>This one is not.</aside>"
        return text

    @property
    def clean_text(self):
        text = "<h1>This is a nice person</h1><h2>Using safe markup when you " \
               "posting in the internet is important</h2><p>When you play nice" \
               "you make the internet more safe for everyone and make" \
               "programmers lives easier"
        return text

    def test_malicious_text(self):
        """Form will validate but the malicious input will be sanitized.
        Script tags are not allowed.
        """
        data = {'text': self.malicious_text}
        form = self.form(data)
        self.failUnless(form.is_valid())
        cleaned_text = form.cleaned_data['text']
        escaped_text = u"&lt;script&gt;alert('I am taking over your browser')" \
                       u"&lt;/script&gt;"
        self.assertEqual(cleaned_text, escaped_text)

    def test_almost_clean_text(self):
        data = {'text': self.almost_clean_text}
        form = self.form(data)
        self.failUnless(form.is_valid())
        cleaned_text = form.cleaned_data['text']
        escaped_text = u"<p>This tag is valid.</p>&lt;aside&gt;" \
                       u"This one is not.&lt;/aside&gt;"
        self.assertEqual(cleaned_text, escaped_text)

    def test_clean_text(self):
        text = self.clean_text
        data = {'text': text}
        form = self.form(data)
        self.failUnless(form.is_valid())
        cleaned_text = form.cleaned_data['text']
        escaped_text = text + '</p>'  # Bleach closes unclosed tags.
        self.assertEqual(cleaned_text, escaped_text)


class SecureMarDownFieldTest(TestCase):

    def setUp(self):
        self.form = ExampleMarkDownForm

    @property
    def safe_text(self):
        return "This text can be easily be\n\n marked down."

    @property
    def malicious_text(self):
        return "<script>alert('hey there')</script>"

    def test_safe_markdown(self):
        text = self.safe_text
        data = {'text': text}
        form = self.form(data)
        self.failUnless(form.is_valid())
        cleaned_text = form.cleaned_data['text']
        # Input text should be made into html and safe tags should not be
        # escaped.
        escaped_text = '<p>This text can be easily be</p>\n<p>marked down.</p>'
        self.assertEqual(cleaned_text, escaped_text)

    def test_malicious_text(self):
        """Markdown should allowed for any html to be entered into the value
        of the field. However, cleaning after we markdown should escape
        unsafe tags."""
        text = self.malicious_text
        data = {'text': text}
        form = self.form(data)
        self.failUnless(form.is_valid())
        cleaned_text = form.cleaned_data['text']
        # Script tags get escaped.
        escaped_text = "&lt;script&gt;alert('hey there')&lt;/script&gt;"
        self.assertEqual(cleaned_text, escaped_text)


class WYSIWYGWidgetTest(TestCase):

    def setUp(self):
        self.form = ExampleWYSIWYGForm()

    def test_render(self):
        rendered_form = self.form.as_p()
        expected = u'<p><label for="id_text">Text:</label> ' \
                   u'<textarea class="hidden secure-input" ' \
                   u'cols="40" data-editor="text-secure-input" ' \
                   u'id="id_text" name="text" rows="10">\r\n' \
                   u'</textarea><div class="bootstrap-wysiwyg" ' \
                   u'id="text-secure-input" /></div></p>'
        self.assertEqual(rendered_form, expected)

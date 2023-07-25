from django.contrib.auth.forms import UserCreationForm
from django import forms

from bug_tracker.models import User, TestCase, TestRun, TestResult


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class TestCaseForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(TestCaseForm, self).__init__(*args, **kwargs)
        self.fields['project'].queryset = user.user.all() | user.users.all()

    class Meta:
        model = TestCase
        fields = ['title', 'description', 'steps', 'expected_result', 'priority', 'project']


class DateInput(forms.DateInput):
    input_type = 'date'


class TestRunForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(TestRunForm, self).__init__(*args, **kwargs)
        self.fields['project'].queryset = user.user.all() | user.users.all()

    deadline = forms.DateField(
        widget=DateInput(),
    )

    class Meta:
        model = TestRun
        fields = ['title', 'description', 'deadline', 'project']


class TestResultForm(forms.ModelForm):
    class Meta:
        model = TestResult
        fields = ('status', 'actual_result')
        labels = {
            'status': 'Status',
            'actual_result': 'Actual Result',
        }


class ShareProjectForm(forms.Form):
    users = forms.ModelMultipleChoiceField(queryset=None, widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project')
        super().__init__(*args, **kwargs)

        # Exclude the user who created the project from the queryset
        self.fields['users'].queryset = User.objects.exclude(id=project.created_by.id)

from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    pass


class TelegramUser(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="telegram"
    )
    chat_id = models.IntegerField(null=True, blank=True)
    token = models.CharField(max_length=255, unique=True)


class Project(models.Model):
    title = models.CharField(max_length=255, null=False)
    description = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name="user"
    )
    shared_with = models.ManyToManyField(
        User, related_name="users", blank=True
    )

    def __str__(self):
        return self.title


class TestCase(models.Model):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    PRIORITIES = ((HIGH, "High"), (MEDIUM, "Medium"), (LOW, "Low"))
    title = models.CharField(max_length=255, null=False)
    description = models.TextField(null=True, blank=True)
    steps = models.TextField(null=True, blank=True)
    expected_result = models.TextField(null=True, blank=True)
    priority = models.CharField(
        max_length=8, choices=PRIORITIES, default=MEDIUM, null=False
    )
    project = models.ForeignKey(to=Project, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class TestRun(models.Model):
    title = models.CharField(max_length=255, null=False)
    description = models.TextField(null=True, blank=True)
    deadline = models.DateTimeField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    test_cases = models.ManyToManyField(
        TestCase,
        through="TestResult",
        related_name="test_runs",
    )

    def __str__(self):
        return self.title


class TestResult(models.Model):
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"
    UNTESTED = "untested"
    STATUS_CHOICES = [
        (PASSED, "Passed"),
        (FAILED, "Failed"),
        (BLOCKED, "Blocked"),
        (UNTESTED, "Untested"),
    ]
    test_run = models.ForeignKey(
        TestRun, on_delete=models.CASCADE, related_name="test_results"
    )
    test_case = models.ForeignKey(
        TestCase, on_delete=models.CASCADE, related_name="test_results"
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=UNTESTED
    )
    actual_result = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return f"Result for {self.test_case.title} test case"

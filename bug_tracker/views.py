from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count, F, IntegerField, Value, Case, When
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import (
    CreateView,
    ListView,
    DetailView,
    UpdateView,
    DeleteView,
)
from telebot import TeleBot
from .forms import RegisterForm, TestCaseForm, TestRunForm
from .forms import ShareProjectForm
from .models import TestRun, TestCase, Project, TestResult, TelegramUser
from .utils import generate_unique_token


class ConnectTelegramView(View):
    def get(self, request):
        user = request.user

        try:
            telegram_user = TelegramUser.objects.get(user=user)
            token = telegram_user.token
            chat_id = telegram_user.chat_id
        except TelegramUser.DoesNotExist:
            token = None
            chat_id = None

        context = {
            "token": token,
            "chat_id": chat_id,
        }

        return render(request, "bug_tracker/connect_telegram.html", context)

    def post(self, request):
        user = request.user

        # Check if a TelegramUser record already exists for the user
        try:
            telegram_user = TelegramUser.objects.get(user=user)
            telegram_user.token = generate_unique_token()  # Update the token
            telegram_user.chat_id = None
            telegram_user.save()
        except TelegramUser.DoesNotExist:
            # Generate a unique token and create a new TelegramUser record
            token = generate_unique_token()
            telegram_user = TelegramUser.objects.create(user=user, token=token)

        return redirect("connect_telegram")


class IndexView(View):
    def get(self, request):
        if request.user.is_authenticated:
            # User is authenticated, redirect to project page
            return redirect("project_list")
        else:
            # User is not authenticated, redirect to login page
            return redirect(reverse("login"))


class RegisterView(CreateView):
    form_class = RegisterForm
    success_url = reverse_lazy("login")
    template_name = "registration/register.html"


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "bug_tracker/project_list.html"
    context_object_name = "projects"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["created_projects"] = self.request.user.user.all()
        return context


class SharedProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "bug_tracker/shared_project_list.html"
    context_object_name = "projects"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["shared_projects"] = self.request.user.users.all()
        return context


class ProjectDetailView(View):
    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        testcases = (
            project.testcase_set.all()
        )  # Retrieve all related test cases for the project
        testruns = (
            project.testrun_set.all()
        )  # Retrieve all related test runs for the project

        testrun_data = []
        for testrun in testruns:
            passed_count = testrun.test_results.filter(
                status="passed").count()
            failed_count = testrun.test_results.filter(
                status="failed").count()
            blocked_count = testrun.test_results.filter(
                status="blocked").count()
            untested_count = testrun.test_results.filter(
                status="untested").count()
            total_count = testrun.test_results.count()

            passed_percent = (
                (passed_count / total_count) * 100 if total_count > 0 else 0
            )
            failed_percent = (
                (failed_count / total_count) * 100 if total_count > 0 else 0
            )
            blocked_percent = (
                (blocked_count / total_count) * 100 if total_count > 0 else 0
            )
            untested_percent = (
                (untested_count / total_count) * 100 if total_count > 0 else 0
            )

            testrun_data.append(
                {
                    "testrun": testrun,
                    "passed_count": passed_count,
                    "failed_count": failed_count,
                    "blocked_count": blocked_count,
                    "untested_count": untested_count,
                    "total_count": total_count,
                    "passed_percent": passed_percent,
                    "failed_percent": failed_percent,
                    "blocked_percent": blocked_percent,
                    "untested_percent": untested_percent,
                }
            )

        return render(
            request,
            "bug_tracker/project_detail.html",
            {
                "project": project,
                "testcases": testcases,
                "testrun_data": testrun_data
            },
        )


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    fields = ["title", "description"]
    template_name = "bug_tracker/project_form.html"
    success_url = reverse_lazy("project_list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    fields = ["title", "description"]
    template_name = "bug_tracker/project_form.html"
    success_url = reverse_lazy("project_list")

    def get_queryset(self):
        return super().get_queryset().filter(created_by=self.request.user)


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = "bug_tracker/project_confirm_delete.html"
    success_url = reverse_lazy("project_list")

    def get_queryset(self):
        return super().get_queryset().filter(created_by=self.request.user)


@login_required
def share_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == "POST":
        form = ShareProjectForm(request.POST, project=project)
        if form.is_valid():
            users = form.cleaned_data["users"]
            project.shared_with.set(users)
            return redirect("project_detail", pk=project.id)
    else:
        form = ShareProjectForm(project=project)

    context = {"project": project, "form": form}
    return render(request, "bug_tracker/share_project.html", context)


class TestRunListView(LoginRequiredMixin, ListView):
    model = TestRun
    template_name = "bug_tracker/testrun_list.html"
    context_object_name = "testruns"

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        # Show test runs of projects created by the logged-in user
        queryset = queryset.filter(project__created_by=user)

        # Show test runs of projects shared with the logged-in user
        queryset |= self.model.objects.filter(project__shared_with=user)

        # Annotate the queryset as before
        queryset = queryset.annotate(
            passed_count=Count(
                "test_results", filter=Q(
                    test_results__status=TestResult.PASSED)
            ),
            failed_count=Count(
                "test_results", filter=Q(
                    test_results__status=TestResult.FAILED)
            ),
            blocked_count=Count(
                "test_results", filter=Q(
                    test_results__status=TestResult.BLOCKED)
            ),
            skipped_count=Count(
                "test_results", filter=Q(
                    test_results__status=TestResult.UNTESTED)
            ),
            total_count=Count("test_results"),
            passed_percent=Case(
                When(total_count=0, then=Value(0)),
                default=100 * F("passed_count") / F("total_count"),
                output_field=IntegerField(),
            ),
            failed_percent=Case(
                When(total_count=0, then=Value(0)),
                default=100 * F("failed_count") / F("total_count"),
                output_field=IntegerField(),
            ),
            blocked_percent=Case(
                When(total_count=0, then=Value(0)),
                default=100 * F("blocked_count") / F("total_count"),
                output_field=IntegerField(),
            ),
            skipped_percent=Case(
                When(total_count=0, then=Value(0)),
                default=100 * F("skipped_count") / F("total_count"),
                output_field=IntegerField(),
            ),
        )

        return queryset


class TestRunDetailView(LoginRequiredMixin, View):
    template_name = "bug_tracker/testrun_detail.html"

    def get(self, request, pk):
        test_run = TestRun.objects.filter(pk=pk).first()
        if not test_run:
            # Test run not found, generate template with a message
            context = {
                "message": "Test run not found.",
            }
            return render(request, self.template_name, context)
        test_results = test_run.test_results.all()

        passed_count = test_results.filter(status="passed").count()
        failed_count = test_results.filter(status="failed").count()
        blocked_count = test_results.filter(status="blocked").count()
        untested_count = test_results.filter(status="untested").count()

        status = request.GET.get("status")
        if status:
            test_results = test_results.filter(status=status)
        priority = request.GET.get("priority")

        if priority:
            test_results = test_results.filter(test_case__priority=priority)

        context = {
            "test_run": test_run,
            "test_results": test_results,
            "passed_count": passed_count,
            "failed_count": failed_count,
            "blocked_count": blocked_count,
            "untested_count": untested_count,
        }
        return render(request, self.template_name, context)


class TestRunCreateView(LoginRequiredMixin, CreateView):
    model = TestRun
    form_class = TestRunForm
    template_name = "bug_tracker/testrun_form.html"
    success_url = reverse_lazy("testrun_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class TestRunUpdateView(LoginRequiredMixin, UpdateView):
    model = TestRun
    form_class = TestRunForm
    template_name = "bug_tracker/testrun_form.html"
    success_url = reverse_lazy("testrun_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class AddTestCaseView(LoginRequiredMixin, View):
    def get(self, request, pk):
        test_run = get_object_or_404(TestRun, pk=pk)
        test_cases = TestCase.objects.filter(project=test_run.project).exclude(
            test_results__test_run=test_run
        )
        return render(
            request,
            "bug_tracker/add_test_case.html",
            {"test_run": test_run, "test_cases": test_cases},
        )

    def post(self, request, pk):
        test_run = get_object_or_404(TestRun, pk=pk)
        test_case_ids = request.POST.getlist("test_case_ids")
        for test_case_id in test_case_ids:
            test_case = get_object_or_404(TestCase, pk=test_case_id)
            TestResult.objects.create(test_run=test_run, test_case=test_case)
        return redirect("testrun_detail", pk=pk)


class TestRunDeleteView(LoginRequiredMixin, DeleteView):
    model = TestRun
    template_name = "bug_tracker/testrun_confirm_delete.html"
    success_url = reverse_lazy("testrun_list")


class TestCaseListView(LoginRequiredMixin, ListView):
    template_name = "bug_tracker/testcase_list.html"
    context_object_name = "testcases"

    def get_queryset(self):
        user = self.request.user
        return TestCase.objects.filter(
            Q(project__created_by=user) | Q(project__shared_with=user)
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["projects_created"] = Project.objects.filter(created_by=user)
        context["projects_shared"] = Project.objects.filter(
            shared_with=user
        ).exclude(created_by=user)
        return context


class TestCaseDetailView(LoginRequiredMixin, DetailView):
    model = TestCase
    template_name = "bug_tracker/testcase_detail.html"
    context_object_name = "testcase"


class TestCaseCreateView(LoginRequiredMixin, CreateView):
    model = TestCase
    form_class = TestCaseForm
    template_name = "bug_tracker/testcase_form.html"
    success_url = reverse_lazy("testcase_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class TestCaseUpdateView(LoginRequiredMixin, UpdateView):
    model = TestCase
    form_class = TestCaseForm
    template_name = "bug_tracker/testcase_form.html"
    success_url = reverse_lazy("testcase_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class TestCaseDeleteView(LoginRequiredMixin, DeleteView):
    model = TestCase
    template_name = "bug_tracker/testcase_confirm_delete.html"
    success_url = reverse_lazy("testcase_list")


class TestResultUpdateView(UpdateView):
    model = TestResult
    fields = ["status", "actual_result"]
    template_name = "bug_tracker/testresult_update.html"

    def get_success_url(self):
        test_run_id = self.object.test_run.id
        return reverse("testrun_detail", args=[test_run_id])

    def form_valid(self, form):
        instance = form.save(commit=False)
        if instance.status != TestResult.PASSED:
            # Retrieve the chat ID from TelegramUser
            try:
                telegram_user = TelegramUser.objects.get(
                    user=self.request.user
                )
                chat_id = telegram_user.chat_id

                test_case = instance.test_case
                project = test_case.project

                test_case_details = f"Test case: {test_case.title}\n\n"
                test_case_details += f"Description: {test_case.description}\n"
                test_case_details += f"Steps:\n {test_case.steps}\n"
                test_case_details += (f"Expected Result: "
                                      f"{test_case.expected_result}\n\n")
                test_case_details += f"Project: {project.title}\n"
                test_case_details += f"Description: {project.description}\n"

                message = (f"Test case: {test_case.title}\n"
                           f"\nTest status: {instance.status}"
                           f"\nActual Result: {instance.actual_result}\n "
                           f"\n{test_case_details}")
                try:
                    bot = TeleBot(settings.TELEGRAM_BOT_API_KEY)
                    bot.send_message(chat_id, message)
                except Exception:
                    pass
            except TelegramUser.DoesNotExist:
                # Handle the case when no TelegramUser
                # record exists for the user
                pass
        instance.timestamp = timezone.now()
        instance.save()
        return super().form_valid(form)


class TestResultDetailView(DetailView):
    model = TestResult
    template_name = "bug_tracker/testresult_detail.html"

    def get_object(self, queryset=None):
        obj = get_object_or_404(TestResult, id=self.kwargs["result_id"])
        return obj


class TestResultListView(ListView):
    model = TestResult
    template_name = "bug_tracker/testresult_list.html"
    context_object_name = "testresults"

    def get_queryset(self):
        queryset = super().get_queryset()

        user = self.request.user

        # Filter results by projects created by
        # the user or shared with the user
        queryset = queryset.filter(
            Q(test_run__project__created_by=user)
            | Q(test_run__project__shared_with=user)
        )

        status = self.request.GET.get(
            "status"
        )  # Get the status filter value from the request
        project_id = self.request.GET.get(
            "project"
        )  # Get the project filter value from the request
        testrun_id = self.request.GET.get(
            "testrun"
        )  # Get the project filter value from the request

        # Filter results by status
        if status:
            queryset = queryset.filter(status=status)

        # Filter results by project
        if project_id:
            queryset = queryset.filter(test_run__project_id=project_id)

        if testrun_id:
            queryset = queryset.filter(test_run__id=testrun_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user

        # Get the available projects for the user
        projects = Project.objects.filter(
            Q(created_by=user) | Q(shared_with=user)
        )

        testruns = TestRun.objects.filter(project__in=projects)

        context["projects"] = projects
        context["testruns"] = testruns
        return context


def handler404(request, exception):
    return render(request, "404.html", status=404)

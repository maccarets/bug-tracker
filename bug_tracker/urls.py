
from django.urls import path
from django.contrib.auth import views as auth_views
from bug_tracker.views import (RegisterView, TestRunListView, TestCaseDetailView,
    TestCaseListView, TestCaseCreateView, TestCaseUpdateView, TestCaseDeleteView, ProjectListView, ProjectCreateView,
    ProjectDetailView, ProjectUpdateView, ProjectDeleteView, AddTestCaseView, TestRunCreateView, TestRunUpdateView,
    TestRunDeleteView, TestRunDetailView, TestResultUpdateView, TestResultDetailView, ConnectTelegramView,
    share_project, TestResultListView, IndexView)

urlpatterns = [
    path('connect-telegram/', ConnectTelegramView.as_view(), name='connect_telegram'),

    path('', IndexView.as_view(), name="index"),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    # Project URLs
    path('project/', ProjectListView.as_view(), name='project_list'),
    path('project/create/', ProjectCreateView.as_view(), name='project_create'),
    path('project/<int:pk>/', ProjectDetailView.as_view(), name='project_detail'),
    path('project/<int:pk>/update/', ProjectUpdateView.as_view(), name='project_update'),
    path('project/<int:pk>/delete/', ProjectDeleteView.as_view(), name='project_delete'),
    path('project/<int:project_id>/share/', share_project, name='share_project'),

    # Test Run URLs
    path('testrun/', TestRunListView.as_view(), name='testrun_list'),
    path('testrun/create/', TestRunCreateView.as_view(), name='testrun_create'),
    path('testrun/<int:pk>/', TestRunDetailView.as_view(), name='testrun_detail'),
    path('testrun/<int:pk>/update/', TestRunUpdateView.as_view(), name='testrun_update'),
    path('testrun/<int:pk>/delete/', TestRunDeleteView.as_view(), name='testrun_delete'),
    path('testrun/<int:pk>/add_test_case/', AddTestCaseView.as_view(), name='add_test_case'),

    # Test Case URLs
    path('testcase/', TestCaseListView.as_view(), name='testcase_list'),
    path('testcase/create/', TestCaseCreateView.as_view(), name='testcase_create'),
    path('testcase/<int:pk>/', TestCaseDetailView.as_view(), name='testcase_detail'),
    path('testcase/<int:pk>/update/', TestCaseUpdateView.as_view(), name='testcase_update'),
    path('testcase/<int:pk>/delete/', TestCaseDeleteView.as_view(), name='testcase_delete'),

    # Test Case URLs
    path('test-result/', TestResultListView.as_view(), name='testresult_list'),
    path('testresult/<int:pk>/update/', TestResultUpdateView.as_view(), name='testresult_update'),
    path('testresult/<int:result_id>/', TestResultDetailView.as_view(), name='testresult_detail'),

]

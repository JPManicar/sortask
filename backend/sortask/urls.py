from django.urls import path, include
from rest_framework_nested import routers
from sortask.views import *

router = routers.SimpleRouter()

router.register('projects', ProjectViewSet)
router.register('tasks', TaskViewSet)

# Projects
projects_router = routers.NestedSimpleRouter(
    router, r'projects', lookup='project')
projects_router.register(r'boards', BoardViewSet, basename='project-boards')
projects_router.register(r'members', MemberViewSet, basename='project-members')

# Tasks
tasks_router = routers.NestedSimpleRouter(router, r'tasks', lookup='task')
tasks_router.register(r'comments', CommentViewSet, basename='task-comments')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(projects_router.urls)),
    path('', include(tasks_router.urls)),

    # Assign user a task
    path('tasks/<int:pk>/assign/',
         TaskViewSet.as_view({'post': 'assign_user'}), name='task-assign'),

    # Get Project Invite Link
    path('projects/<int:project_id>/invite/',
         ProjectInvitationViewSet.as_view({'get': 'get_invite_link'}), name='project_invite'),

    # Accept Project Invite Link
    path('accept-invite/<str:token>/',
         ProjectInvitationViewSet.as_view({'get': 'accept_invite'}), name='accept_invite'),

    # Notifications
    path('notifications/', NotificationAPIView.as_view()),
    path('notifications/<int:id>/', NotificationAPIView.as_view()),

]

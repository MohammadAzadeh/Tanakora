from django.urls import path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views



app_name = 'accounts'
urlpatterns = [
    path('register/', views.UserRegister.as_view(), name='user_register'),
    path('register/confirm/', views.UserRegisterConfirm.as_view(), name='user_register_confirm'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/<int:user_id>/', views.UserProfile.as_view(), name='profile'),
    path('profile/edit/<int:user_id>/', views.UserProfileEdit.as_view(), name='profile_edit'),
    path('profile/edit/confirm/<int:user_id>/', views.UserProfileEditConfirm.as_view(), name='profile_edit_confirm'),
    path('panel/<int:user_id>/', views.UserPanel.as_view(), name='panel'),
    path('withdraw/<int:user_id>/', views.UserWithdraw.as_view(), name='withdraw'),
    path('withdraw/confirm/', views.UserWithdrawConfirm.as_view(), name='withdraw_confirm'),
    path('transaction/cancel/<int:transaction_id>/', views.UserWithdrawCancel.as_view(), name='withdraw_delete'),
    path('logo/edit/<int:user_id>/', views.UserLogoEdit.as_view(), name='logo_edit'),
    path('logo/edit/confirm/<int:user_id>/', views.UserLogoEditConfirm.as_view(), name='logo_edit_confirm'),
    path('product/add/', views.UserProductAdd.as_view(), name='product_add'),
    path('product/edit/<int:product_id>/', views.UserProductEdit.as_view(), name='product_edit'),
    path('product/edit/confirm/<int:product_id>/', views.UserProductEditConfirm.as_view(), name='product_edit_confirm'),
    path('product/delete/<int:product_id>/', views.UserProductDelete.as_view(), name='product_delete'),
]

#router = routers.SimpleRouter()
#router.register('user', views.UserViewSet)
#urlpatterns += router.urls
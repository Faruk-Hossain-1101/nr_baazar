from django.contrib.auth import get_user_model
import pytest 

CustomUser = get_user_model()

@pytest.mark.django_db
def test_create_user():
    """Test creating a regular user"""
    user = CustomUser.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='securepassword123',
        role='staff'
    )
    assert user.email == 'testuser@example.com'
    assert user.username == 'testuser'
    assert not user.is_staff 
    assert not user.is_superuser  
    assert user.check_password('securepassword123')
    
@pytest.mark.django_db
def test_user_str():
    """Test the __str__ method of CustomUser"""
    user = CustomUser.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="securepassword123"
    )

    assert str(user) == "testuser"

@pytest.mark.django_db
def test_create_super_user():
    """Test creating a super user"""
    admin = CustomUser.objects.create_superuser(
        username='admin',
        email='admin.super@example.com',
        password='adminsuper123',
    )

    print(admin.role)
    assert admin.email == 'admin.super@example.com'
    assert admin.username == 'admin'
    assert admin.is_staff 
    assert admin.is_superuser  
    assert admin.role == 'admin'
    assert admin.check_password('adminsuper123')

@pytest.mark.django_db
def test_create_user_without_email():
    """Test that creating a user without an email raises an error"""
    with pytest.raises(ValueError, match="The Email field must be set"):
        CustomUser.objects.create_user(username="noemail", email="", password="password123")

@pytest.mark.django_db
def test_create_superuser_without_is_staff():
    """Test that superuser must have is_staff=True"""
    with pytest.raises(ValueError, match="Superuser must have is_staff=True."):
        CustomUser.objects.create_superuser(username="fakeadmin", email="fake@admin.com", password="password123", is_staff=False)

@pytest.mark.django_db
def test_create_superuser_without_is_superuser():
    """Test that superuser must have is_superuser=True"""
    with pytest.raises(ValueError, match="Superuser must have is_superuser=True."):
        CustomUser.objects.create_superuser(username="fakeadmin", email="fake@admin.com", password="password123", is_superuser=False)
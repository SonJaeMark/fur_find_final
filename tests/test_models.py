import pytest
from models.user import PetOwner, Admin, SuperAdmin

def test_pet_owner_creation_and_hashing():
    # Happy Path: Create user & set password
    user = PetOwner(user_id=1, full_name="John Doe", email="john@example.com", contact_no="09171234567")
    user.set_password("SecurePass123!")
    
    assert user.get_role_name() == "Pet Owner"
    assert user.verify_password("SecurePass123!") is True
    assert user.verify_password("WrongPassword") is False  # Failure path test

def test_invalid_name_setter():
    # Failure Path: Invalid empty name
    user = PetOwner(user_id=1, full_name="John Doe", email="john@example.com", contact_no="09171234567")
    with pytest.raises(ValueError):
        user.full_name = "   "
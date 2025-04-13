
class ValidationErrors:
    
    LOW_AMOUNT = "Amount has to be not less then 0.01"
    NO_CATEGORY = "Please choose category"
    USERNAME_LENGTH = "Allowed username length should be from 3 to 50 characters"
    PASSWORD_LENGTH = "Allowed password length should be from 3 to 12 characters"
    DIFFERENT_PASSWORDS = "Passwords should be equal"
    LOGIN_BAD_CREDENTIALS = "Bad credentials"
    PROFILE_NAME_LENGTH = "Fullname length has to be not longer that 50 symbols"
    CATEGORY_DUPLICATE = "Error while adding category {category_name}: Cannot save duplicates"
    CATEGORY_LENGTH = "Allowed category length is from 2 to 50 symbols"
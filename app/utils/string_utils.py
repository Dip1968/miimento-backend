import secrets
import string


def generate_random_string(length: int = 12) -> str:
    """
    Generate a cryptographically secure random string of specified length.
    # Example usage:
    ```python
        random_string = generate_random_string(20)  # Generates a 20-character long string
        print(random_string)
    ```
    """
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))

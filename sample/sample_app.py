def add(a, b):
    """Return sum of two numbers"""
    return a + b

class Auth:
    def __init__(self, token_store):
        self.tokens = token_store

    def is_authenticated(self, token):
        return token in self.tokens

# Example usage
if __name__ == "__main__":
    print(add(2, 3))

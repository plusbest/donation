
import os

# The context processor function
def api_key(request):
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

    return {
        'GOOGLE_API_KEY': GOOGLE_API_KEY,
    }
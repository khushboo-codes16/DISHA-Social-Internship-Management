import os
from app import create_app

# Create app instance
app = create_app()

# This allows Render and other platforms to find the app
if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
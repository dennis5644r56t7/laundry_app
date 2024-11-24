from waitress import serve
from app import create_app
import logging

# Configure logging
logging.basicConfig(
    filename='server.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create the application
app = create_app()

if __name__ == '__main__':
    # Serve the application
    serve(app, host='0.0.0.0', port=8080, threads=4)
    logging.info('Server started on http://0.0.0.0:8080')

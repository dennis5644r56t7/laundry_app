from pyngrok import ngrok
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def start_tunnel():
    try:
        # Open a HTTP tunnel on the default port (8080)
        public_url = ngrok.connect(8080)
        logging.info(f'Public URL: {public_url}')
        
        # Keep the script running
        ngrok_process = ngrok.get_ngrok_process()
        try:
            # Block until CTRL-C
            ngrok_process.proc.wait()
        except KeyboardInterrupt:
            logging.info('Shutting down tunnel...')
            ngrok.kill()
    except Exception as e:
        logging.error(f'Error: {str(e)}')
        ngrok.kill()

if __name__ == '__main__':
    start_tunnel()

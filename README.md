# Kwamboka Laundry Web Application

A modern web application for a laundry service business, built with Flask and modern frontend technologies.

## Features

- Modern, responsive design
- Service booking system
- Price calculator
- Contact form
- Admin dashboard
- M-Pesa integration
- Beautiful animations and UI effects

## Tech Stack

- Backend: Flask (Python)
- Database: PostgreSQL
- Frontend: HTML5, CSS3, JavaScript
- CSS Animations: AOS (Animate On Scroll)
- Icons: Font Awesome
- Payment: M-Pesa Integration

## Production Deployment

### Prerequisites

1. Create accounts on:
   - [Render.com](https://render.com) for hosting
   - [PostgreSQL database](https://render.com/docs/databases) (Can be created on Render)

### Environment Variables

Set the following environment variables in your production environment:

```
FLASK_ENV=production
SECRET_KEY=your-secret-key
DATABASE_URL=your-postgresql-url
MAIL_USERNAME=your-email
MAIL_PASSWORD=your-email-password
MPESA_CONSUMER_KEY=your-mpesa-key
MPESA_CONSUMER_SECRET=your-mpesa-secret
MPESA_SHORTCODE=your-mpesa-shortcode
MPESA_PASSKEY=your-mpesa-passkey
```

### Deployment Steps

1. Push your code to GitHub

2. On Render.com:
   - Create a new Web Service
   - Connect your GitHub repository
   - Select the Python environment
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `gunicorn -c gunicorn.conf.py "app:create_app()"`
   - Add environment variables

3. Database Setup:
   - Create a PostgreSQL database on Render
   - Add the database URL to your environment variables
   - Run migrations: `flask db upgrade`

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd laundry_app
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables in `.env` file

5. Initialize the database:
```bash
flask db upgrade
```

6. Run the development server:
```bash
flask run
```

## Contact

For support or inquiries:
- Email: kariukidennis782@gmail.com
- Phone: 0792508277 / 0113534007
- Location: Kisii, Kenya

## License

This project is licensed under the MIT License - see the LICENSE file for details.

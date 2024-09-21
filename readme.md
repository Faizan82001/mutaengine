
# Project Title
MutaEngine Test Assignment

## Getting Started

Follow these steps to set up the project on your local machine for development and testing purposes.

### 1. Clone the Project

First, clone the repository to your local machine:

```bash
git clone https://github.com/Faizan82001/mutaengine.git
cd mutaengine
```

### 2. Create and Activate Virtual Environment (Optional but Recommended)

It's recommended to use a virtual environment to isolate dependencies:

```bash
# On Linux/MacOS
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

After setting up the environment, install the required dependencies:

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create an `.env` file in the root directory of your project and add the environment variables mentioned in `.env-template` file.

### 5. Run Migrations

Apply database migrations:

```bash
python manage.py migrate
```

### 6. Create a Superuser (Admin Account)

Create an admin account:

```bash
python manage.py createsuperuser
```

### 7. Run the Development Server

Run the Django development server:

```bash
python manage.py runserver
```

Now the project should be running at `http://127.0.0.1:8000/`.

---

## Additional Information

1. **Google Sign-In/Register**:
   - This app uses Google OAuth2 for user authentication. To set up Google OAuth2:
   - Please [Google Cloud Platform](https://console.cloud.google.com). Once configured, add the following secrets to your `.env` file:
     ```
     GOOGLE_CLIENT_ID=your_google_client_id
     GOOGLE_CLIENT_SECRET=your_google_client_secret
     ```
    - To check the Google sign-in feature go to [OAuth 2.0 Playground](https://developers.google.com/oauthplayground/) and enable Google OAuth 2.0 APIs.
    - Once enabled use your Google account to generate `access_token` and `id_token`. Use the `id_token` in a request for the `/auth/google` route.

2. **Google reCaptcha**:
   - To secure forms and prevent bots, this app integrates with Google reCaptcha. Follow [Google reCAPTCHA](https://developers.google.com/recaptcha/docs/v3) to set it up, and then add these keys to your `.env` file:
     ```
     RECAPTCHA_SECRET_KEY=your_recaptcha_secret_key
     ```
   - To simplify things and get a reCAPTCHA token a file `recaptcha.html` has been added to the scope of this project. Open the LIVE Server and Click the Submit button and you'll get reCAPTCHA. Use this for `/auth/register` and `/auth/login` APIs.

3. **Stripe for Payments**:
   - Payments are processed using Stripe. Refer to [Stripe's developer documentation](https://docs.stripe.com/development) to configure it for your app. Once done, update your `.env` file with the following:
     ```
     STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
     STRIPE_SECRET_KEY=your_stripe_secret_key
     ```

4. **Stripe Webhooks**:
   - Webhooks are used to update payment statuses. Check out [Stripe Webhook documentation]([stripe-webhook-link](https://docs.stripe.com/webhooks)) to configure Stripe webhooks. Add the webhook secret to your `.env` file:
     ```
     STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
     ```
   - Use [Stripe CLI](https://docs.stripe.com/stripe-cli) to check for webhook events.

5. **Email Service**:
   - The app sends transactional emails to users. To configure email delivery, enable two-factor authentication on your Google account. Once done, proceed to create the app password which will serve as our `EMAIL_HOST_PASSWORD`. Update your `.env` file with the necessary email credentials:
     ```
     EMAIL_HOST=smtp.your-email-provider.com
     EMAIL_PORT=your_email_port
     EMAIL_USE_TLS=True
     EMAIL_HOST_USER=your_email_username
     EMAIL_HOST_PASSWORD=your_email_password
     DEFAULT_FROM_EMAIL=your_default_sender_email
     ```
6. **Hosting on GCP**:
   - This app is hosted on **Google Cloud Platform (GCP)** using **App Engine**. To set up hosting on GCP, follow [GCP Hosting Guide](https://cloud.google.com/python/django/appengine#windows_2). Once configured, ensure you have the correct environment variables in your `.env` file for things like database credentials and API keys.
     ```
     DATABASE_URL=your_database_url
     ALLOWED_HOSTS=your_gcp_allowed_hosts
     ```
   - The app's configuration file for GCP, `app.yaml`, should contain the necessary details for deploying to App Engine. An example file `template_app.yaml` has been added to this project scope.

# GeekSurvey

**Version: 0.1.0**

GeekSurvey is a web platform for conducting software engineering research

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Must have a machine with python3 and pip package manager

### Installing

1. ```git clone <this repo>``` ```cd <this repo>```
2. ```pip install requirements.txt```
3. ```python manage.py makemigrations geeksurvey```
3. ```python manage.py migrate```

### Testing
```python manage.py test```

## Deployment

### Deploy locally

For a simple locally deployed version of GeekSurvey, do
1. ```python manage.py runserver```
2. Go to ```localhost:8000``` in the web browser.

Features that integrate with other web APIs typically do not work when geeksurvey is deployed locally. This includes OAuth by Github and Google, PayPal payments, and email services.

Typically, various credentials for these APIs are stored in a .env file at the root of the project. These can be left out for local testing


### Deploy to a server

To deploy GeekSurvey to a server, a .env file must be in the project root containing:
1. A valid Django secret key used for encryption
  - ```GEEKSURVEY_SECRET_KEY = "some_data"```
2. A debug flag set to false (0) for deployment
  - ```GEEKSURVEY_DEBUG = 0```
3. Valid Gmail App credentials for email
  - ```GMAIL_APP_USERNAME = "user@gmail.com"```
  - ```GMAIL_APP_PASSWORD = "sample-app-password"```
4. Valid Google App credentials for OAuth
  - ```GOOGLE_AUTH_CLIENT = "some_data"```
  - ```GOOGLE_AUTH_SECRET = "some_data"```
5. Valid GitHub App credentials for OAuth
  - ```GITHUB_AUTH_CLIENT = "some_data"```
  - ```GITHUB_AUTH_SECRET = "some_data"```
6. Valid PayPal Developer credentials for all payments
  - ```PAYPAL_CLIENT_ID = "some_data"```
  - ```PAYPAL_CLIENT_SECRET = "some_data"```
6. Valid PayPal Business account credentials for paying out to users
  - ```PAYPAL_BIZ_ACCOUNT = "user@example.com"```

GeekSurvey can be published on the web by configuring nginx and gunicorn to run the project through a WSGI. [Here](https://www.youtube.com/watch?v=YnrgBeIRtvo) is a good reference for working through this process.

Take care to host the static files separately to support caching. This requires
```python manage.py collectstatic```
to collect the static files into a single folder.

GeekSurvey will fail if it is not hosted with HTTPS, so make sure your domain name is certified and your nginx config uses SSL.

## Contributing

Please read [CONTRIBUTING.md](./CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.


## Authors

- Tim Giroux - *initial work* - [timgiroux](https://github.com/timgiroux)
- Kyle Austria - *initial work* - [kyleaustria8](https://github.com/kyleaustria8)
- Gustavo Valencia - *initial work* - [GustavoMiguelValencia](https://github.com/GustavoMiguelValencia)
- Pengfei Liu - *initial work* - [Pengfei-Y](https://github.com/Pengfei-Y)


## License

This project is licensed under the MIT License - see [LICENSE](./LICENSE) file for details.


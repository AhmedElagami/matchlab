# Netlify Deployment Guide

This project is configured for deployment on Netlify using serverless functions for Django.

## Prerequisites

- A Netlify account
- An external PostgreSQL database (Netlify does not provide managed PostgreSQL)
- Environment variables configured (see below)

## Deployment Steps

1. **Connect your repository** to Netlify via the Netlify UI.

2. **Set environment variables** in Netlify site settings > Environment variables:

   - `DJANGO_SECRET_KEY`: A secure random string for Django's secret key.
   - `DJANGO_DEBUG`: Set to `"False"` for production.
   - `DJANGO_ALLOWED_HOSTS`: Comma-separated list of allowed domains (include your Netlify site domain, e.g., `*.netlify.app`).
   - `POSTGRES_DB`: Database name.
   - `POSTGRES_USER`: Database user.
   - `POSTGRES_PASSWORD`: Database password.
   - `POSTGRES_HOST`: External PostgreSQL host (e.g., from a provider like Supabase, Neon, or AWS RDS).
   - `POSTGRES_PORT`: PostgreSQL port (default `5432`).

3. **Enable the Netlify plugin**:
   - The `netlify-plugin-django` plugin is configured in `netlify.toml`. Netlify will automatically install it during builds.

4. **Deploy**:
   - Netlify will automatically run the build command `python manage.py collectstatic --noinput` and publish the static files to `resources/staticfiles`.
   - The Django application will be served via a serverless function at `/.netlify/functions/django`.

5. **Post-deployment**:
   - Run Django migrations manually via the Netlify CLI or using a one-off script (Netlify does not automatically run migrations).
   - Create a superuser via the Django admin if needed.

## Local Development with Netlify CLI

To test the Netlify configuration locally:

1. Install the Netlify CLI: `npm install -g netlify-cli`
2. Run `netlify dev` to start the local development server with Netlify functions.

## Notes

- Static files are served directly from Netlify's CDN; dynamic requests are routed to the Django serverless function.
- The `awsgi` package is used to adapt Django's WSGI application to the AWS Lambda environment (which Netlify uses under the hood).
- Ensure your external PostgreSQL database is accessible from Netlify's IP ranges.

## Troubleshooting

- If the plugin fails to install, check Netlify's build logs for errors. You may need to manually add the plugin via the Netlify UI.
- If Django cannot connect to the database, verify environment variables and network connectivity.
- For migration issues, consider using a post‑deploy hook or a manual migration script.

## References

- [Netlify Django Plugin](https://github.com/netlify-labs/netlify-plugin-django)
- [Django on Netlify](https://docs.netlify.com/integrations/frameworks/django/)
- [AWSGI documentation](https://pypi.org/project/awsgi/)
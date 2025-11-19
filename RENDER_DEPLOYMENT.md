# Render Deployment Guide

This guide will help you deploy the DISHA application on Render.

## Prerequisites

- Render account (free tier available at https://render.com)
- GitHub repository with your DISHA code
- MongoDB Atlas connection string

## Step-by-Step Deployment

### 1. Connect Your GitHub Repository

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Select "Build and deploy from a Git repository"
4. Connect your GitHub account and select the `DISHA-Social-Internship-Management` repository

### 2. Configure the Web Service

Fill in the following details:

| Field | Value |
|-------|-------|
| **Name** | `disha-app` (or your preferred name) |
| **Environment** | `Python 3` |
| **Region** | `Oregon` (or closest to your location) |
| **Branch** | `main` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn --workers 2 --worker-class sync --timeout 60 wsgi:app` |
| **Plan** | `Free` (for testing/development) |

### 3. Set Environment Variables

In the "Environment" section, add these variables:

| Key | Value |
|-----|-------|
| `MONGODB_URI` | Your MongoDB Atlas connection string |
| `SECRET_KEY` | Generate one: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DEBUG` | `false` |
| `FLASK_ENV` | `production` |
| `DATABASE_NAME` | `disha_db` |

### 4. Deploy

1. Click "Create Web Service"
2. Render will automatically start building your application
3. You can watch the build logs in the dashboard
4. Once deployment is complete, you'll get a URL like `https://disha-app.onrender.com`

## Troubleshooting

### Build Fails with "Module not found"
- Make sure all dependencies are in `requirements.txt`
- Run `pip install -r requirements.txt` locally to verify

### Application crashes after deployment
- Check the logs in Render dashboard
- Ensure `MONGODB_URI` environment variable is set correctly
- Verify your MongoDB Atlas IP whitelist includes Render's IPs (0.0.0.0/0 for free tier)

### Database connection issues
1. Go to MongoDB Atlas → Network Access
2. Allow access from `0.0.0.0/0` (open access, use with caution)
3. Or add Render's IP range: `34.28.0.0/15`

### App sleeps after 15 minutes of inactivity (Free tier)
- Free tier services spin down after 15 min of no traffic
- First request after spin-down may take 30-60 seconds
- Upgrade to paid plan for continuous uptime

## Configuration Details

### What was changed for Render:
- ✅ Removed `Dockerfile` and `docker-compose.yml` (Render uses buildpacks)
- ✅ Updated `Procfile` with optimized gunicorn settings
- ✅ Updated `render.yaml` with Render-specific configuration
- ✅ Modified `gunicorn_config.py` for Render's environment
- ✅ Updated `wsgi.py` to handle Render's PORT environment variable
- ✅ Added `.renderignore` to exclude unnecessary files from build
- ✅ Created `runtime.txt` to specify Python version

### Production Checklist

Before deploying to production:

- [ ] Set `DEBUG=false` in environment variables
- [ ] Generate a strong `SECRET_KEY`
- [ ] Configure MongoDB Atlas with proper access controls
- [ ] Test all features locally first
- [ ] Set up monitoring/logs in Render dashboard
- [ ] Plan for database backups
- [ ] Consider upgrading to paid plan for production use

## Useful Render Commands

### View Logs
```bash
# Logs are available in Render dashboard → Logs tab
```

### Redeploy
- Push changes to GitHub → Automatic redeploy
- Or manual redeploy from Render dashboard

### Environment Variables
- Update in Render dashboard → Environment
- Changes take effect on next deploy

## Additional Resources

- [Render Documentation](https://render.com/docs)
- [Flask on Render](https://render.com/docs/deploy-flask)
- [Gunicorn Documentation](https://docs.gunicornapp.com/)

---

**Need Help?**
- Check Render logs: Dashboard → Your Service → Logs
- Review error messages carefully
- Verify all environment variables are set

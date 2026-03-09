# Deployment Guide - Hostinger

## Quick Deploy to Hostinger

### Option 1: File Manager Upload
1. Log in to your Hostinger account (hpanel.hostinger.com)
2. Go to **Files** > **File Manager**
3. Navigate to `public_html/`
4. Upload all project files maintaining this structure:
   ```
   public_html/
   ├── index.html
   ├── .htaccess
   ├── css/
   │   └── style.css
   └── js/
       ├── app.js
       └── data.js
   ```
5. Your site will be live at your domain!

### Option 2: Git Deploy
1. In Hostinger hPanel, go to **Advanced** > **Git**
2. Add this repository URL
3. Set the branch to deploy
4. Deploy to `public_html/`

### Option 3: FTP Upload
1. Get FTP credentials from Hostinger hPanel > **Files** > **FTP Accounts**
2. Use FileZilla or similar FTP client
3. Connect and upload all files to `public_html/`

## Post-Deployment
- Verify the site loads correctly on your domain
- Test on mobile devices (the app is fully responsive)
- Check that audio pronunciation works (requires HTTPS)

## SSL/HTTPS
- Enable free SSL in Hostinger hPanel > **Security** > **SSL**
- HTTPS is required for the speech synthesis feature to work

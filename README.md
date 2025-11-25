# theptappgit

**Live URL**: https://mytrainerapp-ie-2025.herokuapp.com  
**GitHub**: https://github.com/YOUR_USERNAME/mytrainerapp  
**Time**: November 15, 2025 04:17 PM GMT (IE)

## Purpose
Personal trainer booking system with role-based access (Client / Trainer).

## Features
- Client: Book, view, edit, cancel sessions
- Trainer: View all bookings in admin
- Responsive UI (Bootstrap 5)
- Form validation
- Secure login

## Tech Stack
- **Python 3.12**
- **Django 4.2.26**
- **SQLite** (dev) / **PostgreSQL** (Heroku)
- **Bootstrap 5** + **django-crispy-forms**

## AI Usage (GitHub Copilot)
- Generated `Booking` model with proper fields
- Suggested admin list display and filters
- Helped write form validation logic
- Created unit test skeleton

> **Outcome**: Saved 2+ hours, improved code quality, caught 1 bug early.

## Deployment
- **Auto-deploy** via GitHub → Heroku
- `whitenoise` for static files
- Environment variables via Heroku Config Vars

```bash
git push origin main
# → Heroku auto-deploys

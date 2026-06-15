# Deployment — DIEYNEM website

Production target: **`dieynem.bjptechnologies.co.tz`** on the existing Ubuntu 24.04
box (shared with several PHP/MySQL/Apache sites).

**Topology**

```
Internet → Apache :443 (existing)
             ├─ existing PHP vhosts                         ← untouched
             └─ dieynem vhost  ──reverse proxy──▶  Gunicorn (systemd, unix socket)
                                                       │
                                                       ▼
                                                  PostgreSQL :5432  (new, alongside MySQL :3306)
Merge develop → main  →  GitHub Actions (test ✅)  →  SSH  →  deploy/deploy.sh
```

Nothing here changes the PHP sites: PostgreSQL uses a different port, Gunicorn
listens on a private unix socket, and we add a single new Apache vhost.

---

## ⚠️ Before anything: memory

The box has **~1 GB RAM and 2 cores**, already mostly used by MySQL 8.4 + the PHP
sites + netdata. Add a **2 GB swap file** as a safety net (skip if `swapon
--show` already lists swap):

```bash
sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile
sudo mkswap /swapfile && sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
free -h   # confirm Swap now shows 2.0Gi
```

Gunicorn is set to **2 workers** for this reason — don't raise it without
watching `free -h`/netdata first.

---

## One-time server setup

Run as the `ubuntu` user. `<REPO_SSH_URL>` is this repo's SSH URL
(`git@github.com:<owner>/<repo>.git`) — note it lives on a **different GitHub
account** than the other sites, so we give the server its own read-only deploy
key (below).

### 1. System packages (only the gaps — Python 3.12 & git already present)

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv \
                    postgresql postgresql-contrib \
                    libpq-dev
sudo a2enmod proxy proxy_http headers     # enable the reverse-proxy modules
```

### 2. PostgreSQL role + database

```bash
sudo -u postgres psql <<'SQL'
CREATE ROLE dieynem WITH LOGIN PASSWORD 'CHOOSE_A_STRONG_PASSWORD';
CREATE DATABASE dieynem OWNER dieynem;
SQL
```

Put the same password into `DATABASE_URL` in `.env` (step 5).

### 3. Read-only deploy key (so the server can pull this private repo)

```bash
ssh-keygen -t ed25519 -f ~/.ssh/dieynem_deploy -N "" -C "dieynem-server-pull"
cat ~/.ssh/dieynem_deploy.pub
```

Add that public key in **GitHub → this repo → Settings → Deploy keys → Add deploy
key** (read-only, do **not** allow write). Then tell SSH to use it for this repo:

```bash
cat >> ~/.ssh/config <<'CFG'
Host github-dieynem
    HostName github.com
    User git
    IdentityFile ~/.ssh/dieynem_deploy
    IdentitiesOnly yes
CFG
```

### 4. Clone the repo + virtualenv

```bash
cd /var/www
git clone github-dieynem:<owner>/<repo>.git dieynem.bjptechnologies.co.tz
cd dieynem.bjptechnologies.co.tz
git remote set-url origin github-dieynem:<owner>/<repo>.git   # ensure pulls use the deploy key
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip && pip install -r requirements.txt
```

### 5. Environment file

```bash
cp deploy/.env.example .env
nano .env            # set DJANGO_SECRET_KEY, DATABASE_URL password, SMTP creds
sudo chown ubuntu:www-data .env && chmod 640 .env
```

Generate a secret key:
`python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"`

### 6. First migrate + collectstatic (also seeds all verified content)

```bash
export DJANGO_SETTINGS_MODULE=config.settings.prod
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser    # your dashboard login
```

### 7. Permissions (Gunicorn runs as www-data; uploads need writing)

```bash
sudo chown -R ubuntu:www-data /var/www/dieynem.bjptechnologies.co.tz
sudo chmod -R g+rX /var/www/dieynem.bjptechnologies.co.tz
sudo chown -R www-data:www-data media        # app writes uploads here
sudo chmod -R g+rwX media
```

### 8. Gunicorn service

```bash
sudo cp deploy/gunicorn-dieynem.service /etc/systemd/system/gunicorn-dieynem.service
sudo systemctl daemon-reload
sudo systemctl enable --now gunicorn-dieynem
systemctl status gunicorn-dieynem            # should be active (running)
```

### 9. Apache vhost + TLS

```bash
sudo cp deploy/apache-dieynem.bjptechnologies.co.tz.conf \
        /etc/apache2/sites-available/dieynem.bjptechnologies.co.tz.conf
sudo a2ensite dieynem.bjptechnologies.co.tz
sudo apache2ctl configtest && sudo systemctl reload apache2
sudo certbot --apache -d dieynem.bjptechnologies.co.tz   # issues HTTPS + redirect
```

### 10. Passwordless restart for CI

```bash
sudo install -m 0440 deploy/sudoers-dieynem-deploy /etc/sudoers.d/dieynem-deploy
sudo visudo -cf /etc/sudoers.d/dieynem-deploy            # must say "parsed OK"
```

Visit **https://dieynem.bjptechnologies.co.tz** — the site should be live.

---

## Wiring auto-deploy (GitHub Actions → server)

The workflow `.github/workflows/deploy.yml` runs the test suite on every push to
`main` and, if green, SSHes in and runs `deploy/deploy.sh`. It needs a second
key — one that lets **Actions log into the server** (distinct from the read-only
deploy key in step 3).

1. On a local machine, make the CI key pair:
   ```bash
   ssh-keygen -t ed25519 -f dieynem_ci -N "" -C "github-actions-deploy"
   ```
2. Authorise it on the server:
   ```bash
   # paste dieynem_ci.pub into the server's authorized_keys for the deploy user
   cat dieynem_ci.pub | ssh ubuntu@<server-ip> 'cat >> ~/.ssh/authorized_keys'
   ```
3. In **GitHub → this repo → Settings → Secrets and variables → Actions**, add:

   | Secret | Value |
   |---|---|
   | `DEPLOY_HOST` | server IP / hostname |
   | `DEPLOY_USER` | `ubuntu` |
   | `DEPLOY_PORT` | `22` |
   | `DEPLOY_PATH` | `/var/www/dieynem.bjptechnologies.co.tz` |
   | `DEPLOY_SSH_KEY` | **contents of the private `dieynem_ci` file** |

4. Delete the local `dieynem_ci` private key after pasting it into the secret.

From then on: **merge `develop → main` → tests run → site deploys automatically.**
Trigger a manual run any time from the Actions tab ("Run workflow").

---

## Day-to-day

```bash
# Logs
journalctl -u gunicorn-dieynem -f
sudo tail -f /var/log/apache2/dieynem-error.log

# Manual deploy / restart
bash deploy/deploy.sh
sudo systemctl restart gunicorn-dieynem
```

**Rollback:** `git -C /var/www/dieynem.bjptechnologies.co.tz reset --hard <good-sha>`
then `bash deploy/deploy.sh` (it will run migrations + restart).

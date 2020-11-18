source ~/.bash_profile
cd /home/ec2-user/waffle-rookies-18.5-backend-2/
git pull
pyenv activate waffle-backend
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py check --deploy
uwsgi --ini /home./ec2-user/waffle-rookies-18.5-backend-2/waffle_backend/waffle-backend_uwsgi.ini
sudo nginx -t
sudo service nginx start

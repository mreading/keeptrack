# keeptrack

# After making changes to database: 
	python manage.py makemigrations (builds script to change the database)
	python manage.py migrate (executes that script)
	
# Github workflow:
	git pull
	(make changes to files)
	git add . (make sure you are in the highest level directory, the one with the manage.py file in it)
	git commit -m "this is where your commit message goes"
	git push
    
# If locked out of account
    from axes.utils import *
    reset()
	
	


#!/.condaUser/.anaconda3/envs/snoutScan/bin/python3 
from main.api.model import db, Profile

if __name__ == '__main__':
    print('Dropping all tables...')
    db.drop_all()

    print('Creating all database tables...')
    db.create_all()

    p = Profile("admin", "EWnwjBNLPGi0l8mOOEKF")
    p.isadmin = True
    db.session.add(p)
    db.session.commit()

    print('Done!')

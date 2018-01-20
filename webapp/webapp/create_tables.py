from main.api.model import db, Profile

if __name__ == '__main__':
    print('Creating all database tables...')
    db.create_all()

    p = Profile("admin", "EWnwjBNLPGi0l8mOOEKF")
    p.isadmin = True
    db.session.add(p)
    db.session.commit()

    print('Done!')

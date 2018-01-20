from main.api.model import db

if __name__ == '__main__':
    print('Droping all database tables...')
    db.drop_all()
    print('Done!')

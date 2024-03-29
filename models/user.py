import datetime
import uuid
from flask import session

from sourceCode.common.database import Database
from sourceCode.models.blog import Blog


class User(object):
    def __init__(self, email, password, _id=None):
        self.email = email
        self.password = password
        self._id = self._id = uuid.uuid4().hex if _id is None else _id

    @classmethod
    def find_by_email(cls, email):
        data = Database.find_one('users', {'email': email})
        if data is not None:
            return cls(**data)

    @classmethod
    def find_by_id(cls, _id):
        data = Database.find_one('users', {'_id': _id})
        if data is not None:
            return cls(**data)

    @staticmethod
    def login_check(email, password):
        user = User.find_by_email(email)
        if user is not None:
            return user.password == password
        else:
            return False

    @staticmethod
    def register(email, password):
        user = User.find_by_email(email)
        if user is None:
            new_user = User(email, password)
            new_user.save_to_mongo()
            session['email'] = email
            return True
        return False

    @staticmethod
    def login(email):
        session['email'] = email

    @staticmethod
    def logout():
        session['email'] = None

    def get_blogs(self):
        return Blog.find_by_user_id(self._id)

    def new_blog(self, title, description):
        blog = Blog(title=title,
                    author_id=self._id,
                    author=self.email,
                    description=description)
        blog.save_to_mongo()

    @staticmethod
    def new_post(blog_id, title, content, date=datetime.datetime.utcnow()):
        blog = Blog.from_mongo(blog_id)
        blog.new_post(title=title,
                      content=content,
                      date=date)

    def json(self):
        return {
            'email': self.email,
            '_id': self._id,
            'password': self.password
        }

    def save_to_mongo(self):
        Database.insert(collection='users',
                        data=self.json())

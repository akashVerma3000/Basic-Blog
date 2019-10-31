import uuid
import datetime
from sourceCode.common.database import Database
from sourceCode.models.post import Posts


class Blog(object):
    def __init__(self, title, author_id, author, description, _id=None):
        self.title = title
        self.author_id = author_id
        self.author = author
        self.description = description
        self._id = uuid.uuid4().hex if _id is None else _id

    def new_post(self, title, content, date=datetime.datetime.utcnow()):

        post = Posts(title, self._id, self.author, content, created_date=date)

        post.save_to_mongo()
        
    def get_posts(self):
        return Posts.from_blog(self._id)

    def save_to_mongo(self):
        Database.insert(collection='blogs', data=self.json())

    def json(self):
        return {
            'title': self.title,
            'author_id': self.author_id,
            'author': self.author,
            'description': self.description,
            '_id': self._id
        }

    @classmethod
    def from_mongo(cls, _id):
        blog_data = Database.find_one(collection='blogs',
                                      query={'_id': _id})
        return cls(**blog_data)

    @classmethod
    def find_all(cls):
        user_data = Database.find('blogs', {})
        return [cls(**data) for data in user_data]

    @classmethod
    def find_by_user_id(cls, author_id):
        user_data = Database.find('blogs', {'author_id': author_id})
        return [cls(**data) for data in user_data]

    def delete_blog(self):
        Database.delete_one('blogs', {"_id": self._id})


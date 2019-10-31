import uuid
import datetime
from sourceCode.common.database import Database


class Posts(object):
    def __init__(self, title, blog_id, author, content, _id=None, created_date=datetime.datetime.utcnow()):
        self._id = uuid.uuid4().hex if _id is None else _id
        self.title = title
        self.blog_id = blog_id
        self.author = author
        self.content = content
        self.created_date = created_date

    def save_to_mongo(self):
        Database.insert(collection='posts', data=self.json())

    def json(self):
        return(
            {
                'blog_id': self.blog_id,
                '_id': self._id,
                'title': self.title,
                'author': self.author,
                'content': self.content,
                'created_date': self.created_date
            }
        )
    
    @classmethod
    def from_mongo(cls, id):
        data = Database.find_one('posts', {'_id': id})
        if data is not None:
            return cls(**data)
    
    @staticmethod
    def from_blog(id):
        return [post for post in Database.find(collection='posts',
                                               query={'blog_id': id})]

    def delete_post(self):
        Database.delete_one('posts', {"_id": self._id})

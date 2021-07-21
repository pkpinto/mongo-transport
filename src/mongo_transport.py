from datetime import datetime, timezone
from enum import Enum
import logging

import pymongo


class Status(Enum):
    PENDING = 0
    PROCESSED = 1
    SUCCESS = 2
    FAILURE = 3


class SubscriptionIter:

    def __init__(self, collection, topic) -> None:
        self.logger = logging.getLogger(__name__)
        self.collection = collection
        self.topic = topic
        # used to reset the cursor when/if it dies
        self._ts = self.collection.find().sort('$natural', pymongo.ASCENDING).limit(-1).next()['ts']
        self.cursor = None

    def __iter__(self):
        if self.cursor is None or not self.cursor.alive:
            self.cursor = self.collection.find(
                {'topic': self.topic, 'status': Status.PENDING.value, 'ts': {'$gt': self._ts}},
                cursor_type=pymongo.CursorType.TAILABLE_AWAIT,
            )
            self.logger.info('tailable cursor created')
        return self

    def __next__(self):
        while(True):
            doc = self.cursor.next()
            r = self.collection.update(
                {'_id': doc['_id'], 'status': Status.PENDING.value},
                {'$set': {'ts': datetime.now(timezone.utc), 'status': Status.PROCESSED.value}},
            )
            if r['nModified'] == 1:
                self.logger.debug('next message:\n{}'.format(doc))
                self._ts = doc['ts']
                return doc


class MongoTransport:

    def __init__(self, db, collection_name='msg_transport', size=5242880, max=5000) -> None:
        self.logger = logging.getLogger(__name__)

        self.db = db
        self.collection_name = collection_name
        self.size = size
        self.max = max

        if self.collection_name not in self.db.list_collection_names():
            self.collection = self.db.create_collection(self.collection_name, capped=True, size=self.size, max=self.max)
            self.logger.info('collection {} created'.format(self.collection_name))
        else:
            self.collection = self.db[self.collection_name]
            if self.collection.options().get('capped', False) is False:
                raise pymongo.errors.CollectionInvalid('collection {} exists but is not capped'.format(self.collection_name))
            else:
                self.logger.info('using collection {}'.format(self.collection_name))

    def publish(self, topic, data):
        record = dict(topic=topic, ts=datetime.utcnow(), status=Status.PENDING.value, data=data)
        return self.collection.insert_one(record)

    def subscribe(self, topic):
        return SubscriptionIter(self.collection, topic)

    def clear(self):
        self.collection.drop()
        self.logger.info('collection {} dropped'.format(self.collection_name))
        self.collection = self.db.create_collection(self.collection_name, capped=True, size=self.size, max=self.max)
        self.logger.info('collection {} created'.format(self.collection_name))


def main():

    db = pymongo.mongo_client.MongoClient('localhost')['booktracker']
    transporter = MongoTransport(db)

    for i in range(100):
        transporter.publish('test topic', {str(i): i})

    # idx = 'sub2'
    # while(True):
    #     for msg in transporter.subscribe('test topic'):
    #         print('{}: {}'.format(idx, msg['data']))



if __name__ == '__main__':
    main()

from tgt_grease_core_util import Logging
from tgt_grease_core_util.Database import MongoConnection
import datetime
from pymongo.errors import ServerSelectionTimeoutError
import json
import hashlib
import os
import pymongo
from difflib import SequenceMatcher
import threading


class SourceDeDuplify(object):
    def __init__(self, logger, collection='source_dedup'):
        # type: (Logging.Logger) -> None
        self._logger = logger
        self._final_result = []
        try:
            self._mongo_connection = MongoConnection()
            self._client = self._mongo_connection.client()
            self._db = self._client.get_database(
                name=os.getenv('GREASE_MONGO_DB', 'grease'),
                write_concern=pymongo.WriteConcern(w=0)
            )
            self._collection = self._db.get_collection(name=collection)
            self._dedup = True
        except ServerSelectionTimeoutError:
            self._mongo_connection = None
            self._client = None
            self._db = None
            self._collection = None
            self._dedup = False

    def __del__(self):
        self._client.close()

    def create_unique_source(self, source_name, field_set, source):
        # type: (str, list, list) -> list
        if not self._dedup:
            self._logger.error("Failed To connect to MongoDB de-duplication is off", hipchat=True)
            return source
        # we could connect lets process
        if not isinstance(source, list):
            self._logger.error('DeDuplification did not receive list returning empty', hipchat=True)
            return []
        self._logger.debug("STARTING DEDUPLICATION::TOTAL OBJECTS TO PROCESS [" + str(len(source)) + "]")
        # now comes James' version of machine learning. I call it "Blue Collar Machine Learning"
        source_pointer = 0
        source_max = len(source)
        threads = []
        for source_obj in source:
            source_pointer += 1
            if not isinstance(source_obj, dict):
                self._logger.warning('DeDuplification Received NON-DICT Type: [' + str(type(source_obj)) + ']')
                continue
            proc = threading.Thread(
                target=self.process_obj,
                args=(source_name, source_max, source_pointer, field_set, source_obj,),
                name="GREASE DEDUPLICATION THREAD [{0}/{1}]".format(source_pointer, source_max)
            )
            proc.daemon = True
            proc.start()
            threads.append(proc)
        while len(threads) > 0:
            final = []
            for thread in threads:
                if thread.isAlive():
                    final.append(thread)
            threads = final
        # create the auto del index if it doesnt already exist
        self._collection.create_index([('expiry', 1), ('expireAfterSeconds', 1)])
        self._collection.create_index([('max_expiry', 1), ('expireAfterSeconds', 1)])
        remaining = len(self._final_result) - 1
        if remaining < 0:
            remaining = 0
        self._logger.debug("DEDUPLICATION COMPLETE::REMAINING OBJECTS [" + str(remaining) + "]")
        return self._final_result

    def process_obj(self, source_name, source_max, source_pointer, field_set, source_obj):
        # first thing try to find the object level hash
        hash_obj = self._collection.find_one({'hash': self.generate_hash(source_obj)})
        if not hash_obj:
            self._logger.debug("Failed To Locate Type1 Match, Performing Type2 Search Match", True)
            # Globally unique hash for request
            # create a completely new document hash and all the field set hashes
            self._collection.insert_one({
                'expiry': self.generate_expiry_time(),
                'max_expiry': self.generate_max_expiry_time(),
                'source': str(source_name),
                'score': 1,
                'hash': self.generate_hash(source_obj),
                'type': 1
            })
            # Next start field level processing
            # first check if our fields are limited
            if len(field_set) < 1:
                # All fields need to be considered for de-dup
                fields = source_obj.keys()
            else:
                # only registered fields
                fields = field_set
            # now lets get the composite score
            composite_score = self.get_field_score(source_name, source_obj, fields)
            self._logger.debug(
                "DEDUPLICATION COMPOSITE SCORE ["
                + str(source_pointer)
                + "/"
                + str(source_max)
                + "]: "
                + str(composite_score)
            )
            # now lets observe to see if we have a 'unique' source
            if composite_score < float(os.getenv('GREASE_DEDUP_SCORE', 85)):
                # look at that its time to add it to the final list
                self._logger.debug("Type2 ruled Unique adding to final result", True)
                self._final_result.append(source_obj)
        else:
            # we have a duplicate source document
            # increase the counter and expiry and move on (DROP)
            self._logger.debug("Type1 match found, dropping", True)
            if 'max_expiry' in hash_obj:
                update_statement = {
                    "$set": {
                        'score': int(hash_obj['score']) + 1,
                        'expiry': self.generate_expiry_time()
                    }
                }
            else:
                update_statement = {
                    "$set": {
                        'score': int(hash_obj['score']) + 1,
                        'expiry': self.generate_expiry_time(),
                        'max_expiry': self.generate_max_expiry_time()
                    }
                }
            self._collection.update_one(
                {'_id': hash_obj['_id']},
                update_statement
            )

    def get_field_score(self, source_name, document, field_set):
        # type: (str, dict, list) -> float
        # This function does a field by field assessment of a source
        # Woo is what I said too
        # first lets create our array of field scores
        score_list = []
        for field in field_set:
            if field in document:
                # unicode check because idk even man + Sha256 hash if too long
                if not document[field]:
                    document[field] = ''
                if isinstance(document[field], unicode):
                    check_document = {
                        'source': str(source_name),
                        'field': str(field),
                        'value': document[field].encode('utf-8')
                    }
                else:
                    check_document = {
                        'source': str(source_name),
                        'field': str(field),
                        'value': str(document[field]).encode('utf-8')
                    }
                # lets only observe fields in our list
                field_obj = self._collection.find_one({'hash': self.generate_hash(check_document)})
                if not field_obj:
                    self._logger.debug("Failed To Locate Type2 Match, Performing Type2 Search", True)
                    # globally unique field->value pair
                    # alright lets start the search for all fields of its name
                    field_probability_list = []
                    for record in self._collection.find({'source': str(source_name), 'field': field})\
                            .sort('score', pymongo.ASCENDING) \
                            .limit(int(os.getenv('GREASE_DEDUP_INSPECTION_STRENGTH', 100))):
                        # Now we are looping through our fields
                        if self.compare_strings(record['value'], check_document['value']) > .95:
                            # we found a VERY strong match
                            score_list.append(1 - self.compare_strings(record['value'], check_document['value']))
                            # leave the for loop since we found a highly probable match
                            break
                        else:
                            field_probability_list.append(self.compare_strings(record['value'], check_document['value']))
                    self._logger.debug("Failed To Location Type1 Match, Performing Type2 Search", True)
                    # lets record it in the 'brain' to remember it
                    check_document['hash'] = self.generate_hash(check_document)
                    check_document['score'] = 1
                    check_document['expiry'] = self.generate_expiry_time()
                    check_document['max_expiry'] = self.generate_max_expiry_time()
                    check_document['type'] = 2
                    self._collection.insert_one(check_document)
                    # now lets either choose the highest probable match we found or 0 being a completely globally
                    # unique value (No matches found in the above loop
                    if len(field_probability_list) > 0:
                        probability_average = float(sum(field_probability_list) / len(field_probability_list))
                        self._logger.debug("Field Probability Average: source [{0}] field [{1}] is [{2}]"
                                           .format(source_name, field, probability_average), True)
                        score_list.append(probability_average)
                    else:
                        score_list.append(100)
                else:
                    self._logger.debug("Found Type2 Match! Dropping", True)
                    # exact match we can bug out
                    if 'max_expiry' in field_obj:
                        update_statement = {
                            "$set": {
                                'score': int(field_obj['score']) + 1,
                                'expiry': self.generate_expiry_time()
                            }
                        }
                    else:
                        update_statement = {
                            "$set": {
                                'score': int(field_obj['score']) + 1,
                                'expiry': self.generate_expiry_time(),
                                'max_expiry': self.generate_max_expiry_time()
                            }
                        }
                    self._collection.update_one(
                        {'_id': field_obj['_id']},
                        update_statement
                    )
                    score_list.append(0)

        # finally return our aggregate field score
        if len(score_list) is 0:
            return 0
        return sum(score_list) / float(len(score_list))

    @staticmethod
    def generate_hash(document):
        # type: (dict) -> str
        return hashlib.sha256(json.dumps(document)).hexdigest()

    @staticmethod
    def generate_expiry_time():
        return datetime.datetime.utcnow() + datetime.timedelta(hours=int(os.getenv('GREASE_DEDUP_TIMEOUT', 12)))

    @staticmethod
    def generate_max_expiry_time():
        return datetime.datetime.utcnow() + datetime.timedelta(weeks=int(os.getenv('GREASE_DEDUP_MAX_TIMEOUT', 1)))

    @staticmethod
    def compare_strings(constant, variable):
        # type: (str, str) -> float
        return SequenceMatcher(constant, variable).ratio()

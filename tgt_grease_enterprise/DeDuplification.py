from tgt_grease_core_util import Logging, Configuration
from tgt_grease_core_util.Database import MongoConnection
import datetime
from pymongo.errors import ServerSelectionTimeoutError
import json
import hashlib
import os
import pymongo
from difflib import SequenceMatcher
from psutil import cpu_percent, virtual_memory
import threading


class SourceDeDuplify(object):
    def __init__(self, logger, collection='source_dedup'):
        # type: (Logging.Logger) -> None
        self._logger = logger
        self.collection_name = collection
        self._config = Configuration()
        try:
            self._mongo_connection = MongoConnection()
            self._client = self._mongo_connection.client()
            self._db = self._client.get_database(
                name=os.getenv('GREASE_MONGO_DB', 'grease'),
                write_concern=pymongo.WriteConcern(w=0)
            )
            self._collection = self._db.get_collection(name=self.collection_name)
            self._dedup = True
        except ServerSelectionTimeoutError:
            self._mongo_connection = None
            self._client = None
            self._db = None
            self._collection = None
            self._dedup = False

    def __del__(self):
        self._client.close()

    def create_unique_source(self, source_name, field_set, source, strength=None):
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
        final = []
        while source_pointer < source_max:
            # Ensure we aren't swamping the system
            cpu = cpu_percent(interval=.1)
            mem = virtual_memory().percent
            if \
                    cpu >= int(self._config.get('GREASE_THREAD_MAX', '85')) \
                    or mem >= int(self._config.get('GREASE_THREAD_MAX', '85')):
                self._logger.info("sleeping due to high memory consumption", verbose=True)
                # remove variables
                del cpu
                del mem
                continue
            if not isinstance(source[source_pointer], dict):
                self._logger.warning(
                    'DeDuplification Received NON-DICT from source: [{0}] Type: [{1}] got: [{2}]'.format(
                        source_name,
                        str(type(source[source_pointer])),
                        str(source[source_pointer])
                    )
                )
                source_pointer += 1
                continue
            if source_pointer is 0:
                pid_num = 1
            else:
                pid_num = source_pointer
            proc = threading.Thread(
                target=self.process_obj,
                args=(
                    self.collection_name,
                    self._logger,
                    source_name,
                    source_max,
                    source_pointer,
                    field_set,
                    source[source_pointer],
                    final,
                    strength,
                ),
                name="GREASE DEDUPLICATION THREAD [{0}/{1}]".format(pid_num, source_max)
            )
            proc.daemon = True
            proc.start()
            threads.append(proc)
            source_pointer += 1
        self._logger.debug("All source objects have been threaded for processing", verbose=True)
        while len(threads) > 0:
            self._logger.debug("Current DeDuplication Threads [{0}]".format(len(threads)), verbose=True)
            threads_final = []
            for thread in threads:
                if thread.isAlive():
                    threads_final.append(thread)
            threads = threads_final
            self._logger.debug("Remaining DeDuplication Threads [{0}]".format(len(threads)), verbose=True)
        # create the auto del index if it doesnt already exist
        self._collection.create_index([('expiry', 1), ('expireAfterSeconds', 1)])
        self._collection.create_index([('max_expiry', 1), ('expireAfterSeconds', 1)])
        if len(final) == 1:
            self._logger.debug("DEDUPLICATION COMPLETE::REMAINING OBJECTS [1]")
            return final
        else:
            remaining = len(final) - 1
            self._logger.debug("DEDUPLICATION COMPLETE::REMAINING OBJECTS [{0}]".format(remaining))
            return final

    @staticmethod
    def process_obj(collection_name, logger, source_name, source_max, source_pointer, field_set, source_obj, final, strength=None):
        # first thing try to find the object level hash
        mongo_connection = MongoConnection()
        client = mongo_connection.client()
        db = client.get_database(
            name=os.getenv('GREASE_MONGO_DB', 'grease'),
            write_concern=pymongo.WriteConcern(w=0)
        )
        collection = db.get_collection(name=collection_name)
        hash_obj = collection.find_one({'hash': SourceDeDuplify.generate_hash(source_obj)})
        if not hash_obj:
            logger.debug("Failed To Locate Type1 Match, Performing Type2 Search Match", True)
            # Globally unique hash for request
            # create a completely new document hash and all the field set hashes
            collection.insert_one({
                'expiry': SourceDeDuplify.generate_expiry_time(),
                'max_expiry': SourceDeDuplify.generate_max_expiry_time(),
                'source': str(source_name),
                'score': 1,
                'hash': SourceDeDuplify.generate_hash(source_obj),
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
            composite_score = SourceDeDuplify.get_field_score(collection, logger, source_name, source_obj, fields)
            if source_pointer is 0:
                compo_spot = 1
            else:
                compo_spot = source_pointer
            logger.debug(
                "DEDUPLICATION COMPOSITE SCORE ["
                + str(compo_spot)
                + "/"
                + str(source_max)
                + "]: "
                + str(composite_score)
            )
            # now lets observe to see if we have a 'unique' source
            if strength is None:
                composite_score_limit = float(os.getenv('GREASE_DEDUP_SCORE', 85))
            else:
                if isinstance(strength, int) or isinstance(strength, float):
                    logger.debug("Global DeDuplication strength override", verbose=True)
                    composite_score_limit = float(strength)
                else:
                    composite_score_limit = float(os.getenv('GREASE_DEDUP_SCORE', 85))
            if composite_score < composite_score_limit:
                # look at that its time to add it to the final list
                logger.debug("Type2 ruled Unique adding to final result", True)
                final.append(source_obj)
        else:
            # we have a duplicate source document
            # increase the counter and expiry and move on (DROP)
            logger.debug("Type1 match found, dropping", True)
            if 'max_expiry' in hash_obj:
                update_statement = {
                    "$set": {
                        'score': int(hash_obj['score']) + 1,
                        'expiry': SourceDeDuplify.generate_expiry_time()
                    }
                }
            else:
                update_statement = {
                    "$set": {
                        'score': int(hash_obj['score']) + 1,
                        'expiry': SourceDeDuplify.generate_expiry_time(),
                        'max_expiry': SourceDeDuplify.generate_max_expiry_time()
                    }
                }
            collection.update_one(
                {'_id': hash_obj['_id']},
                update_statement
            )

    @staticmethod
    def get_field_score(collection, logger, source_name, document, field_set):
        # type: (Collection, Logging.Logger, str, dict, list) -> float
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
                field_obj = collection.find_one({'hash': SourceDeDuplify.generate_hash(check_document)})
                if not field_obj:
                    logger.debug("Failed To Locate Type2 Match, Performing Type2 Search", True)
                    # globally unique field->value pair
                    # alright lets start the search for all fields of its name
                    field_probability_list = []
                    for record in collection.find({'source': str(source_name), 'field': field})\
                            .sort('score', pymongo.ASCENDING) \
                            .limit(int(os.getenv('GREASE_DEDUP_INSPECTION_STRENGTH', 100))):
                        # Now we are looping through our fields
                        if SourceDeDuplify.compare_strings(record['value'], check_document['value']) > .95:
                            # we found a VERY strong match
                            score_list.append(
                                1 - SourceDeDuplify.compare_strings(record['value'], check_document['value'])
                            )
                            # leave the for loop since we found a highly probable match
                            break
                        else:
                            field_probability_list.append(
                                SourceDeDuplify.compare_strings(record['value'], check_document['value'])
                            )
                    logger.debug("Failed To Location Type1 Match, Performing Type2 Search", True)
                    # lets record it in the 'brain' to remember it
                    check_document['hash'] = SourceDeDuplify.generate_hash(check_document)
                    check_document['score'] = 1
                    check_document['expiry'] = SourceDeDuplify.generate_expiry_time()
                    check_document['max_expiry'] = SourceDeDuplify.generate_max_expiry_time()
                    check_document['type'] = 2
                    collection.insert_one(check_document)
                    # now lets either choose the highest probable match we found or 0 being a completely globally
                    # unique value (No matches found in the above loop
                    if len(field_probability_list) > 0:
                        probability_average = float(sum(field_probability_list) / len(field_probability_list))
                        logger.debug(
                            "Field Probability Average: source [{0}] field [{1}] is [{2}]".format(
                                source_name,
                                field,
                                probability_average
                            ),
                            True
                        )
                        score_list.append(probability_average)
                    else:
                        score_list.append(100)
                else:
                    logger.debug("Found Type2 Match! Dropping", True)
                    # exact match we can bug out
                    if 'max_expiry' in field_obj:
                        update_statement = {
                            "$set": {
                                'score': int(field_obj['score']) + 1,
                                'expiry': SourceDeDuplify.generate_expiry_time()
                            }
                        }
                    else:
                        update_statement = {
                            "$set": {
                                'score': int(field_obj['score']) + 1,
                                'expiry': SourceDeDuplify.generate_expiry_time(),
                                'max_expiry': SourceDeDuplify.generate_max_expiry_time()
                            }
                        }
                    collection.update_one(
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

from tgt_grease.core import GreaseContainer
from psutil import virtual_memory, cpu_percent
from bson.objectid import ObjectId
import threading
import hashlib
import datetime
import difflib
import pymongo


class Deduplication(object):
    """Responsible for Deduplication Operations

    Deduplication in GREASE is a multi-step process to ensure performance and accuracy of deduplication. The overview of
    this process is this:
        - Step 1: Identify a Object Type 1 Hash Match. A Type 1 Object (T1) is a SHA256 hash of a dictionary in a data list. If we can hash the entire object and find a match then the object is 100% duplicate.
        - Step 2: Object Type 2 Matching. If a Type 1 (T1) object cannot be found Type 2 Object (T2) deduplication occurs. This will introspect the dictionary for each field and map them against other likely objects of the same type. If a hash match is found (source + field + value as a SHA256) then the field is 100% duplicate. The aggregate score of all fields or the specified subset is above the provided threshold then the object is duplicate. This prevents similar objects from passing through when they are most likely updates to an original object that does not need to be computed on. If a field updates that you will need always then exclude it will need to be passed into the `Deduplicate` function.

    Object examples::

        # Type 1 Object

        {
            '_id': ObjectId, # <-- MongoDB ObjectID
            'type: Int, # <-- Always Type 1
            'hash': String, # <-- SHA256 hash of entire object
            'expiry': DateTime, # <-- Expiration time if no objects are found to be duplicate after which object will be deleted
            'max_expiry': DateTime, # <-- Expiration time for object to be deleted when reached
            'score': Int, # <-- Amount of times this object has been found
            'source': String # <-- Source of the object
        }
        # Type 2 Object
        {
            '_id': ObjectId, # <-- MongoDB ObjectID
            'type: Int, # <-- Always Type 2
            'source': String, # <-- Source of data
            'field': String, # <-- Field in Object
            'value': String, # <-- Value of Object's field
            'hash': String, # <-- SHA256 of source + field + value
            'expiry': DateTime, # <-- Expiration time if no objects are found to be duplicate after which object will be deleted
            'max_expiry': DateTime, # <-- Expiration time for object to be deleted when reached
            'score': Int, # <-- Amount of times this object has been found
            'parentId': ObjectId # <-- T1 Object ID from parent
        }

    Attributes:
        ioc (GreaseContainer): IoC access for DeDuplication

    """

    def __init__(self, ioc=None):
        if isinstance(ioc, GreaseContainer):
            self.ioc = ioc
        else:
            self.ioc = GreaseContainer()

    def Deduplicate(self, data, source, configuration, threshold, expiry_hours, expiry_max, collection, field_set=None):
        """Deduplicate data

        This method will deduplicate the `data` object to allow for only unique objects to be returned. The collection
        variable will be the collection deduplication data will be stored in

        Args:
            data (list[dict]): **list or single dimensional dictionaries** to deduplicate
            source (str): Source of data being deduplicated
            configuration (str): Configuration Name Provided
            threshold (float): level of duplication allowed in an object (the lower the threshold the more uniqueness is required)
            expiry_hours (int): Hours to retain deduplication data
            expiry_max (int): Maximum days to retain deduplication data
            collection (str): Deduplication collection to use
            field_set (list, optional): Fields to deduplicate on

        Note:
            expiry_hours is specific to how many hours objects will be persisted for if they are not seen again

        Returns:
            list[dict]: Deduplicated data

        """
        # ensure we got a list
        if not isinstance(data, list):
            self.ioc.getLogger().error(
                "Data was not of type list for Deduplication got type [{0}]".format(str(type(data))),
                notify=False,
                verbose=True
            )
            return []
        # ensure there is data to parse
        if len(data) <= 0:
            # empty list return empty lists
            return []
        self.ioc.getLogger().trace(
            "Starting deduplication from data source [{0}] total records to parse [{1}]".format(source, len(data)),
            trace=True
        )
        # now comes James' version of machine learning. I call it "Blue Collar Machine Learning"
        # Pointer to access items in the list
        data_pointer = 0
        # Max Length
        data_max = len(data)
        if data_max is 0:
            # we have no data to process
            self.ioc.getLogger().trace("Length of data is zero", verbose=True)
            return []
        # Thread pool
        threads = []
        # Final result
        final = []
        # loop through the objects
        while data_pointer < data_max:
            # ensure we don't swamp the system resources
            cpu = cpu_percent(interval=.1)
            mem = virtual_memory().percent
            if \
                    cpu >= int(self.ioc.getConfig().get('NodeInformation', 'ResourceMax')) or \
                    mem >= int(self.ioc.getConfig().get('NodeInformation', 'ResourceMax')):
                self.ioc.getLogger().trace("Deduplication sleeping; System resource maximum reached", verbose=True)
                # remove variables
                del cpu
                del mem
                continue
            # Resources are available lets start cooking down this list
            # Poll the active threads to ensure we are cleaning up
            self.ioc.getLogger().trace("Thread Pool polling Starting", verbose=True)
            threads_final = []
            for thread in threads:
                if thread.isAlive():
                    threads_final.append(thread)
            threads = threads_final
            self.ioc.getLogger().trace("Thread polling complete", verbose=True)
            self.ioc.getLogger().trace("Total current deduplication threads [{0}]".format(len(threads)), verbose=True)
            # ensure we do not breach the thread limit for the server
            if len(threads) >= int(self.ioc.getConfig().get('NodeInformation', 'DeduplicationThreads')):
                self.ioc.getLogger().trace(
                    "Thread max reached. Deduplication waiting for threads to complete",
                    verbose=True
                )
                continue
            # Ensure each object is a dictionary
            if not isinstance(data[data_pointer], dict):
                self.ioc.getLogger().warning(
                    'DeDuplication Received NON-DICT from source: [{0}] Type: [{1}] got: [{2}]'.format(
                        source,
                        str(type(data[data_pointer])),
                        str(data[data_pointer])
                    )
                )
                data_pointer += 1
                continue
            # create thread for deduplication
            proc = threading.Thread(
                target=self.deduplicate_object,
                args=(
                    self.ioc,
                    data[data_pointer],
                    expiry_hours,
                    expiry_max,
                    threshold,
                    source,
                    configuration,
                    final,
                    collection,
                    data_pointer,
                    data_max,
                    field_set,
                ),
                name="GREASE DEDUPLICATION THREAD [{0}/{1}]".format(data_pointer, data_max)
            )
            proc.daemon = True
            proc.start()
            threads.append(proc)
            data_pointer += 1
            self.ioc.getLogger().trace("Total current deduplication threads [{0}]".format(len(threads)), verbose=True)
        self.ioc.getLogger().info("All data objects have been threaded for processing", verbose=True)
        # wait for threads to finish out
        while len(threads) > 0:
            self.ioc.getLogger().trace("Total current deduplication threads [{0}]".format(len(threads)), verbose=True)
            threads_final = []
            for thread in threads:
                if thread.isAlive():
                    threads_final.append(thread)
            threads = threads_final
            self.ioc.getLogger().trace("Total current deduplication threads [{0}]".format(len(threads)), verbose=True)
        # ensure collections expiry timers are in place
        self.ioc.getCollection(collection).create_index([('expiry', 1)], expireAfterSeconds=1)
        self.ioc.getCollection(collection).create_index([('max_expiry', 1)], expireAfterSeconds=1)
        return final

    @staticmethod
    def deduplicate_object(ioc, obj, expiry, expiry_max, threshold, source_name, configuration_name, final, collection, data_pointer=None, data_max=None, field_set=None):
        """DeDuplicate Object

        This is the method to actually deduplicate an object. The `final` argument is appended to with the obj if it
        was successfully deduplicated.

        Args:
            ioc (GreaseContainer): IoC for the instance
            obj (dict): Object to be deduplicated
            expiry (int): Hours to deduplicate for
            expiry_max (int): Maximum days to deduplicate for
            threshold (float): level of duplication allowed in an object (the lower the threshold the more uniqueness is required)
            source_name (str): Source of data being deduplicated
            configuration_name (str): Configuration being deduplicated for
            final (list): List to append `obj` to if unique
            collection (str): Name of deduplication collection
            data_pointer (int): If provided will provide log information relating to thread
                (Typically used via `Deduplicate`)
            data_max (int): If provided will provide log information relating to thread
                (Typically used via `Deduplicate`)
            field_set (list): If provided will only deduplicate on list of fields provided

        Returns:
            None: Nothing returned. Updates `final` object

        """
        # first determine if this object has been seen before
        DeDupCollection = ioc.getCollection(collection)
        t1test = obj
        t1test['grease_internal_configuration'] = configuration_name
        T1Hash = DeDupCollection.find_one({'hash': Deduplication.generate_hash_from_obj(t1test)})
        if T1Hash:
            # T1 Found Protocol: We have found a fully duplicate object
            # we have a duplicate source document
            # increase the counter and expiry and move on (DROP)
            ioc.getLogger().debug("Type1 Match found for object", verbose=True)
            # bump the expiry time and move on
            DeDupCollection.update_one(
                {'_id': T1Hash['_id']},
                {
                    "$set": {
                        'score': int(T1Hash['score']) + 1,
                        'expiry': Deduplication.generate_expiry_time(expiry)
                    }
                }
            )
            return
        else:
            # T1 Not Found Protocol: We have a possibly unique object
            ioc.getLogger().debug("Type1 Match not found; Beginning type 2 processing")
            # Create a T1
            T1ObjectId = DeDupCollection.insert_one({
                'expiry': Deduplication.generate_expiry_time(int(expiry)),
                'grease_internal_configuration': configuration_name,
                'max_expiry': Deduplication.generate_max_expiry_time(int(expiry_max)),
                'type': 1,
                'score': 1,
                'source': str(source_name),
                'hash': Deduplication.generate_hash_from_obj(t1test)
            }).inserted_id
            # Begin T2 Deduplication
            compositeScore = Deduplication.object_field_score(
                collection, ioc, source_name, configuration_name, obj, str(T1ObjectId), expiry, expiry_max, field_set
            )
            if compositeScore < threshold:
                # unique obj
                ioc.getLogger().trace(
                    "Unique object! Composite score was: [{0}] threashold: [{1}]".format(compositeScore, threshold),
                    verbose=True
                )
                final.append(obj)
                return
            else:
                # likely duplicate value
                ioc.getLogger().trace(
                    "Object surpassed threshold, suspected to be duplicate! "
                    "Composite score was: [{0}] threashold: [{1}]".format(compositeScore, threshold),
                    verbose=True
                )
                return

    @staticmethod
    def object_field_score(collection, ioc, source_name, configuration_name, obj, objectId, expiry, max_expiry, field_set=None):
        """Returns T2 average uniqueness

        Takes a dictionary and returns the likelihood of that object being unique based on data in the collection

        Args:
            collection (str): Deduplication collection name
            ioc (GreaseContainer): IoC Access
            source_name (str): source of data to be deduplicated
            configuration_name (str): configuration name to be deduplicated
            obj (dict): Single dimensional list to be compared against collection
            objectId (str): T1 Hash Mongo ObjectId to be used to associate fields to a T1
            expiry (int): Hours for deduplication to wait before removing a field if not seen again
            max_expiry (int): Days for deduplication to wait before ensuring object is deleted
            field_set (list, optional): List of fields to deduplicate with if provided. Else will use all keys

        Returns:
            float: Duplication Probability

        """
        # generate field list if not provided
        FieldColl = ioc.getCollection(collection)
        if not isinstance(field_set, list) or len(field_set) <= 0:
            field_set = obj.keys()
        # List to hold field level scores
        field_scores = []
        # iterate over the field set
        for field in field_set:
            # ensure key is in the object
            ioc.getLogger().trace("Starting field [{0}]".format(field), verbose=True)
            if field in obj:
                if isinstance(obj.get(field), bytes):
                    value = obj.get(field).decode('utf-8', 'ignore')
                else:
                    value = obj.get(field)
                T2Object = {'source': source_name, 'field': field, 'value': value, 'configuration': configuration_name}
                checkDoc = FieldColl.find_one({'hash': Deduplication.generate_hash_from_obj(T2Object)})
                if checkDoc:
                    # we found a 100% matching T2 object
                    ioc.getLogger().trace("T2 object Located", trace=True)
                    update_statement = {
                        "$set": {
                            'score': int(checkDoc['score']) + 1,
                            'expiry': Deduplication.generate_expiry_time(expiry)
                        }
                    }
                    FieldColl.update_one(
                        {'_id': checkDoc['_id']},
                        update_statement
                    )
                    field_scores.append(100)
                    continue
                else:
                    # We have a possible unique value
                    ioc.getLogger().trace("T2 object not found", trace=True)
                    # generate a list to collect similarities to other field objects
                    fieldProbabilityList = []
                    for record in FieldColl.find({'source': source_name, 'configuration': configuration_name, 'field': field, 'type': 2})\
                            .sort('score', pymongo.ASCENDING).limit(100):
                        if Deduplication.string_match_percentage(record['value'], str(T2Object['value'])) > .95:
                            # We've found a REALLY strong match
                            # Set this field's score to that of the match
                            field_scores.append(
                                100 * Deduplication.string_match_percentage(record['value'], str(T2Object['value']))
                            )
                            # leave the for loop for this field since we found a highly probable match
                            break
                        else:
                            fieldProbabilityList.append(
                                100 * Deduplication.string_match_percentage(record['value'], str(T2Object['value']))
                            )
                    if fieldProbabilityList:
                        # We have at least one result
                        score = float(sum(fieldProbabilityList) / len(fieldProbabilityList))
                        ioc.getLogger().trace("Field Score [{0}]".format(score), verbose=True)
                        field_scores.append(score)
                    else:
                        # It is a globally unique field
                        field_scores.append(0)
                    # finally persist the new object
                    T2Object['hash'] = Deduplication.generate_hash_from_obj(T2Object)
                    T2Object['score'] = 1
                    T2Object['expiry'] = Deduplication.generate_expiry_time(expiry)
                    T2Object['max_expiry'] = Deduplication.generate_max_expiry_time(max_expiry)
                    T2Object['type'] = 2
                    T2Object['parentId'] = ObjectId(objectId)
                    FieldColl.insert_one(T2Object)
            else:
                ioc.getLogger().warning("field [{0}] not found in object".format(field), trace=True, notify=False)
                continue
        if len(field_scores) is 0:
            return 0.0
        else:
            return float(sum(field_scores) / float(len(field_scores)))

    @staticmethod
    def generate_hash_from_obj(obj):
        """Takes an object and generates a SHA256 Hash of it

        Args:
            obj (object): Hashable object ot generate a SHA256

        Returns:
            str: Object Hash

        """
        return hashlib.sha256(str(obj).encode('utf-8')).hexdigest()

    @staticmethod
    def generate_expiry_time(hours):
        """Generates UTC Timestamp for hours in the future

        Args:
            hours (int): How many hours in the future to expire on

        Returns:
            datetime.datetime: Datetime object for hours in the future

        """
        return datetime.datetime.utcnow() + datetime.timedelta(hours=int(hours))

    @staticmethod
    def generate_max_expiry_time(days):
        """Generates UTC Timestamp for hours in the future

        Args:
            days (int): How many days in the future to expire on

        Returns:
            datetime.datetime: Datetime object for days in the future

        """
        return datetime.datetime.utcnow() + datetime.timedelta(days=int(days))

    @staticmethod
    def string_match_percentage(constant, new_value):
        """Returns the percentage likelihood two strings are identical

        Args:
            constant (str): Value to use as base standard
            new_value (str): Value to compare `constant` against

        Returns:
            float: Percentage likelihood of duplicate value

        """
        return difflib.SequenceMatcher(lambda x: x == " ", constant, new_value).quick_ratio()

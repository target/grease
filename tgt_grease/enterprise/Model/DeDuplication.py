from tgt_grease.core import GreaseContainer
from psutil import virtual_memory, cpu_percent
import threading


class Deduplication(object):
    """Responsible for Deduplication Operations

    Attributes:
        ioc (GreaseContainer): IoC access for DeDuplication

    """

    def __init__(self, ioc):
        if isinstance(ioc, GreaseContainer):
            self.ioc = ioc
        else:
            self.ioc = GreaseContainer()

    def Deduplicate(self, data, source, strength, expiry_hours, expiry_max, collection, field_set=None):
        """Deduplicate data

        This method will deduplicate the `data` object to allow for only unique objects to be returned. The collection
        variable will be the collection deduplication data will be stored in

        Args:
            data (list[dict]): **list or single dimensional dictionaries** to deduplicate
            source (str): Source of data being deduplicated
            strength (float): Strength of deduplication (higher is more unique)
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
            "Starting deduplication from data source [{0}] total records to parse [{0}]".format(source, len(data)),
            trace=True
        )
        # now comes James' version of machine learning. I call it "Blue Collar Machine Learning"
        # Pointer to access items in the list
        data_pointer = 0
        # Max Length
        data_max = len(data)
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
            if not isinstance(source[data_pointer], dict):
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
                    strength,
                    source,
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
        self.ioc.getCollection(collection).create_index([('expiry', 1), ('expireAfterSeconds', 1)])
        self.ioc.getCollection(collection).create_index([('max_expiry', 1), ('expireAfterSeconds', 1)])
        return final

    @staticmethod
    def deduplicate_object(ioc, obj, expiry, expiry_max, strength, source_name, final, collection, data_pointer=None, data_max=None, field_set=None):
        """DeDuplicate Object

        This is the method to actually deduplicate an object. The `final` argument is appended to with the obj if it
        was successfully deduplicated.

        Args:
            ioc (GreaseContainer): IoC for the instance
            obj (dict): Object to be deduplicated
            expiry (int): Hours to deduplicate for
            expiry_max (int): Maximum days to deduplicate for
            strength (float): Uniqueness Measurement
            source_name (str): Source of data being deduplicated
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

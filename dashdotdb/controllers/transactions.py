import threading

from uuid import uuid4

open_transactions = {}
transaction_lock = threading.Lock()


def add_to_transaction(transaction_id, obj):
    with transaction_lock:
        if transaction_id in open_transactions:
            open_transactions[transaction_id].append(obj)
        else:
            # maybe return an error here instead?
            open_transactions[transaction_id] = [obj]


def post(transactionid):
    # complete the transaction for the provided transaction id
    if transactionid in open_transactions:
        transactions = []
        with transaction_lock:
            transactions = open_transactions[transactionid]
            del open_transactions[transactionid]

        # write the data to db
        for obj in transactions:
            obj.insert()
        return 'transaction committed'
    return 'transaction id unknown', 404


def get():
    # generate a unique id
    uuid = str(uuid4())
    open_transactions[uuid] = []
    return uuid

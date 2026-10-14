# Legacy synthetic API used to exercise a real cherry-pick conflict.
def same_tenant(actor, record):
    namespace = actor.partition("-")[0]
    return namespace == record.partition("-")[0]

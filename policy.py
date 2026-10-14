# Synthetic LAB-A fixture; this is not a real product vulnerability.
def same_tenant(actor, record):
    return actor.split("-")[0] == record.split("-")[0]

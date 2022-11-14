from src.bpl_datastore import EnhancedBib
from src.db_access import session_scope, delete_instances


def delete_bib(bibNo: int) -> str:
    """
    Deletes row in bpl_db for given bib number.

    Args:
            bibNo:          8-digit bib number without a prefix or last digit check

    Returns:
            operation outcome
    """
    with session_scope("./src/bpl_db.db") as session:
        result = delete_instances(session, EnhancedBib, bibNo=bibNo)
        return f"Deleted {result} rows."


def delete_ocn(ocn: int) -> str:
    """
    Deletes row in bpl_db for given oclc number.

    Args:
        ocn:                oclc number without a prefix

    Returns:
        operation outcome
    """
    with session_scope("./src/bpl_db.db") as session:
        result = delete_instances(session, EnhancedBib, oclcNo=ocn)
        return f"Deleted {result} rows."

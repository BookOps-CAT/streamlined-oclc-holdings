import csv
import json
import os

from bookops_bpl_solr import SolrSession

from utils import save2csv


def get_creds():
    fh = os.path.join(os.getenv("USERPROFILE"), ".bpl-solr/bpl-solr-general-prod.json")
    with open(fh, "r") as f:
        creds = json.load(f)
        return creds


def get_bibNos(src_fh: str):
    """
    Generator. Reads a csv file with Sierra bib numbers and yields one
    id at a time
    """
    with open(src_fh, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            try:
                yield row[0]
            except IndexError:
                continue


def find_ocnNo(session, bibNo):
    response = session.search_bibNo(
        bibNo,
        default_response_fields=False,
        response_fields="id,title,ss_marc_tag_001",
    )
    data = response.json()
    if data["response"]["numFound"] == 1:
        try:
            controlNo = data["response"]["docs"][0]["ss_marc_tag_001"]
            if controlNo.startswith("oc") or controlNo.startswith("on"):
                return controlNo

            else:
                return None

        except KeyError:
            return None
    else:
        return None


def has_duplicate(session, ocnNo):
    # check if existing record is suppressed or matches on bibNo?
    response = session.search_controlNo(ocnNo)
    if response.json()["response"]["numFound"] > 1:
        return True
    else:
        return False


def query_solr(src_fh: str, out_fh: str):
    creds = get_creds()
    with SolrSession(
        authorization=creds["client_key"], endpoint=creds["endpoint"]
    ) as session:
        for bibNo in get_bibNos(src_fh):
            ocn = find_ocnNo(session, bibNo)
            if ocn is not None:
                duplicate = has_duplicate(session, ocn)
                if not duplicate:
                    save2csv(out_fh, [bibNo, ocn])


def test_bibNo(bibNo: str):
    creds = get_creds()
    with SolrSession(
        authorization=creds["client_key"], endpoint=creds["endpoint"]
    ) as session:
        response = session.search_bibNo(
            bibNo,
            default_response_fields=False,
            response_fields="id,title,ss_marc_tag_001",
        )
        print(response.json())


def test_ocn(ocn: str):
    creds = get_creds()
    with SolrSession(
        authorization=creds["client_key"], endpoint=creds["endpoint"]
    ) as session:
        response = session.search_controlNo(
            ocn,
            default_response_fields=False,
            response_fields="id,title,ss_marc_tag_001",
        )
        print(response.json())


if __name__ == "__main__":
    src_fh = os.path.join(
        os.getenv("USERPROFILE"), "Desktop\\Temp\\BLW-Q-220329_ERRlog.csv"
    )
    # query_solr(src_fh, "./files/BPL/ocn-for-deletion.csv")
    test_ocn("ocm62267545")
    # test_bibNo("b120312116")

import sys
import argparse


from src.bpl_ingest import select_for_sierra_list_creation, parse_sierra_bib
from src.bpl_delete import delete_bib, delete_ocn
from src.enhance import launch_bpl_enhancement


def main(args: list) -> None:
    """
    launches enrichment of local records from CLI.
    """
    parser = argparse.ArgumentParser(
        prog="EnrichBib",
        description="Enriches local bibs with Worldcat metadata based on the OCLC Streamlined Holdings project.",
    )

    parser.add_argument(
        "library", help="'BPL' or 'NYPL'", type=str, choices=["BPL", "NYPL"]
    )

    parser.add_argument(
        "action",
        help=(
            "'select2enrich' selects a batch of records for enrichment and "
            "results in a list of Sierra bib number to be used to create a "
            "list of records in Sierra, 'enrich' uses exported from "
            "Sierra MARC records and runs enrichment process.; "
            "'enrich-resume' resumes interrupted process"
        ),
        type=str,
        choices=["select2enrich", "enrich", "enrich-resume", "delete"],
    )

    parser.add_argument(
        "--volume",
        help="size of batch for processing",
        type=int,
        nargs="?",
        default=5000,
    )
    parser.add_argument(
        "--bibno",
        help="eight digit bib number without 'b' prefix and last digit check to be deleted",
        type=int,
        nargs="?",
        default=0,
    )
    parser.add_argument(
        "--ocn",
        help="OCN number without a prefix to be deleted",
        type=int,
        nargs="?",
        default=0,
    )

    pargs = parser.parse_args(args)

    if pargs.library == "BPL":
        if pargs.action == "select2enrich":
            print(f"Selecting {pargs.volume} BPL bibs for processing...")
            out_fh = select_for_sierra_list_creation(pargs.volume)
            print(f"Created a file with Sierra bib numbers to use: {out_fh}")
        elif pargs.action == "enrich":
            print("Parsing prepared MARC file...")
            parse_sierra_bib()
            print("Obtaining Worldcat records...")
            launch_bpl_enhancement()
        elif pargs.action == "enrich-resume":
            print("Resuming enrichment...")
            launch_bpl_enhancement()
        elif pargs.action == "delete":
            if pargs.bibno:
                print(f"Deleting b{pargs.bibno}a from the database.")
                result = delete_bib(pargs.bibno)
                print(result)
            elif pargs.ocn:
                print(f"Deleting OCN {pargs.ocn} from the database.")
                result = delete_ocn(pargs.ocn)
                print(result)

    elif pargs.library == "NYPL":
        print("Workflow not implemented yet. Exiting...")


if __name__ == "__main__":
    main(sys.argv[1:])

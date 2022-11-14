# streamlined-oclc-holdings
Scripts supporting OCLC streamlined holdings project and its follow up work, such as incorporating matched OCN numbers into local bibs (NYPL) and full enhancement of local bibs with Worldcat records (BPL).

## Enhancing BPL Sierra records (full matching process only)
Legacy and vendor records (not WorldCat records) will benefit from enhancement: bringing matching record from WorldCat to overlay Sierra bib.
Full matching process of the OCLC Streamlined Holdings service provides reports that can be used to identify bibs that benefit from such enrichment.

OCLC reports have been parsed and incorporated into `bpl_db.db` SQLite database. This store servers as a reference point for all work related to record enrichment.
Enhancement scripts read a batch of a given size from the `bpl_db.db` and produce list of Sierra bib numbers that can be used to create a list of records in Sierra.
Exported MARC bibs based on such list are then parsed and their data incorporated into downloaded Worldcat records, so no important local information is lost in the process.

Obtained records must be manipulated before the import:
+ unsupported subject headings must be removed
+ deleted certain fields (019, 029, 263, 938, etc.)
+ ISBNs on Worldcat record must be replaced with ISBNs taken from local bib
+ added import command tag (949) with proper Sierra format and OPAC display codes


Enriched with WorldCat metadata records are loaded to Sierra using local Overload NEW load table. Overlaid records require removal of 948 tag with "MARS" value to be picked by a authority control routine. This happens automatically since the 948 field is not protected by the NEW load table.

The enhancement process should include sending resulting records to authority work vendor to update their base file. This step is important because otherwise we run into a problem of the newly enriched records being overlaid by older version of bib in vendor's base file (BPL in quarterly update).


#### Procedure step-by-step guide
1. Activate virtual environment:
	+ navigate to repo main directory
	+ run
	bash: 
	```
	source ./.venv/scripts/activate
	``` 
	or CMD:
	```
	.venv/scripts/activate
	```
	or any other method to activate project's virtual environment
2. Select records for processing:
	+ run the following command: 
	```
	python run.py BPL select2enrich 5000
	``` 
	where the last argument is size of the batch (5k records in the above example)
	+ the script produces a file with Sierra bib numbers for processing in the `Documents` directory: `bpl-batch2enrich-[YYMMDD]-sierra-nos.csv`
3. Provide relevant Sierra MARC records:
	+ using `\Documents\bpl-batch2enrich-[YYMMDD]-sierra-nos.csv` create a list in Sierra (use 'import records' feature and upload bib numbers from the file)
	+ export MARC records using Data Exchange and "out" export table, use following naming convention: bpl-batch2enrich-[YYMMDD].out and save it into the `Documents` directory
	+ note and delete from `bpl_db.db` any records that have been deleted from Sierra
	(in the Sierra List deleted bibs appear on top as empty rows, double-clicking allows to look up bib number of the deleted record)

4. Get Worldcat records for selected batch
	+ run the following command in CLI:
	```bash
	python run.py BPL enrich
	```
	+ requires WorldCat Metadata API credentials
	+ uses `\Documents\bpl-batch2enrich-[YYMMDD].out` file to obtain local data to be incorporated into final enriched records
	+ outputs obtained records to `\Documents\bpl-enriched-[yymmdd].mrc`
		+ replaces ISBNs found on Worldcat record with local ones
		+ adds the 907 tag with Sierra bib number to use as a match point in the overlay process
		+ removes following fields: 019, 029, 263, 938
		+ adds 949 with command to set proper Sierra bib format and OPAC Display code
	+ only records present in the `bpl-batch2enrich-[YYMMDD].out` will be processed
	+ if enrichment process get interrupted (for example, OCLC service times out, or returns an error) it can be resumed using the following command:
	```
	python run.py BPL enrich-resume
	```
	+ if OCLC service returns 404 HTTP error (not found) for a given OCN number, the row in bpl database must be deleted:

	error example:
	```
	requests.exceptions.HTTPError: 404 Client Error: Not Found for url: https://worldcat.org/bib/data/1330292752
	```
	Use the following command to delete a row with given OCN:
	```
	python run.py BPL delete --ocn 1330292752
	```

5. Load enriched records to Sierra:
	+ use "Load Overload NEW" load table
	+ occasionally, bibs get deleted from Sierra and during loading of the file you may see error messages indicating such bib numbers. In this case delete that bib from bpl database using the following command (8 digit number):
	```
	python run.py delete --bibno 10962655
	```
6. Create a Backstage list of newly loaded records and submit them for authority processing:
	+ use the same list that was utilized to create MARC records for enrichment
	+ output a MARC file for Backstage processing using export table "out" and name the file using following convention: BLW-GAP-[YYMMDD].out`
	+ follow directions outlined [here](https://docs.google.com/document/d/13EXSuZ8QVWnvwSxzYgTeQteNoFaQWqxJC6K-lyxL6DQ/edit#heading=h.mcwvej88gk8g) to upload and import processed by Backstage files
	+ do not start Backstage job while any regular MAX job is in process!
7. Record enrichment and authority work numbers for statistical purposes ([sheet](https://docs.google.com/spreadsheets/d/1fbVGzfgoG2-RTR_q0oeRlJltnzaDMCBxLL49sdOlLyE))
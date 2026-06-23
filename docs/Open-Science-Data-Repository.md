# Open Science Data Repository Public API

> **In plain terms:** Access to NASA's space-biology and life-sciences research data. Search studies, pull downloadable file lists, and fetch full metadata — plus related records like experiments, missions, payloads, and hardware.

NASA OSDR provides a RESTful Application Programming Interface (API) to its full-text search, data file retrieval, and metadata retrieval capabilities. The API provides a choice of standard web output formats, either JavaScript Object Notation (JSON) or Hyper Text Markup Language (HTML), of query results. The Data File API returns metadata on data files associated with dataset(s), including the location of these files for download via https. The Metadata API returns entire sets of metadata for input study dataset accession numbers. The Search API can be used to search dataset metadata by keywords and/or metadata. It can also be used to provide search of three other omics databases: the National Institutes of Health (NIH) / National Center for Biotechnology Information's (NCBI) Gene Expression Omnibus (GEO); the European Bioinformatics Institute's (EBI) Proteomics Identification (PRIDE); the Argonne National Laboratory's (ANL) Metagenomics Rapid Annotations using Subsystems Technology (MG-RAST).

In addition to study datasets, NASA OSDR also hosts metadata for 7 other data types: experiments, payloads, subjects, biospecimens, missions, vehicles, and hardware. The API for these data types is listed separately and uniform throughout, to make for easy metadata exploration.

## Study

### Study Data File API

**Syntax**

```
https://osdr.nasa.gov/osdr/data/osd/files/{OSD_STUDY_IDs}/?page={CURRENT_PAGE_NUMBER}&size={RESULTS_PER_PAGE}?all_files={ALL_FILES}
```

**Returns: JSON-formatted response**

| Parameters | Data Type | Notes | Values | Required |
|------------|-----------|-------|--------|----------|
| {OSD_STUDY_IDs} | Integer or Decimal | Comma separated list with mixture of single OSD accession numbers and ranges. Use single decimal numbers to indicate a specific study version (Ex: 4.1 would be OSD-4, version 1). | ex. 87-95,137,153.2 | Yes |
| {CURRENT_PAGE_NUMBER} | Integer | Current page number in pagination | Starts from 0 | No |
| {RESULTS_PER_PAGE} | Integer | Number of results returned per page in pagination | Max 25 results per page | No |
| {ALL_FILES} | Boolean | Include hidden files. true to include invisible files; false to exclude. Default value is false. | true or false | No |

**Example requests:**

- Single study request using study accession number
  - `https://osdr.nasa.gov/osdr/data/osd/files/87`
- Multiple studies request using combination of range and comma separated list
  - `https://osdr.nasa.gov/osdr/data/osd/files/137,87-95,13,20-50`

**Note:**

The study_files element in the JSON response has the remote_url attribute, which can be used to obtain the specific download URL for the file by prefacing with the OSDR data server address, https://osdr.nasa.gov . In the example query/response below, the first study file for OSD-87 (version 1) study in the response below can be downloaded from `https://osdr.nasa.gov/geode-py/ws/studies/OSD-87/download?source=datamanager&file=GLDS-87_metadata_Zanello_STS135-ISA.zip`

**Multiple Study Data Files Request:**

Example: `https://osdr.nasa.gov/osdr/data/osd/files/137.1,86-87`

### Study Metadata API

**Syntax**

```
https://osdr.nasa.gov/osdr/data/osd/meta/{OSD_STUDY_ID}
```

| Parameters | Data Type | Notes | Values | Required |
|------------|-----------|-------|--------|----------|
| {OSD_STUDY_ID} | Integer | Single study accession number | Example: 87 | Yes |

**Single Study Metadata Request:**

Example: `https://osdr.nasa.gov/osdr/data/osd/meta/137`

### Study Dataset Search API

**Syntax 1 (returns JSON response)**

```
https://osdr.nasa.gov/osdr/data/search?<PARAMETER-LIST>
```

| parameters | definition | values |
|------------|------------|--------|
| term | search keyword | string |
| from | starting page | integer (single value) |
| size | search result display count | integer (single value) |
| type | datasource | cgene , nih_geo, ebi_pride, mg_rast (accepts multiple value separated by comma separated) |
| sort | sort field | string (Field Name) |
| order | sort order | ASC - ascending order; DESC - descending order |
| ffield | filter field | string (should always be pared with fvalue); append .raw to the end of the field to use the exact match index; see table below for possible filter field values and example filter value pairings |
| fvalue | filter value | string (should always be pared with ffield) |

| Filter Field (Case Sensitive) | Example Filter Value |
|-------------------------------|----------------------|
| Accession | OSD-4 |
| Acknowledgments | NASA JPL |
| Authoritative Source URL | OSD-4 |
| Data Source Accession | GSE18388 |
| Data Source Type | cgene |
| Experiment Platform | Animal Enclosure Module |
| Flight Program | Shuttle |
| links | GPL13112 |
| Managing NASA Center | Ames Research Center |
| Material Type | thymus |
| organism | Mus musculus |
| Project Identifier | NNA04CC97G |
| Project Link | `https://taskbook.nasaprs.com/tbp/index.cfm?action=public_query_taskbook_content&TASKID=7191` |
| Project Title | Vector-Averaged Gravity |
| Project Type | Spaceflight |
| Space Program | NASA |
| Study Assay Measurement Type | transcription profiling |
| Study Assay Technology Platform | Affymetrix |
| Study Assay Technology Type | DNA microarray |
| Study Description | Murine Thymus Tissue |
| Study Factor Name | Spaceflight |
| Study Factor Type | Space Flight |
| Study Funding Agency | NNA04CC97G |
| Study Identifier | OSD-4 |
| Study Protocol Description | thymus tissue |
| Study Protocol Name | sample collection |
| Study Protocol Type | sample collection |
| Study Public Release Date | 1268179200 |
| Study Publication Author List | Gruener R |
| Study Publication Title | spaceflown murine thymus tissue |
| Study Title | Space-flown Murine Thymus Tissue |

POST and GET requests accept the URL encoded name/value pairs for submission

Examples:

- `https://osdr.nasa.gov/osdr/data/search?term=space&from=0&type=cgene,nih_geo_gse&ffield=links&fvalue=GPL16417&ffield=Data%20Source%20Accession.raw&fvalue=GSE82255`
- `https://osdr.nasa.gov/osdr/data/search?ffield=organism&fvalue=Homo%20sapiens&ffield=Study%20Assay%20Technology%20Type&fvalue=RNA%20Sequencing`

**Syntax 2 (returns HTML response):**

Format: `https://osdr.nasa.gov/bio/repo/search?q=<SEARCH-TERMS>&data_source=<DATA-SOURCE>`

| Parameters | Values | Usage |
|------------|--------|-------|
| SEARCH-TERMS | text | Any text to search for, can be augmented by the keywords: AND - ALL search terms must be present (default boolean search); OR - ANY of your search terms can be present; NOT - exclude words from your search. If no conjunctive or disjunctive operator specified, the default is "AND" |
| DATA-SOURCE | cgene, nih_geo_gse, ebi_pride, mg_rast | cgene - Search authoritative data records in NASA Open Science Data Repository; nih_geo_gse - Search authoritative data records in NIH Gene Expression Omnibus database; ebi_pride - Search authoritative data records in the European Bioinformatics Institute Proteomics Identification database; mg_rast - Search authoritative data records in the Metagenomic Rapid Annotations using Subsystems Technology database |

Examples:

- `https://osdr.nasa.gov/bio/repo/search?q=cancer&data_source=cgene`
- `https://osdr.nasa.gov/bio/repo/search?q=mouse%20AND%20liver&data_source=cgene`

## Experiments, Missions, Payloads, Hardware, Vehicles, Subjects, Biospecimens

### Format:

Experiments, Missions, Payloads, Hardware, Vehicles, Subjects, and Biospecimens follow the same API format. The "All" call returns a list of all objects within that data type, while the "Single" call returns an expanded version of a specific object. The endpoint for any single object can be selected from the "All" call. Some objects may include links to other objects within the API, such as a vehicle within a mission.

- **Experiment:**
  - All: `https://osdr.nasa.gov/geode-py/ws/api/experiments`
  - Single: `https://osdr.nasa.gov/geode-py/ws/api/experiment/` + identifier
- **Mission:**
  - All: `https://osdr.nasa.gov/geode-py/ws/api/missions`
  - Single: `https://osdr.nasa.gov/geode-py/ws/api/mission/` + identifier
- **Payload:**
  - All: `https://osdr.nasa.gov/geode-py/ws/api/payloads`
  - Single: `https://osdr.nasa.gov/geode-py/ws/api/payload/` + identifier
- **Hardware:**
  - All: `https://osdr.nasa.gov/geode-py/ws/api/hardware`
  - Single: `https://osdr.nasa.gov/geode-py/ws/api/hardware/` + identifier
- **Vehicle:**
  - All: `https://osdr.nasa.gov/geode-py/ws/api/vehicles`
  - Single: `https://osdr.nasa.gov/geode-py/ws/api/vehicle/` + identifier
- **Subject:**
  - All: `https://osdr.nasa.gov/geode-py/ws/api/subjects`
  - Single: `https://osdr.nasa.gov/geode-py/ws/api/subject/` + identifier
- **Biospecimen:**
  - All: `https://osdr.nasa.gov/geode-py/ws/api/biospecimens`
  - Single: `https://osdr.nasa.gov/geode-py/ws/api/biospecimen/` + identifier

### Examples:

**Single Vehicle Call**

From the above example, we can see a vehicle endpoint which directs us to the vehicle linked to SpaceX-12.

`https://osdr.nasa.gov/geode-py/ws/api/vehicle/Dragon`

## API Requests with Python

### Basic API Request

For basic API requests, the requests python library can be used. Install the library with the command:

```
pip install requests
```

We can use the requests libray to make API calls to any of the endpoints above. The python code below shows the exact commands needed to read the API endpoints that return JSON. Replace API_ENDPOINT_HERE with any API endpoint that returns JSON, as in the example.

```python
import requests
response = requests.get("API_ENDPOINT_HERE").json()
# Example:
response = requests.get("https://osdr.nasa.gov/osdr/data/osd/files/87").json()
```

## Resources

For more information on making API requests with python, visit [https://www.dataquest.io/blog/python-api-tutorial/](https://www.dataquest.io/blog/python-api-tutorial/).

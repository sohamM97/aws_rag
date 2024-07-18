from uuid import uuid4

import boto3
from constants import COLLECTION_NAME, INDEX_NAME
from opensearchpy import OpenSearch, RequestsHttpConnection
from pypdf import PdfReader
from requests_aws4auth import AWS4Auth
from upload import BUCKET_NAME, upload_file

FILE_NAME = "11-backgroundchecks disclosure form.pdf"


s3_url = upload_file(file_name=FILE_NAME, bucket=BUCKET_NAME)

service = "aoss"
region = "us-east-1"
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    region,
    service,
    session_token=credentials.token,
)

aoss_client = boto3.client("opensearchserverless")
response = aoss_client.batch_get_collection(names=[COLLECTION_NAME])
host = response["collectionDetails"][0]["collectionEndpoint"].replace("https://", "")

# Build the OpenSearch client
opensearch_client = OpenSearch(
    hosts=[{"host": host, "port": 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    timeout=300,
)

if FILE_NAME.endswith(".pdf"):
    content = ""
    reader = PdfReader(FILE_NAME)
    for i in range(len(reader.pages)):
        page = reader.pages[i]
        content += page.extract_text()
else:
    with open(FILE_NAME) as f:
        content = f.read()

response = opensearch_client.index(
    index=INDEX_NAME,
    body={
        "id": uuid4(),
        "project_uuid": uuid4(),
        "filename": FILE_NAME,
        "content": content,
        "sourcepage": FILE_NAME,
        "sourcefilepath": s3_url,
        "language": "english",
        "tags": [1, 2, 3],
        "embedding": [1, 2, 3],
    },
)
print("\nDocument added:")
print(response)
import os
import requests
import xml.etree.ElementTree as ET


# change these
collection_id = "COLLECTION_ID"
doc_id = "DOC_ID"

username = "USER_EMAIL"
password = "USER_PWD"

status = "IN_PROGRESS" 

login_url = 'https://transkribus.eu/TrpServer/rest/auth/login'
fulldoc_url = 'https://transkribus.eu/TrpServer/rest/collections/{}/{}/fulldoc'
update_page_xml_url = 'https://transkribus.eu/TrpServer/rest/collections/{}/{}/{}/text'
all_docs_in_collection_url = 'https://transkribus.eu/TrpServer/rest/collections/{}/list'

def login_transkribus(username, password):
    """
    Logs in to the Transkribus API using the provided credentials.

    Args:
        username (str): Your Transkribus account username (email).
        password (str): Your Transkribus account password.

    Returns:
        str: The session ID upon successful login.

    Raises:
        Exception: If the login fails, an exception is raised with the error details.
    """
    response = requests.post(login_url, data={'user': username, 'pw': password})
    if response.status_code == 200:
        root = ET.fromstring(response.text)
        session_id = root.find('sessionId').text
        return session_id
    else:
        raise Exception(f"Login failed: {response.status_code} - {response.text}")


def get_full_document(session_id, collection_id, doc_id):

    headers = {'Cookie': f"JSESSIONID={session_id}"}
    response = requests.get(fulldoc_url.format(collection_id, doc_id), headers=headers)
   
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to retrieve document: {response.status_code} - {response.text}")

def load_xml(xml_path):

    if os.path.exists(xml_path):
        with open(xml_path, 'r', encoding='UTF-8') as xml_file:
            return xml_file.read()
    else:
        return None

def update_page_xml(session_id, collection_id, doc_id, page_nr, xml_content, status="IN_PROGRESS", overwrite=True):
    """Updates the XML for a specific page."""
    headers = {'Cookie': f"JSESSIONID={session_id}", 'Content-Type': 'application/xml'}
    params = {'status': status, 'overwrite': str(overwrite).lower()}  # true or false as lowercase string
    
    response = requests.post(update_page_xml_url.format(collection_id, doc_id, page_nr), headers=headers, params=params, data=xml_content)

    if response.status_code == 200:
        print(f"Page {page_nr} XML updated successfully.")
    else:
        print(xml_content)
        print(f"Failed to update XML for page {page_nr}: {response.status_code} - {response.text}")

def batch_update_document_xmls(base_dir, collection_id):
    """Updates the XML for multiple documents in a base directory."""
  
    session_id = login_transkribus(username, password)
    headers = {'Cookie': f"JSESSIONID={session_id}"}
    response = requests.get(all_docs_in_collection_url.format(collection_id), headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to retrieve documents in collection: {response.status_code} - {response.text}")

    all_docs = response.json()
    
    for doc in all_docs:
        doc_id = doc['docId']
        doc_title = doc['title']
        print(base_dir)
        metadata_file = os.path.join(base_dir, doc_title, "metadata.xml")
        
        if os.path.exists(metadata_file):
            tree = ET.parse(metadata_file)
            root = tree.getroot()
            
            metadata_doc_id = root.findtext('docId')
            
            if metadata_doc_id == str(doc_id):
                print(f"Updating document {doc_title} with ID {doc_id}")
                document = get_full_document(session_id, collection_id, doc_id)
                pages = document['pageList']['pages']
                
                for page in pages:
                    page_nr = page['pageNr']
                    page_filename = page['imgFileName']
                    xml_path = None
                    
                    for filename in os.listdir(os.path.join(base_dir, doc_title, "page")):
                        if filename[5:-4] == page_filename[:-4] and filename.endswith(".xml"):
                            xml_path = os.path.join(base_dir, doc_title, "page", filename)
                    
                    if xml_path:
                        xml_content = load_xml(xml_path)
                        if xml_content:
                            update_page_xml(session_id, collection_id, doc_id, page_nr, xml_content.encode("utf-8"), status=status, overwrite=True)
                        else:
                            print(f"Failed to load XML content for page {page_nr}.")
                    else:

                        print(f"No matching PageXML found for page {page_nr} in document {doc_title}.")
            else:
                print(f"Metadata docId {metadata_doc_id} does not match document {doc_id}. Skipping...")
        else:
            print(f"Could not find metadata.xml for document {doc_title}. Skipping...")

if __name__ == "__main__":

    base_dir = r'/PATH/TO/BASE/DIRECTORY'
    doc_dir = r'PATH/TO/DOC'

    batch_update_document_xmls(base_dir, collection_id)
    #update_page_xml(doc_dir, collection_id, doc_id)

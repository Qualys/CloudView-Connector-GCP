# Author: Sadanand Nerurkar/Sean Nicholson
# Purpose: Onboard GCP PRoject Connectors to Qulays CloudView
# version: 1.0.0
# date: 05.28.2021


from google.cloud import resource_manager
import yaml, json, requests, base64, getpass, csv, os, logging, sys
from requests.exceptions import HTTPError
from os.path import split
import logging.config

# Lists to evaluate
List_Of_GCP_Projects = []
List_of_GCP_Connectors_in_Qualys = []
Connectors_to_be_added_to_Qualys = []

def Password():
    global Qualys_Password
    try:
        Qualys_Password = getpass.getpass(prompt='Qualys Password: ')
    except Exception as error:
        logger.error(f'Password Error: {error}')
    return Qualys_Password

def config():
    global username, baseurl, keyfile1, keyfile2, projects
    with open('./config/config.yml', 'r') as config_settings:
        config_info = yaml.load(config_settings, Loader=yaml.SafeLoader)
        username = str(config_info['defaults']['QualysUsername']).rstrip()
        baseurl = str(config_info['defaults']['Baseurl']).rstrip()
        keyfile1 = str(config_info['defaults']['GcpApiKey']).rstrip()
        keyfile2 = str(config_info['defaults']['ConnectorCreationJson']).rstrip()
        projects = str(config_info['defaults']['Projects']).rstrip()
        if username == '' or baseurl == '' or keyfile1 == '' or keyfile2 == '' or projects == '':
            logger.info(f'Please configure ./config.yml File correctly. Exiting...')
            sys.exit(1)
    return username, baseurl, keyfile1, keyfile2, projects

def setup_logging(default_path='./config/logging.yml', default_level=logging.INFO, env_key='LOG_CFG'):
    """Set up Logging Configuration"""
    if not os.path.exists("log"):
        os.makedirs("log")
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

#Declare Globals
global rm_client
#global Qualys_Password
#global username, baseurl, keyfile1, projects
def list_GCPConnectors_fromQualys(pageNo):
    logger.info(f'\nList Existing GCP connectors in Qualys Subscription....\n')
    api_endpoint = "{}/cloudview-api/rest/v1/gcp/connectors".format(baseurl)
    payload = {'pageNo': pageNo, 'pageSize': '50'}
    resp1 = http_request('get', api_endpoint, payload)
    if resp1.status_code == 200:
        resp11 = json.loads(resp1.content)
        paginate(resp11)
    else:
        logger.info(f'\nError Calling Get List of GCP connectors API {api_endpoint}?{payload}. Response Status code : {resp1.status_code}\n')
        return resp1

def paginate(response):
    nextToken = response['last']
    while nextToken is False:
        content = response['content']
        logger.debug("GCP API Response Content = {} \n".format(content))
        for projectid in content:
            logger.debug("List Project ID from GCP API = {}".format(projectid['projectId']))
            projectId = projectid['projectId']
            List_of_GCP_Connectors_in_Qualys.append(projectId)
        pageVar = response['pageable']
        pageno = pageVar['pageNumber']
        pageno += 1
        list_GCPConnectors_fromQualys(pageno)
    else:
        content = response['content']
        for projectid in content:
            projectId = projectid['projectId']
            List_of_GCP_Connectors_in_Qualys.append(projectId)
    logger.debug(f'\nCompleted listing all existing GCP connectors\n')
    logger.info(f'\nTotal count of existing GCP connectors: {len(List_of_GCP_Connectors_in_Qualys)}\n')
    logger.debug(f'\nExisting GCP connectors: {str(List_of_GCP_Connectors_in_Qualys)}\n')
    if List_of_GCP_Connectors_in_Qualys is not None:
        Add_GCP_Connectors()


def Add_GCP_Connectors():
    global rm_client
    #Compare the Lists and add only missing GCP project Id as connectors
    logger.debug("List of All GCP Projects: {} \n".format(str(List_Of_GCP_Projects)))
    logger.debug("List of All GCP Project Connectors in Qualys: {} \n".format(str(List_of_GCP_Connectors_in_Qualys)))
    Connectors_to_be_added_to_Qualys = [i for i in List_Of_GCP_Projects if i not in List_of_GCP_Connectors_in_Qualys]
    logger.info(f'\nProjectID {str(Connectors_to_be_added_to_Qualys)} Onboarding the Additional {len(Connectors_to_be_added_to_Qualys)} GCP projects as GCP connectors in Qualys....\n')
    try:
        for item in Connectors_to_be_added_to_Qualys:
            logger.debug("Connector to add to Qualys = {}".format(item))
            project_name = rm_client.fetch_project(item)
            logger.debug("project_name type: {}".format(type(project_name)))
            logger.debug("Project Name = {}".format(project_name.name))
            if project_name.name == '':
                project_name_str = item
            else:
                project_name_str = project_name.name
            api_endpoint = "{}/cloudview-api/rest/v1/gcp/connectors".format(baseurl)

            files = {
            'name': str(project_name_str),
            'projectId': str(item),
            'configFile': (split(keyfile2)[-1], open(keyfile2, 'rb'), 'application/json')}
            logger.debug("Files: \n {} \n".format(files))
            http_request('post', api_endpoint, files)
        #return resp2
    except Exception as err:
        logger.info(f'Error while creating GCP connector: {err}', exc_info=True)

def http_request(request_type, url, payload):
    Password = Qualys_Password
    usrPass = str(username) + ':' + str(Password)
    usrPassBytes = bytes(usrPass, "utf-8")
    b64Val = base64.b64encode(usrPassBytes).decode("utf-8")

    request_type = request_type.lower()
    resp = ''
    try:
        if request_type.lower() == 'post':
            headers = {
                'Accept': 'application/json',
                'Authorization': "Basic %s" % b64Val
            }
            resp = requests.post(url, headers=headers, files=payload, verify=True)
            logger.debug("Response Status Code: {}\n".format(resp.status_code))
            logger.debug("POST Response: {}".format(resp.text))
        elif request_type.lower() == 'get':
            headers = {
                'Accept': 'application/json',
                'Authorization': "Basic %s" % b64Val
            }
            resp = requests.get(url, headers=headers, params=payload, verify=True)
        else:
            #print('Request Type not supported')
            logger.info(f'\nRequest type: {request_type} is not Supported\n')
        resp.raise_for_status()
    except HTTPError as http_err:
        #print(f'HTTP error code: {http_err}')
        logger.error(f'\nHTTP error code: {http_err}\n')
        logger.info(f'\nError Message: {resp.content}\n')
    except Exception as err:
        #print(f'Other error: {err}')
        logger.error(f'\nOther error: {err}\n')
    logger.info("Status code: {}".format(resp))
    return resp


def List_GCP_Projects(servAccountJson):
    try:
        global rm_client
        rm_client = resource_manager.Client.from_service_account_json(servAccountJson)
        logger.info(f'Authenticating to GCP platform {rm_client}')
        try:
            list_projects = rm_client.list_projects()
            logger.debug(f'\nReading GCP project Ids from GCP organization....\n')
            for project in list_projects:
                List_Of_GCP_Projects.append(project.project_id)
        except Exception as err1:
            logger.error(f'\nError Message: {err1}\n', exc_info=True)
        logger.info(f'\n Total no of GCP projects listed: {len(List_Of_GCP_Projects)}')
        return List_Of_GCP_Projects
    except Exception as err2:
        logger.error(f'\nOther Error: {err2}\n.Please check if correct service account file/path provided, exc_info=True', exc_info=True)

#Main
def main_start():
    global rm_client
    global logger
    setup_logging()
    logger = logging.getLogger(__name__)
    Password()
    config()
    pagenum = 0
    try:
        if projects.lower() == 'all':
            List_GCP_Projects(keyfile1)
            list_GCPConnectors_fromQualys(pagenum)

        else:
            with open(projects, 'rt') as GCP_connector_info_file:
                rm_client = resource_manager.Client.from_service_account_json(keyfile1)
                reader = csv.DictReader(GCP_connector_info_file)
                read_info_file = list(reader)
                logger.info(f'\nReading GCP project Ids from CSV file....\n')
                for item in read_info_file:
                    List_Of_GCP_Projects.append(item['ProjectId'])
                GCP_connector_info_file.close()
                logger.info(f'\n Total no of GCP projects listed: {len(List_Of_GCP_Projects)}')
                list_GCPConnectors_fromQualys(pagenum)
    except Exception as err:
        logger.info(f'\nError: {err}\n')

main_start()

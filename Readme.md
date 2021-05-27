# Cloud View Multiple GCP Connectors Onboard Script

Onboarding of multiple GCP projects ( Associated with GCP organization/Folders) as Qualys cloud View connectors.

## License
***THIS SCRIPT IS PROVIDED TO YOU "AS IS." TO THE EXTENT PERMITTED BY LAW, QUALYS HEREBY DISCLAIMS ALL WARRANTIES AND LIABILITY FOR THE PROVISION OR USE OF THIS SCRIPT. IN NO EVENT SHALL THESE SCRIPTS BE DEEMED TO BE CLOUD SERVICES AS PROVIDED BY QUALYS***

## Description
The Purpose of this script is to help you onboard multiple GCP projects ( within an GCP organization/folder) or multiple selective GCP projects to Qualys Cloud View as GCP connectors.
This reporsitory contains:
1. Main Python program (source code)
2. Configuration files (Folder containing configuration file as well as logging configuration file)
3. A Sample CSV (includes GCP project Ids)
4. Sample Service Account JSON keys (1 for Authenticating GCP SDK calls to list GCP projects within Organization and 1 for Onboarding GCP projects to Qualys Cloud View as connectors)

### PLEASE NOTE : We do recommend using 2 different Service Account JSON keys for better management of permissions, if you will be using the All settings in the project scope configuration. The Service Account JSON key, specified by GcpApiKey, which will be used to authenticate GCP SDK and list GCP projects within GCP organization and folders will added as IAM member at GCP Organization level with Organization and Folder Viewer Permissions.

The other Service Account JSON Key, specified in ConnectorCreationJson, will be used to onboard GCP projects as Connectors in Qualys Cloud View. This service account will require Project Viewer and Security Viewer permissions on the projects scoped to create connectors.


## Deployment Modes:
There are 2 different modes for onboarding GCP projects as Qualys Cloud View Connectors:

1. **Organization**: To onboard all the GCP projects within an GCP organization & folders as Cloud View connectors. 
   To configure this mode, input 'ALL' as value for 'Projects' field within configuration file (config.yml).

2. **Multiple Projects**: To onboard Multiple/Selective GCP projects but not all the GCP projects within an Organization.
   To configure this input complete path of CSV file containing list of Projects Ids as value for 'Projects' field within configuration file (config.yml). 

## Pre-requisites:
Before you execute the script, you need to follow some pre configurations on GCP console as well as before executing scripts.

### A] Create Service Account to Authenticate GCP API/SDK calls
1. Create Service Account in any GCP project (recommended is a central GCP project) for eg. say Service_Account_A in GCP_Project_A. This service account will be used to authenticate GCP APIs/SDK calls.
Using this Service Account the script calls list projects API/SDK call to list all the GCP projects within GCP organization and folder.
2. Create A JSON key for Service_Account_A and download it. Input complete path of this JSON key as value for 'GcpApiKey' field within configuration file (config.yml).
3. Add this service Account as member at GCP organization and assign IAM role 'Resource Manager' --> 'Organization Viewer' and 'Folder Viewer' role to it.
4. Enable 'Cloud Resource Manager' API in which this Sevrice Account is created say for eg. here it would be GCP_Project_A.
To create a Sevrice Account and Add it as member at GCP organization please refer, Steps to Create Service Account and Add to GCP Organization.

### B] Create Service Account to Onboard GCP project(s) as Qualys Cloud View Connector
1. Create Service Account in any GCP project (recommended is a central GCP project) for eg. say Service_Account_B. This service account will be used to create a GCP connector in Qualys Cloud view.
2. Create a JSON key for Service_Account_B and download it. Input complete path of this JSON key as value for 'ConnectorCreationJson' field within configuration file (config.yml).
3. Add this service Account as member at GCP organization and assign IAM role 'Projects' --> 'Viewer' and 'IAM' --> 'Security Reviewer' role to it.
To create a Sevrice Account and Add it as member at GCP organization please refer, `Steps to Create Service Account and Add to GCP Organization`.

#### Steps to Create Service Account and Add to GCP Organization.
1. Login to GCP Console and navigate to IAM & Admin > Service Accounts.
2. Click 'CREATE SERVICE ACCOUNT'. 
3. Provide a name and description (optional) for the service account and click CREATE.
4. Click CREATE KEY.Select JSON as Key type and click CREATE. A message saying “Private key saved to your computer” is displayed and the JSON file is downloaded to your computer. Click CLOSE and then click DONE.
5. Navigate to GCP organization. Then navigate to IAM & Admin > IAM.
6. Click on 'ADD'.
7. Paste the Service Account email address(generated when service account was created)in 'New members' field.
8. Add required roles as mentioned in Step A & B to respective service accounts 'Select a role' dropdown list and Click 'SAVE'.


### C] Ensure the following list of APIs are enabled for all the GCP projects to be onboarded as Qualys Cloud View Connectors.
- Compute Engine API
- Cloud Resource Manager API
- Kubernetes Engine API
- Cloud SQL Admin API
- BigQuery API
- Cloud Functions API
- Cloud DNS API
- Cloud Key Management Service (KMS) API
- Cloud Logging API
- Stackdriver Monitoring API
follow `Steps to Enable the GCP APIs in API libray for a project` for more details on enabling Google APIs

#### Steps to Enable the GCP APIs in API libray for a project:
1. On GCP console, Navigate to API & Services > Library.
2. In the Search box, paste the required APIs from the list as mentioned in Step C.
3. Click on the API tab and then click 'ENABLE'.

### D] Configure the config.yml file
With required inputs, create the yaml configuration file i.e config.yml and store it in a suitable location.
Fields and inputs of config.yml file:
1. ***QualysUsername***: Username to authenticate and execute Qualys Cloud View API.
2. ***Baseurl***: Base URL for Qualys Cloud Platform i.e `https://qualysguard.qualys.com` (for detailed list, check [Qualys Platform URLs](https://www.qualys.com/docs/qualys-cloudview-api-user-guide.pdf))
3. ***GcpApiKey***: Complete path for downloaded JSON key for Service_Account_A.
4. ***ConnectorCreationJson***: Complete path for downloaded JSON key for Service_Account_B.
5. ***Projects***: Either path complete path of CSV file containing GCP project Ids or ALL.


### E] Use/Update the logging.yml file
logging.yml file stores configuration details to setup logging. You can use the same reference yaml file for logging as provided in our github (Provide link to sample config and logging yml files in github) or update the logging.yml as per your requirements.

**PS**: ***It is recommended to store config.yml and logging.yml in a single folder say config folder i.e ./config/config.yml & ./config/logging.yml for better file management.***

### F] (Optional) Create a CSV file
You need to create a CSV file if you are using 'Multiple Projects' deployment mode. Please refer the sample CSV as in our github (Provide link to sample CSV in github).

### G] Install google-cloud-resource-manager client library for python
1. As this script uses Cloud Resource Manager API to list all the GCP projects within an GCP organization, you need to install 'google-cloud-resource-manager' client library for Python.
2. To install, use command > pip install google-cloud-resource-manager.

## Getting Started
1. Update the config.yml by making the choice of deployment mode i.e All projects within an GCP Organization OR Multiple Projects within an GCP organization/Folders.
2. Update teh config.ymal with other details as mentioned in Step D.
3. (Optional)Update the logging.yml file if any specific logging requirement.
4. (Optional) Create a CSV file if 'Multiple Projects' mode used.
5. Run the main python program.

### PLEASE NOTE: When the main python program is executed, it will prompt you to input the Qualy password used to execute/call Qualys Cloud View API.

## Reference Links
- [Qualys Cloud View API guide](https://www.qualys.com/docs/qualys-cloudview-api-user-guide.pdf).
- [Install Google python client library for Google cloud resource manager](https://pypi.org/project/google-cloud-resource-manager/)
- [Creating and Managing GCP Service Accounts](https://cloud.google.com/iam/docs/creating-managing-service-accounts)
- [Enabling GCP APIs](https://cloud.google.com/apis/docs/getting-started)
- [Understanding GCP IAM roles](https://cloud.google.com/iam/docs/understanding-roles)
 

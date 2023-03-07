import requests
import os


# Method to create index pattern in kibana
def createIndexPattern(indexPatternName: str, kibanaURL: str):
    # Kibana credentials to be setup as env to create index in kibana depending upon where it will be running
    kibanaUsername = os.environ.get('kibanaUsername')
    kibanaPassword = os.environ.get('kibanaPassword')

    """_summary_
    Args:
        indexPatternName (str): Name of the index pattern to be created
        kibanaURL       (str): Kibana URL where index would be created

    Returns:
        _type_: If index is created
    """
    
    indexPatternName = indexPatternName + '*'
    try:
        headers = {
            'kbn-xsrf': 'true',
            'Content-Type': 'application/json',
        }

        json_data = {
            'index_pattern': {
                'title': indexPatternName,
                'timeFieldName': '@timestamp',
            },
        }
        kibanaIndexCreateURL = 'https://' + kibanaURL + '/' + 'api/index_patterns/index_pattern'
        response = requests.post(
            kibanaIndexCreateURL,
            headers=headers,
            json=json_data,
            auth=(kibanaUsername, kibanaPassword),
        )

        return True
    
    except Exception as e:
        print(str(e))
        return False

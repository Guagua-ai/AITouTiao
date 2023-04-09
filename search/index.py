import os
from algoliasearch.search_client import SearchClient


def create_post_search_index():
    ALGOLIA_APP_ID = os.getenv('ALGOLIA_APP_ID')
    ALGOLIA_API_KEY = os.getenv('ALGOLIA_API_KEY')
    ALGOLIA_INDEX_NAME = os.getenv('DEPLOY_ENV') + '-post-index'

    # Initialize the Algolia client and index
    algolia_client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_API_KEY)
    algolia_index = algolia_client.init_index(ALGOLIA_INDEX_NAME)
    return algolia_index


def create_user_search_index():
    ALGOLIA_APP_ID = os.getenv('ALGOLIA_APP_ID')
    ALGOLIA_API_KEY = os.getenv('ALGOLIA_API_KEY')
    ALGOLIA_INDEX_NAME = os.getenv('DEPLOY_ENV') + '-user-index'

    # Initialize the Algolia client and index
    algolia_client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_API_KEY)
    algolia_index = algolia_client.init_index(ALGOLIA_INDEX_NAME)
    return algolia_index

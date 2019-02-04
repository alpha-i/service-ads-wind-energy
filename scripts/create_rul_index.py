from elasticsearch import Elasticsearch

host = '51.144.39.71:9200'
index_name = 'wf_model_ruls'
doc_type = 'wf_model_rul'

es = Elasticsearch('51.144.39.71:9200')

mapping = {
    "mappings": {
        doc_type: {
            'properties': {
                'timestamp': {
                    'type': 'date'
                }
            }
        }
    }
}
es.indices.create(index_name, mapping)

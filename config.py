import csv
from collections import defaultdict

#from app.common.auth import AuthKey
from app.common.scoring_conf import ScoringMethods

__author__ = 'andreap'




import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    DATA_VERSION = os.getenv('OPENTARGETS_DATA_VERSION', '16.08_')
    ELASTICSEARCH_DATA_INDEX_NAME = DATA_VERSION+'evidence-data*'
    ELASTICSEARCH_DATA_DOC_NAME = 'evidencestring'
    ELASTICSEARCH_EFO_LABEL_INDEX_NAME = DATA_VERSION+'efo-data'
    ELASTICSEARCH_EFO_LABEL_DOC_NAME = 'efo'
    ELASTICSEARCH_ECO_INDEX_NAME = DATA_VERSION+'eco-data'
    ELASTICSEARCH_ECO_DOC_NAME = 'eco'
    ELASTICSEARCH_GENE_NAME_INDEX_NAME = DATA_VERSION+'gene-data'
    ELASTICSEARCH_GENE_NAME_DOC_NAME = 'genedata'
    ELASTICSEARCH_EXPRESSION_INDEX_NAME = DATA_VERSION+'expression-data'
    ELASTICSEARCH_EXPRESSION_DOC_NAME = 'expression'
    ELASTICSEARCH_REACTOME_INDEX_NAME = DATA_VERSION+'reactome-data'
    ELASTICSEARCH_REACTOME_REACTION_DOC_NAME = 'reactome-reaction'
    ELASTICSEARCH_DATA_ASSOCIATION_INDEX_NAME = DATA_VERSION+'association-data'
    ELASTICSEARCH_DATA_ASSOCIATION_DOC_NAME = 'association'
    ELASTICSEARCH_DATA_SEARCH_INDEX_NAME = DATA_VERSION+'search-data'
    ELASTICSEARCH_DATA_SEARCH_DOC_NAME = 'search-object'
    ELASTICSEARCH_DATA_RELATION_INDEX_NAME = DATA_VERSION + 'relation-data'
    ELASTICSEARCH_DATA_RELATION_DOC_NAME = 'relation'
    ELASTICSEARCH_LOG_EVENT_INDEX_NAME = '!eventlog'
    DEBUG = os.getenv('API_DEBUG', False)
    TESTING = False
    PROFILE = False
    SECRET_KEY = os.getenv('SECRET_KEY', u'C=41d6xo]4940NP,9jwF@@v0KDdTtO')
    PUBLIC_API_BASE_PATH = '/api/public/v'
    PRIVATE_API_BASE_PATH = '/api/private/v'
    API_VERSION = '1.2'
    API_VERSION_MINOR = '1.2.1'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = True
    '''datatype configuration'''
    DATATYPES = defaultdict(lambda: "other")
    DATATYPES['rna_expression'] = ['expression_atlas',]
    DATATYPES['genetic_association'] = ['uniprot','gwas_catalog','eva','uniprot_literature', 'gene2phenotype']
    DATATYPES['affected_pathway'] = ['reactome',]
    DATATYPES['animal_model'] = ['phenodigm',]
    DATATYPES['somatic_mutation'] = ['cancer_gene_census','eva_somatic','intogen']
    DATATYPES['known_drug'] = ['chembl',]
    DATATYPES['literature'] = ['europepmc']
    DATATYPE_ORDERED=['genetic_association','somatic_mutation','known_drug','rna_expression','affected_pathway','animal_model', 'literature']
    # DATATYPES['protein_expression'] = ['hpa']

    DATASOURCE_SCORING_METHOD = defaultdict(lambda: ScoringMethods.SUM)
    # DATASOURCE_SCORING_METHOD['phenodigm'] = ScoringMethods.MAX

    PROXY_SETTINGS={'allowed_targets': {'ensembl': 'https://rest.ensembl.org/',
                                        'gxa': 'https://www.ebi.ac.uk/gxa/',
                                        'pdbe': 'https://www.ebi.ac.uk/pdbe/',
                                        'epmc': 'http://www.ebi.ac.uk/europepmc/',
                                        },
                    'allowed_domains': ['www.ebi.ac.uk'],
                    'allowed_request_domains' : ['targetvalidation.org', 'alpha.targetvalidation.org','beta.targetvalidation.org','localhost', '127.0.0.1'],
                    }
    REDIS_SERVER_PATH =os.getenv('REDIS_SERVER_PATH', '/tmp/api_redis.db')

    USAGE_LIMIT_DEFAULT_SHORT = 3000
    USAGE_LIMIT_DEFAULT_LONG = 1200000
    USAGE_LIMIT_PATH = 'rate_limit.csv'
    IP_RESOLVER_LIST_PATH = 'ip_list.csv'

    NO_CACHE_PARAMS = 'no_cache'



    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    # currently these also corresponds to the defaults i.e. OPENTARGETS_API_CONFIG=`default`
    DEBUG = True
    ELASTICSEARCH_URL = os.getenv('ELASTICSEARCH_URL', 'http://193.62.54.18:9200/')
    LOGSTASH_HOST = '127.0.0.1'
    LOGSTASH_PORT = 5000
    APP_CACHE_EXPIRY_TIMEOUT = 1

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)



class TestingConfig(Config):
    TESTING = True
    ELASTICSEARCH_URL = os.getenv('ELASTICSEARCH_URL', 'http://beta.targetvalidation.org:9200/')
    APP_CACHE_EXPIRY_TIMEOUT = 60
    SERVER_NAME = 'localhost:5000'


class ProductionConfig(Config):
    ## kubernetes automatically defines DNS names for each service, at least on GKE
    ELASTICSEARCH_URL = os.getenv('ELASTICSEARCH_URL', 'http://elasticsearch:9200')
    APP_CACHE_EXPIRY_TIMEOUT = 60*60*6 #6 hours
    USAGE_LIMIT_PATH = '/etc/restapi/rate_limit.csv'
    IP_RESOLVER_LIST_PATH = '/etc/restapi/ip_list.csv'

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        #TODO: handle logs
        #
        # import logging
        # from logging.handlers import SMTPHandler
        # credentials = None
        # secure = None
        # if getattr(cls, 'MAIL_USERNAME', None) is not None:
        #     credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
        #     if getattr(cls, 'MAIL_USE_TLS', None):
        #         secure = ()
        # mail_handler = SMTPHandler(
        #     mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
        #     fromaddr=cls.FLASKY_MAIL_SENDER,
        #     toaddrs=[cls.FLASKY_ADMIN],
        #     subject=cls.FLASKY_MAIL_SUBJECT_PREFIX + ' Application Error',
        #     credentials=credentials,
        #     secure=secure)
        # mail_handler.setLevel(logging.ERROR)
        # app.logger.addHandler(mail_handler)



# we are not using the one below.
# TODO: consider deleting it or whether it should belong to production directly

# class UnixConfig(ProductionConfig):
#     @classmethod
#     def init_app(cls, app):
#         ProductionConfig.init_app(app)
#
#         # log to syslog
#         import logging
#         from logging.handlers import SysLogHandler
#         syslog_handler = SysLogHandler()
#         syslog_handler.setLevel(logging.WARNING)
#         app.logger.addHandler(syslog_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

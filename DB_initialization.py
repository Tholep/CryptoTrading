from utilities import initialized_db
import yaml
import logging
import logging.config
conf=yaml.load(open("conf/conf_recommender.yml"))
#set up logger
logging.config.dictConfig(conf["logging"])
logger = logging.getLogger(__name__)
if __name__ == "__main__":
    initialized_db()
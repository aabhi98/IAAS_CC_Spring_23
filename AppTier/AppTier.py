import logging
from AppTier.Utils import AWSUtils, AppTierProperties
from AppTier.classifier import ImageClassifier

log = logging.getLogger(__name__)

if __name__ == "__main__":
    log.info("Starting IAAS App Tier Application")
    ImageClassifier(AWSUtils(AppTierProperties())).start_classifier()
    log.info("AppTier Instance Shutting Down")

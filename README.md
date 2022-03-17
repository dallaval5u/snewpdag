# snewpdag

SNEWS2 alert (pointing) calculations.

# Hop stream
For testing purposes alerts are read from a Local server. When reading the alerts online is necessary, then set the online hop-broker in app.py to
online_alert_topic = "kafka://"kafka.scimma.org"/snews.alert-test" instead of the current alert_topic = "kafka://localhost:9092/snews.alert-test"

SELECT_LABELLED_TICKETS = """
    SELECT ticket_id, subject, body, customer_email, category
    FROM {table}
"""

INSERT_MODEL = """
    INSERT INTO retraining.classifier_model_registry (
        model_name,
        model_version,
        training_job_name,
        artifact_s3_uri,
        training_data_s3_uri,
        metrics
    )
    VALUES (
        %(model_name)s,
        %(model_version)s,
        %(training_job_name)s,
        %(artifact_s3_uri)s,
        %(training_data_s3_uri)s,
        %(metrics)s
    )
    RETURNING model_id
"""

DEMOTE_CHAMPIONS = """
    UPDATE retraining.classifier_model_registry
    SET is_champion = false
    WHERE model_name = %(model_name)s AND is_champion
"""

PROMOTE_MODEL = """
    UPDATE retraining.classifier_model_registry
    SET is_champion = true, promoted_at = now()
    WHERE model_id = %(model_id)s
"""

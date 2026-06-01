class RequestContext:
    def __init__(self, org_id: str, settings):
        self.org_id = org_id
        self.settings = settings

        # runtime info - Mapeando os atributos planos do objeto settings
        self.aws_config = {
            "region": getattr(settings, "AWS_REGION", "us-east-1"),
            "profile": getattr(settings, "AWS_PROFILE", None),
        }
        self.rag_config = {
            "bucket": getattr(settings, "RAG_BUCKET", ""),
            "key": getattr(settings, "RAG_KEY", ""),
        }
        self.memory_policy = {}  # Placeholder já que não existe no settings.py
        self.runtime = {}

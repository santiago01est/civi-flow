# Custom OpenTelemetry metrics
from opentelemetry import metrics
from opentelemetry.metrics import Counter, Histogram

class CiviChatMetrics:
    def __init__(self):
        self.meter = metrics.get_meter(__name__)
        
        # Custom counters
        self.chat_requests = self.meter.create_counter(
            name="chat_requests_total",
            description="Total number of chat requests",
            unit="1"
        )
        
        self.government_queries = self.meter.create_counter(
            name="government_queries_total",
            description="Total government data queries",
            unit="1"
        )
        
        self.notifications_sent = self.meter.create_counter(
            name="notifications_sent_total",
            description="Total notifications sent",
            unit="1"
        )
        
        # Custom histograms
        self.chat_response_time = self.meter.create_histogram(
            name="chat_response_duration",
            description="Chat response latency",
            unit="ms"
        )
        
        self.azure_ai_latency = self.meter.create_histogram(
            name="azure_ai_call_duration",
            description="Azure AI service call latency",
            unit="ms"
        )
    
    def record_chat_request(self, user_location: str = None):
        attributes = {}
        if user_location:
            attributes["location"] = user_location
        self.chat_requests.add(1, attributes)
    
    def record_government_query(self, query_type: str):
        self.government_queries.add(1, {"query_type": query_type})
    
    def record_notification(self, notification_type: str):
        self.notifications_sent.add(1, {"type": notification_type})

# Singleton instance
civi_metrics = CiviChatMetrics()

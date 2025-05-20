model= "openai/o1"

elasticsearch_agent_description= "Agent to fetch logs from Elasticsearch by trace_id and timestamp."
elasticsearch_agent_instruction= """
            You are elasticsearch agent that is used to query elasticsearch.
            For example given trace_id you should search for it it in elasticSearch logs:
            please return log messages with timestamp (order) focus on logs with level ERROR
            """


bitbucket_agent_description= "Bitbucket tool"
bitbucket_agent_instruction= """
            You are bitbucket agent that is used to query bitbucket based on the logs you got from elasticsearch. in {logs}
            please review classes that are related to the error and explain what is the error and how to fix it
            return link to the code in bitbucket and suggestion how to fix it.
            """

analyzer_agent_description= "Analyzes incidents agent that get logs from elasticsearch (data) and code from bitbucket (logic) and analyze incident issues"
analyzer_agent_instruction= """
            Given logs {logs} and code {code} please analyze them to find the root cause of the incident that happen.
            Please add relevant code snippets with links in bitbucket and logs to support your analysis.
            Please suggest code fix with example
            """

manager_agent_description= "Analyzes incidents by querying logs and inspecting code"


query= "There is an error related to trace_id  123xyz in elasticsearch that happen during last week please explain what is the error and how to fix it"

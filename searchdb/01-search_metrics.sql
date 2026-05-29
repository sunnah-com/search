-- Shadow-sampling metrics table. In prod this lives in the externally-managed
-- searchdb; locally the docker-compose `searchdb` service runs this on first
-- init (mounted into /docker-entrypoint-initdb.d, applied to MYSQL_DATABASE).
CREATE TABLE IF NOT EXISTS search_metrics (
    id                     BIGINT        NOT NULL AUTO_INCREMENT PRIMARY KEY,
    query                  TEXT          NOT NULL,
    lexical_results        JSON          NOT NULL,
    lexical_query_time_ms  DECIMAL(12,3) NOT NULL,
    semantic_results       JSON          NOT NULL,
    semantic_query_time_ms DECIMAL(12,3) NOT NULL,
    semantic_model_name    VARCHAR(255)  NOT NULL,
    routing_decision       VARCHAR(255)  NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

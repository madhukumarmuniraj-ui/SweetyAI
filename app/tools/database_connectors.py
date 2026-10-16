"""
SweetyAI Database Connectors
PostgreSQL, MySQL, MongoDB, Redis, Neo4j integrations
"""

import json
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

# SQLite (built-in)
import sqlite3

# PostgreSQL
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False
    print("[Database] PostgreSQL not available. Run: pip install psycopg2-binary")

# MySQL
try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    print("[Database] MySQL not available. Run: pip install mysql-connector-python")

# MongoDB
try:
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    print("[Database] MongoDB not available. Run: pip install pymongo")

# Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("[Database] Redis not available. Run: pip install redis")

# Neo4j
try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    print("[Database] Neo4j not available. Run: pip install neo4j")


# =============================================================================
# SQLITE CLIENT (Enhanced)
# =============================================================================

class SQLiteClient:
    """Enhanced SQLite database client."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None

    def connect(self) -> str:
        """Connect to SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            return f"Connected to SQLite: {self.db_path}"
        except Exception as e:
            return f"Error connecting: {e}"

    def execute(self, query: str, params: tuple = None) -> Union[List[Dict], str]:
        """Execute SQL query."""
        try:
            if not self.conn:
                self.connect()

            cursor = self.conn.cursor()
            cursor.execute(query, params or ())

            if query.strip().upper().startswith('SELECT'):
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            else:
                self.conn.commit()
                return f"Query executed: {cursor.rowcount} rows affected"

        except Exception as e:
            return f"Error executing query: {e}"

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


# =============================================================================
# POSTGRESQL CLIENT
# =============================================================================

class PostgreSQLClient:
    """PostgreSQL database client."""

    def __init__(self, host: str, database: str, user: str, password: str, port: int = 5432):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.conn = None

    def connect(self) -> str:
        """Connect to PostgreSQL database."""
        if not POSTGRESQL_AVAILABLE:
            return "Error: psycopg2 not installed"

        try:
            self.conn = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            return f"Connected to PostgreSQL: {self.database}"
        except Exception as e:
            return f"Error connecting: {e}"

    def execute(self, query: str, params: tuple = None, fetch: bool = True) -> Union[List[Dict], str]:
        """Execute SQL query."""
        if not self.conn:
            return "Error: Not connected"

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params or ())

                if fetch and query.strip().upper().startswith('SELECT'):
                    rows = cursor.fetchall()
                    return [dict(row) for row in rows]
                else:
                    self.conn.commit()
                    return f"Query executed: {cursor.rowcount} rows affected"

        except Exception as e:
            self.conn.rollback()
            return f"Error executing query: {e}"

    def bulk_insert(self, table: str, data: List[Dict[str, Any]]) -> str:
        """Bulk insert data into table."""
        if not data:
            return "No data to insert"

        try:
            columns = data[0].keys()
            values_template = ', '.join(['%s'] * len(columns))
            insert_query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({values_template})"

            with self.conn.cursor() as cursor:
                for row in data:
                    cursor.execute(insert_query, tuple(row.values()))

            self.conn.commit()
            return f"Inserted {len(data)} rows into {table}"

        except Exception as e:
            self.conn.rollback()
            return f"Error bulk inserting: {e}"

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


# =============================================================================
# MYSQL CLIENT
# =============================================================================

class MySQLClient:
    """MySQL database client."""

    def __init__(self, host: str, database: str, user: str, password: str, port: int = 3306):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.conn = None

    def connect(self) -> str:
        """Connect to MySQL database."""
        if not MYSQL_AVAILABLE:
            return "Error: mysql-connector-python not installed"

        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            return f"Connected to MySQL: {self.database}"
        except Exception as e:
            return f"Error connecting: {e}"

    def execute(self, query: str, params: tuple = None, fetch: bool = True) -> Union[List[Dict], str]:
        """Execute SQL query."""
        if not self.conn:
            return "Error: Not connected"

        try:
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute(query, params or ())

            if fetch and query.strip().upper().startswith('SELECT'):
                rows = cursor.fetchall()
                return rows
            else:
                self.conn.commit()
                return f"Query executed: {cursor.rowcount} rows affected"

        except Exception as e:
            self.conn.rollback()
            return f"Error executing query: {e}"
        finally:
            cursor.close()

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


# =============================================================================
# MONGODB CLIENT
# =============================================================================

class MongoDBClient:
    """MongoDB database client."""

    def __init__(self, connection_string: str, database: str):
        self.connection_string = connection_string
        self.database_name = database
        self.client = None
        self.db = None

    def connect(self) -> str:
        """Connect to MongoDB."""
        if not MONGODB_AVAILABLE:
            return "Error: pymongo not installed"

        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            # Test connection
            self.client.server_info()
            return f"Connected to MongoDB: {self.database_name}"
        except Exception as e:
            return f"Error connecting: {e}"

    def find(self, collection: str, query: Dict = None, limit: int = 100) -> List[Dict]:
        """Find documents in collection."""
        if not self.db:
            return [{"error": "Not connected"}]

        try:
            query = query or {}
            results = list(self.db[collection].find(query).limit(limit))

            # Convert ObjectId to string
            for doc in results:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])

            return results
        except Exception as e:
            return [{"error": str(e)}]

    def insert(self, collection: str, document: Dict) -> str:
        """Insert document into collection."""
        if not self.db:
            return "Error: Not connected"

        try:
            result = self.db[collection].insert_one(document)
            return f"Inserted document with ID: {result.inserted_id}"
        except Exception as e:
            return f"Error inserting: {e}"

    def insert_many(self, collection: str, documents: List[Dict]) -> str:
        """Insert multiple documents."""
        if not self.db:
            return "Error: Not connected"

        try:
            result = self.db[collection].insert_many(documents)
            return f"Inserted {len(result.inserted_ids)} documents"
        except Exception as e:
            return f"Error inserting: {e}"

    def update(self, collection: str, query: Dict, update: Dict) -> str:
        """Update documents in collection."""
        if not self.db:
            return "Error: Not connected"

        try:
            result = self.db[collection].update_many(query, {'$set': update})
            return f"Updated {result.modified_count} documents"
        except Exception as e:
            return f"Error updating: {e}"

    def delete(self, collection: str, query: Dict) -> str:
        """Delete documents from collection."""
        if not self.db:
            return "Error: Not connected"

        try:
            result = self.db[collection].delete_many(query)
            return f"Deleted {result.deleted_count} documents"
        except Exception as e:
            return f"Error deleting: {e}"

    def aggregate(self, collection: str, pipeline: List[Dict]) -> List[Dict]:
        """Run aggregation pipeline."""
        if not self.db:
            return [{"error": "Not connected"}]

        try:
            results = list(self.db[collection].aggregate(pipeline))
            for doc in results:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
            return results
        except Exception as e:
            return [{"error": str(e)}]

    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()


# =============================================================================
# REDIS CLIENT
# =============================================================================

class RedisClient:
    """Redis cache client."""

    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0, password: str = None):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.client = None

    def connect(self) -> str:
        """Connect to Redis."""
        if not REDIS_AVAILABLE:
            return "Error: redis not installed"

        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True
            )
            self.client.ping()
            return f"Connected to Redis: {self.host}:{self.port}"
        except Exception as e:
            return f"Error connecting: {e}"

    def set(self, key: str, value: str, expire: int = None) -> str:
        """Set key-value pair."""
        if not self.client:
            return "Error: Not connected"

        try:
            self.client.set(key, value, ex=expire)
            return f"Set key: {key}"
        except Exception as e:
            return f"Error setting key: {e}"

    def get(self, key: str) -> Optional[str]:
        """Get value by key."""
        if not self.client:
            return None

        try:
            return self.client.get(key)
        except Exception as e:
            return None

    def delete(self, *keys: str) -> str:
        """Delete keys."""
        if not self.client:
            return "Error: Not connected"

        try:
            count = self.client.delete(*keys)
            return f"Deleted {count} keys"
        except Exception as e:
            return f"Error deleting keys: {e}"

    def exists(self, key: str) -> bool:
        """Check if key exists."""
        if not self.client:
            return False
        return self.client.exists(key) > 0

    def keys(self, pattern: str = '*') -> List[str]:
        """Get keys matching pattern."""
        if not self.client:
            return []
        return self.client.keys(pattern)

    def flush(self) -> str:
        """Clear all keys in current database."""
        if not self.client:
            return "Error: Not connected"

        try:
            self.client.flushdb()
            return "Database flushed"
        except Exception as e:
            return f"Error flushing database: {e}"


# =============================================================================
# NEO4J CLIENT (Graph Database)
# =============================================================================

class Neo4jClient:
    """Neo4j graph database client."""

    def __init__(self, uri: str, user: str, password: str):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None

    def connect(self) -> str:
        """Connect to Neo4j."""
        if not NEO4J_AVAILABLE:
            return "Error: neo4j not installed"

        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            self.driver.verify_connectivity()
            return f"Connected to Neo4j: {self.uri}"
        except Exception as e:
            return f"Error connecting: {e}"

    def execute(self, query: str, parameters: Dict = None) -> List[Dict]:
        """Execute Cypher query."""
        if not self.driver:
            return [{"error": "Not connected"}]

        try:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                return [dict(record) for record in result]
        except Exception as e:
            return [{"error": str(e)}]

    def create_node(self, label: str, properties: Dict) -> str:
        """Create a node."""
        if not self.driver:
            return "Error: Not connected"

        try:
            props_str = ', '.join([f"{k}: ${k}" for k in properties.keys()])
            query = f"CREATE (n:{label} {{{props_str}}}) RETURN id(n) as id"

            with self.driver.session() as session:
                result = session.run(query, properties)
                node_id = result.single()['id']
                return f"Created node with ID: {node_id}"
        except Exception as e:
            return f"Error creating node: {e}"

    def create_relationship(
        self,
        from_label: str,
        from_property: str,
        from_value: Any,
        to_label: str,
        to_property: str,
        to_value: Any,
        relationship_type: str,
        properties: Dict = None
    ) -> str:
        """Create relationship between nodes."""
        if not self.driver:
            return "Error: Not connected"

        try:
            props = properties or {}
            props_str = ', '.join([f"{k}: ${k}" for k in props.keys()]) if props else ''

            query = f"""
            MATCH (a:{from_label} {{{from_property}: $from_value}})
            MATCH (b:{to_label} {{{to_property}: $to_value}})
            CREATE (a)-[r:{relationship_type} {{{props_str}}}]->(b)
            RETURN id(r) as id
            """

            params = {'from_value': from_value, 'to_value': to_value, **props}

            with self.driver.session() as session:
                result = session.run(query, params)
                rel_id = result.single()['id']
                return f"Created relationship with ID: {rel_id}"
        except Exception as e:
            return f"Error creating relationship: {e}"

    def find_path(self, from_label: str, to_label: str, max_depth: int = 5) -> List[Dict]:
        """Find shortest path between node types."""
        if not self.driver:
            return [{"error": "Not connected"}]

        try:
            query = f"""
            MATCH path = shortestPath(
                (a:{from_label})-[*..{max_depth}]-(b:{to_label})
            )
            RETURN path
            LIMIT 10
            """

            with self.driver.session() as session:
                result = session.run(query)
                return [{"path": str(record['path'])} for record in result]
        except Exception as e:
            return [{"error": str(e)}]

    def close(self):
        """Close Neo4j connection."""
        if self.driver:
            self.driver.close()


__all__ = [
    'SQLiteClient',
    'PostgreSQLClient',
    'MySQLClient',
    'MongoDBClient',
    'RedisClient',
    'Neo4jClient'
]

"""
Graph Database Loader for Memgraph

This script loads activities data into Memgraph graph database.
It creates nodes and relationships based on the defined schema.

Usage:
    python load_graph.py [--clear]

    --clear: Clear existing data before loading

Requirements:
    pip install neo4j # working with memgraph and neo4j too
"""

import json
import argparse
import re
from pathlib import Path
from neo4j import GraphDatabase

from ontology import (
    LEVELS_OF_STUDY, EDUCATION_LEVEL_MAP, ACTIVITY_TYPES, LOCATIONS, LOCATION_MAP,
    STATES, SKILLS, JOBS, SKILL_JOB_MAPPING, FIELDS, FORMATS, FUNDING_TYPES,
    ORGANISATION_PARTNERSHIPS, FIELD_KEYWORDS, SKILL_KEYWORDS, FORMAT_KEYWORDS,
    FUNDING_KEYWORDS
)

# Graph connection settings
GRAPH_URI = "bolt://localhost:7687"
GRAPH_USER = ""  # Graph database doesn't require auth by default
GRAPH_PASSWORD = ""

class GraphLoader:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password) if user else None)
        self.organisations = {}  # Track created organisations {name: id}
        
    def close(self):
        self.driver.close()
        
    def execute(self, query: str, parameters: dict = None):
        """Execute a Cypher query."""
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return list(result)
    
    def clear_database(self):
        """Remove all nodes and relationships."""
        print("Clearing database...")
        self.execute("MATCH (n) DETACH DELETE n")
        print("Database cleared.")
        
    def create_constraints(self):
        """Create uniqueness constraints and indexes for better performance."""
        print("Creating constraints and indexes...")
        
        constraints = [
            "CREATE CONSTRAINT ON (n:Activity) ASSERT n.id IS UNIQUE",
            "CREATE CONSTRAINT ON (n:LevelOfStudy) ASSERT n.id IS UNIQUE",
            "CREATE CONSTRAINT ON (n:ActivityType) ASSERT n.id IS UNIQUE",
            "CREATE CONSTRAINT ON (n:Organisation) ASSERT n.id IS UNIQUE",
            "CREATE CONSTRAINT ON (n:Location) ASSERT n.id IS UNIQUE",
            "CREATE CONSTRAINT ON (n:State) ASSERT n.id IS UNIQUE",
            "CREATE CONSTRAINT ON (n:Skill) ASSERT n.id IS UNIQUE",
            "CREATE CONSTRAINT ON (n:Job) ASSERT n.id IS UNIQUE",
            "CREATE CONSTRAINT ON (n:Field) ASSERT n.id IS UNIQUE",
            "CREATE CONSTRAINT ON (n:Format) ASSERT n.id IS UNIQUE",
            "CREATE CONSTRAINT ON (n:FundingType) ASSERT n.id IS UNIQUE",
        ]
        
        for constraint in constraints:
            try:
                self.execute(constraint)
            except Exception as e:
                # Constraint might already exist
                if "already exists" not in str(e).lower():
                    print(f"Warning: {e}")
                    
        # Create indexes for common lookups
        indexes = [
            "CREATE INDEX ON :Activity(name)",
            "CREATE INDEX ON :Organisation(name)",
            "CREATE INDEX ON :ActivityType(name)",
            "CREATE INDEX ON :Location(name)",
        ]
        
        for index in indexes:
            try:
                self.execute(index)
            except Exception:
                pass  # Index might already exist
                
        print("Constraints and indexes created.")
        
    def load_static_nodes(self):
        """Load all static/dummy data nodes."""
        print("Loading static nodes...")
        
        # LevelOfStudy
        for item in LEVELS_OF_STUDY:
            self.execute("""
                CREATE (n:LevelOfStudy {id: $id, name: $name, code: $code})
            """, item)
        print(f"  - Created {len(LEVELS_OF_STUDY)} LevelOfStudy nodes")
        
        # ActivityType
        for item in ACTIVITY_TYPES:
            self.execute("""
                CREATE (n:ActivityType {id: $id, name: $name, description: $description})
            """, {"id": item["id"], "name": item["name"], "description": item["description"]})
        print(f"  - Created {len(ACTIVITY_TYPES)} ActivityType nodes")
        
        # ActivityType PARENT_OF relationships
        for item in ACTIVITY_TYPES:
            if item.get("parent_id"):
                self.execute("""
                    MATCH (child:ActivityType {id: $child_id})
                    MATCH (parent:ActivityType {id: $parent_id})
                    CREATE (parent)-[:PARENT_OF]->(child)
                """, {"child_id": item["id"], "parent_id": item["parent_id"]})
        print("  - Created ActivityType PARENT_OF relationships")
        
        # Location
        for item in LOCATIONS:
            self.execute("""
                CREATE (n:Location {id: $id, name: $name, type: $type})
            """, {"id": item["id"], "name": item["name"], "type": item["type"]})
        print(f"  - Created {len(LOCATIONS)} Location nodes")
        
        # Location hierarchy (LOCATED_IN)
        for item in LOCATIONS:
            if item.get("parent_id"):
                self.execute("""
                    MATCH (child:Location {id: $child_id})
                    MATCH (parent:Location {id: $parent_id})
                    CREATE (child)-[:LOCATED_IN]->(parent)
                """, {"child_id": item["id"], "parent_id": item["parent_id"]})
        print("  - Created Location LOCATED_IN relationships")
        
        # State
        for item in STATES:
            self.execute("""
                CREATE (n:State {id: $id, shortcut: $shortcut, name: $name})
            """, item)
        print(f"  - Created {len(STATES)} State nodes")
        
        # Link Czech regions to Czech Republic state
        self.execute("""
            MATCH (loc:Location {type: 'country', name: 'Česká republika'})
            MATCH (state:State {shortcut: 'CZ'})
            CREATE (loc)-[:LOCATED_IN]->(state)
        """)
        
        # Skill
        for item in SKILLS:
            self.execute("""
                CREATE (n:Skill {id: $id, name: $name, description: $description})
            """, item)
        print(f"  - Created {len(SKILLS)} Skill nodes")
        
        # Job
        for item in JOBS:
            self.execute("""
                CREATE (n:Job {id: $id, name: $name, averageSalary: $averageSalary})
            """, item)
        print(f"  - Created {len(JOBS)} Job nodes")
        
        # Skill USED_IN Job relationships
        for skill_id, job_id in SKILL_JOB_MAPPING:
            self.execute("""
                MATCH (skill:Skill {id: $skill_id})
                MATCH (job:Job {id: $job_id})
                CREATE (skill)-[:USED_IN]->(job)
            """, {"skill_id": skill_id, "job_id": job_id})
        print(f"  - Created {len(SKILL_JOB_MAPPING)} Skill-Job relationships")
        
        # Field
        for item in FIELDS:
            self.execute("""
                CREATE (n:Field {id: $id, name: $name, description: $description})
            """, item)
        print(f"  - Created {len(FIELDS)} Field nodes")
        
        # Format
        for item in FORMATS:
            self.execute("""
                CREATE (n:Format {id: $id, name: $name, durationCategory: $durationCategory})
            """, item)
        print(f"  - Created {len(FORMATS)} Format nodes")
        
        # FundingType
        for item in FUNDING_TYPES:
            self.execute("""
                CREATE (n:FundingType {id: $id, name: $name, description: $description})
            """, item)
        print(f"  - Created {len(FUNDING_TYPES)} FundingType nodes")
    
    def detect_fields(self, text: str) -> list[int]:
        """Detect relevant fields based on text content."""
        text_lower = text.lower()
        detected = []
        for field_id, keywords in FIELD_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    detected.append(field_id)
                    break
        return detected[:5]
    
    def detect_skills(self, text: str) -> list[int]:
        """Detect relevant skills based on text content."""
        text_lower = text.lower()
        detected = []
        for skill_id, keywords in SKILL_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    detected.append(skill_id)
                    break
        return detected[:5]
    
    def detect_format(self, text: str, tags: list) -> list[int]:
        """Detect format based on text and tags."""
        text_lower = text.lower()
        detected = []
        for format_id, keywords in FORMAT_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text_lower or keyword.lower() in tags:
                    detected.append(format_id)
                    break
        return detected
    
    def detect_funding(self, text: str, tags: list) -> list[int]:
        """Detect funding type based on text and tags."""
        text_lower = text.lower()
        detected = []
        for funding_id, keywords in FUNDING_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text_lower or keyword.lower() in tags:
                    detected.append(funding_id)
                    break
        return detected
    
    def get_or_create_organisation(self, name: str, is_nonprofit: bool = True) -> int:
        """Get existing organisation ID or create new one."""
        if name in self.organisations:
            return self.organisations[name]
        
        org_id = len(self.organisations) + 1
        
        self.execute("""
            CREATE (n:Organisation {id: $id, name: $name, isNonProfit: $isNonProfit})
        """, {"id": org_id, "name": name, "isNonProfit": is_nonprofit})
        
        self.organisations[name] = org_id
        return org_id
    
    def load_activities(self, json_path: str):
        """Load activities from JSON file."""
        print(f"Loading activities from {json_path}...")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        activities = data.get("activities", [])
        print(f"  Found {len(activities)} activities")
        
        for activity in activities:
            # Create Activity node
            metadata = activity.get("metadata", {})
            activity_id = activity["id"]
            name = activity["title"]
            short_desc = activity.get("short_description", "")
            long_desc = activity.get("long_description", "")
            created_at = activity.get("created_at", "")
            updated_at = activity.get("updated_at", "")
                        
            # Combined text for detection
            full_text = f"{name} {long_desc}"
            tags = activity.get("tags", []) + metadata.get("tags_extended", [])
            url = metadata.get("website_url", "")

            self.execute("""
                CREATE (a:Activity {
                    id: $id,
                    name: $name,
                    shortDescription: $shortDescription,
                    longDescription: $longDescription,
                    url: $url,
                    createdAt: $createdAt,
                    updatedAt: $updatedAt
                })
            """, {
                "id": activity_id,
                "name": name,
                "shortDescription": short_desc,
                "longDescription": long_desc,
                "url": url,
                "createdAt": created_at,
                "updatedAt": updated_at
            })
            
            # Create Organisation and ORGANIZED_BY relationship
            org_id = self.get_or_create_organisation(name)
            self.execute("""
                MATCH (a:Activity {id: $activity_id})
                MATCH (o:Organisation {id: $org_id})
                CREATE (a)-[:ORGANIZED_BY]->(o)
            """, {"activity_id": activity_id, "org_id": org_id})
            
            # AIMS_TO -> LevelOfStudy
            for edu_level in activity.get("education_level", []):
                code = EDUCATION_LEVEL_MAP.get(edu_level)
                if code:
                    self.execute("""
                        MATCH (a:Activity {id: $activity_id})
                        MATCH (l:LevelOfStudy {code: $code})
                        CREATE (a)-[:AIMS_TO]->(l)
                    """, {"activity_id": activity_id, "code": code})
            
            # HAS_TYPE -> ActivityType (from tags)
            for tag in tags:
                self.execute("""
                    MATCH (a:Activity {id: $activity_id})
                    MATCH (t:ActivityType {name: $tag})
                    CREATE (a)-[:HAS_TYPE]->(t)
                """, {"activity_id": activity_id, "tag": tag})
            
            # AVAILABLE_IN -> Location
            for loc_name in activity.get("location", []):
                loc_id = LOCATION_MAP.get(loc_name)
                if loc_id:
                    self.execute("""
                        MATCH (a:Activity {id: $activity_id})
                        MATCH (l:Location {id: $loc_id})
                        CREATE (a)-[:AVAILABLE_IN]->(l)
                    """, {"activity_id": activity_id, "loc_id": loc_id})
            
            # FOCUSES_ON -> Field (detected from text)
            field_ids = self.detect_fields(full_text)
            for field_id in field_ids:
                self.execute("""
                    MATCH (a:Activity {id: $activity_id})
                    MATCH (f:Field {id: $field_id})
                    CREATE (a)-[:FOCUSES_ON]->(f)
                """, {"activity_id": activity_id, "field_id": field_id})
            
            # REQUIRES -> Skill (detected from text)
            skill_ids = self.detect_skills(full_text)
            for skill_id in skill_ids:
                self.execute("""
                    MATCH (a:Activity {id: $activity_id})
                    MATCH (s:Skill {id: $skill_id})
                    CREATE (a)-[:REQUIRES]->(s)
                """, {"activity_id": activity_id, "skill_id": skill_id})
            
            # DELIVERED_AS -> Format (detected)
            format_ids = self.detect_format(full_text, tags)
            for format_id in format_ids:
                self.execute("""
                    MATCH (a:Activity {id: $activity_id})
                    MATCH (f:Format {id: $format_id})
                    CREATE (a)-[:DELIVERED_AS]->(f)
                """, {"activity_id": activity_id, "format_id": format_id})
            
            # FUNDED_BY -> FundingType (detected)
            funding_ids = self.detect_funding(full_text, tags)
            for funding_id in funding_ids:
                self.execute("""
                    MATCH (a:Activity {id: $activity_id})
                    MATCH (ft:FundingType {id: $funding_id})
                    CREATE (a)-[:FUNDED_BY]->(ft)
                """, {"activity_id": activity_id, "funding_id": funding_id})
        
        print(f"  Created {len(activities)} Activity nodes with relationships")
        print(f"  Created {len(self.organisations)} Organisation nodes")
        
    def create_organisation_relationships(self):
        """Create Organisation relationships (PARTNERS_WITH, OPERATES_IN)."""
        print("Creating organisation relationships...")
        
        # PARTNERS_WITH
        for org1_name, org2_name in ORGANISATION_PARTNERSHIPS:
            self.execute("""
                MATCH (o1:Organisation {name: $org1})
                MATCH (o2:Organisation {name: $org2})
                CREATE (o1)-[:PARTNERS_WITH]->(o2)
            """, {"org1": org1_name, "org2": org2_name})
        
        # OPERATES_IN - link organisations to locations based on their activities
        # Using MERGE instead of checking EXISTS (Memgraph compatible)
        self.execute("""
            MATCH (a:Activity)-[:ORGANIZED_BY]->(o:Organisation)
            MATCH (a)-[:AVAILABLE_IN]->(l:Location)
            MERGE (o)-[:OPERATES_IN]->(l)
        """)
        
        print("  Organisation relationships created")
        
    def print_statistics(self):
        """Print database statistics."""
        print("\n=== Database Statistics ===")
        
        node_counts = self.execute("""
            MATCH (n)
            RETURN labels(n)[0] AS label, count(*) AS count
            ORDER BY count DESC
        """)
        
        print("\nNode counts:")
        for record in node_counts:
            print(f"  {record['label']}: {record['count']}")
        
        rel_counts = self.execute("""
            MATCH ()-[r]->()
            RETURN type(r) AS type, count(*) AS count
            ORDER BY count DESC
        """)
        
        print("\nRelationship counts:")
        for record in rel_counts:
            print(f"  {record['type']}: {record['count']}")


def main():
    parser = argparse.ArgumentParser(description="Load graph data into Memgraph")
    parser.add_argument("--clear", action="store_true", help="Clear existing data before loading")
    args = parser.parse_args()
    
    # Get the path to activities_real.json
    script_dir = Path(__file__).parent
    json_path = script_dir / "activities_real.json"
    
    if not json_path.exists():
        print(f"Error: {json_path} not found")
        return 1
    
    print(f"Connecting to graph database at {GRAPH_URI}...")
    loader = GraphLoader(GRAPH_URI, GRAPH_USER, GRAPH_PASSWORD)
    
    try:
        if args.clear:
            loader.clear_database()
        
        loader.create_constraints()
        loader.load_static_nodes()
        loader.load_activities(str(json_path))
        loader.create_organisation_relationships()
        loader.print_statistics()
        
        print("\n✓ Graph data loaded successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        raise
    finally:
        loader.close()
    
    return 0


if __name__ == "__main__":
    exit(main())

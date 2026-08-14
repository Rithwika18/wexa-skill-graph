import sys
from backend.graph.cognodb_client import get_cognodb_client
from backend.graph.queries import (
    UPSERT_PREREQUISITE_RELATIONSHIP,
    UPSERT_ROLE,
    UPSERT_ROLE_REQUIREMENT,
)
from backend.graph.sample_data import SAMPLE_RELATIONSHIPS, SAMPLE_ROLES


def seed_cognodb() -> bool:
    """Seed the CognoDB database with skills, prerequisite relationships, and career roles.

    Returns:
        bool: True if seeding completed successfully, False otherwise.
    """
    client = get_cognodb_client()

    print("Checking CognoDB connectivity...")
    connected, message = client.check_connectivity()
    if not connected:
        print(f"Cannot seed database: {message}", file=sys.stderr)
        return False

    print("Connected to CognoDB. Seeding skill graph and career roles data...")

    try:
        # 1. Seed prerequisite relationships
        rel_count = 0
        for from_skill, to_skill in SAMPLE_RELATIONSHIPS:
            params = {
                "from_name": from_skill,
                "to_name": to_skill,
            }
            client.execute_query(UPSERT_PREREQUISITE_RELATIONSHIP, parameters=params)
            rel_count += 1
            print(f"  [OK] Skill Relation: ({from_skill}) -[:PREREQUISITE_OF]-> ({to_skill})")

        # 2. Seed career roles and role requirements
        role_count = 0
        req_count = 0
        for role_title, role_data in SAMPLE_ROLES.items():
            client.execute_query(
                UPSERT_ROLE,
                parameters={
                    "title": role_title,
                    "domain": role_data["domain"],
                    "level": role_data["level"],
                }
            )
            role_count += 1
            print(f"  [OK] Role: (:Role {{title: '{role_title}', domain: '{role_data['domain']}'}})")

            for skill_name, importance in role_data["skills"]:
                client.execute_query(
                    UPSERT_ROLE_REQUIREMENT,
                    parameters={
                        "title": role_title,
                        "skill_name": skill_name,
                        "importance": importance,
                    }
                )
                req_count += 1
                print(f"    -> Requires: ({role_title}) -[:REQUIRES {{importance: '{importance}'}}]-> ({skill_name})")

        print(f"\nSeeding complete: {rel_count} skill relations, {role_count} roles, {req_count} requirements upserted.")
        return True
    except Exception as e:
        print(f"Seeding failed: {type(e).__name__}", file=sys.stderr)
        return False
    finally:
        client.close()


if __name__ == "__main__":
    success = seed_cognodb()
    sys.exit(0 if success else 1)

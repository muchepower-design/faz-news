# ============================================================
# seed_national_team_age_groups.py
#
# Creates age-group national teams from the existing
# Senior national team records already stored in
# the national_teams table.
#
# It DOES NOT use a hardcoded list of countries.
#
# Existing source records:
#   - Senior Men
#   - Senior Women
#
# New records created:
#   - Under 23 Men
#   - Under 23 Women
#   - Under 20 Men
#   - Under 20 Women
#   - Under 17 Men
#   - Under 17 Women
#   - Under 15 Men
#   - Under 15 Women
#
# IMPORTANT:
#   age and age_group will contain exactly the same value.
#
# Example:
#
#   Existing:
#       Zambia Men's National Team
#       gender = Male
#       age = Senior
#       age_group = Senior Men
#
#   New:
#       Same Zambia record information
#       gender = Male
#       age = Under 23
#       age_group = Under 23
#
#       Same Zambia record information
#       gender = Male
#       age = Under 20
#       age_group = Under 20
#
#       Same Zambia record information
#       gender = Male
#       age = Under 17
#       age_group = Under 17
#
#       Same Zambia record information
#       gender = Male
#       age = Under 15
#       age_group = Under 15
#
# The same is done for the Female record.
#
# Duplicate protection:
#   A new record will NOT be inserted if a record already exists
#   for the same:
#
#       country_id + gender + age_group
#
# ============================================================


import sys
import os


# ============================================================
# ADD BACKEND DIRECTORY TO PYTHON PATH
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


# ============================================================
# IMPORT FLASK APPLICATION
# ============================================================

from app import create_app, db

from app.models.national_team import NationalTeam


# ============================================================
# AGE GROUPS TO CREATE
# ============================================================

AGE_GROUPS = [
    "Under 23",
    "Under 20",
    "Under 17",
    "Under 15",
]


# ============================================================
# FIND EXISTING TEAM
# ============================================================

def team_already_exists(country_id, gender, age_group):
    """
    Check whether a national team already exists for:

        country + gender + age_group

    This prevents duplicate records.
    """

    return NationalTeam.query.filter_by(
        country_id=country_id,
        gender=gender,
        age_group=age_group
    ).first()


# ============================================================
# CREATE AGE-GROUP TEAM
# ============================================================

def create_age_group_team(senior_team, age_group):
    """
    Create one age-group national team from an existing
    Senior national team.

    All existing information is copied from the Senior record.

    Only:
        age
        age_group

    are changed.

    The name and short_name are also changed so that the
    database records can be clearly identified by age group.
    """

    country_id = senior_team.country_id
    gender = senior_team.gender

    # --------------------------------------------------------
    # Check for duplicate
    # --------------------------------------------------------

    existing_team = team_already_exists(
        country_id=country_id,
        gender=gender,
        age_group=age_group
    )

    if existing_team:

        print(
            f"⏭️ Already exists: "
            f"{senior_team.short_name} "
            f"{gender} "
            f"{age_group}"
        )

        return "exists"


    # --------------------------------------------------------
    # Determine gender-specific name
    # --------------------------------------------------------

    if gender == "Male":

        new_name = (
            f"{senior_team.country.name} "
            f"Men's National Team"
        )

        new_short_name = (
            f"{senior_team.country.name} Men"
        )

    else:

        new_name = (
            f"{senior_team.country.name} "
            f"Women's National Team"
        )

        new_short_name = (
            f"{senior_team.country.name} Women"
        )


    # --------------------------------------------------------
    # Create new record
    # --------------------------------------------------------

    new_team = NationalTeam(

        # Same country
        country_id=senior_team.country_id,

        # Same basic team information
        name=new_name,
        short_name=new_short_name,

        # Same gender
        gender=senior_team.gender,

        # IMPORTANT:
        # age and age_group are identical
        age=age_group,
        age_group=age_group,

        # Copy existing information
        nickname=senior_team.nickname,
        fifa_code=senior_team.fifa_code,
        flag_image_url=senior_team.flag_image_url
    )

    db.session.add(new_team)

    return "created"


# ============================================================
# MAIN SEEDER
# ============================================================

def seed_national_team_age_groups():

    print()
    print("=" * 75)
    print(" NATIONAL TEAM AGE-GROUP SEEDER")
    print("=" * 75)
    print()

    # --------------------------------------------------------
    # Get existing Senior records
    # --------------------------------------------------------
    #
    # We deliberately use only Senior records as the source.
    #
    # This prevents the script from creating:
    #
    # Under 23 → Under 23 → Under 23 → ...
    #
    # on subsequent executions.
    #
    # --------------------------------------------------------

    senior_teams = NationalTeam.query.filter_by(
        age="Senior"
    ).all()


    print(
        f"Senior national teams found: "
        f"{len(senior_teams)}"
    )

    print()


    if not senior_teams:

        print("=" * 75)
        print("⚠️ NO SENIOR TEAMS FOUND")
        print("=" * 75)
        print()
        print(
            "The national_teams table does not contain "
            "any records where age = 'Senior'."
        )
        print()
        return


    # --------------------------------------------------------
    # Counters
    # --------------------------------------------------------

    created = 0
    existing = 0
    failed = 0


    # --------------------------------------------------------
    # Process each Senior team
    # --------------------------------------------------------

    for senior_team in senior_teams:

        print(
            f"Processing: "
            f"{senior_team.short_name} "
            f"({senior_team.gender})"
        )

        # ----------------------------------------------------
        # Create all required age groups
        # ----------------------------------------------------

        for age_group in AGE_GROUPS:

            try:

                result = create_age_group_team(
                    senior_team=senior_team,
                    age_group=age_group
                )


                if result == "created":

                    created += 1

                    print(
                        f"   ✅ Created: "
                        f"{age_group}"
                    )


                elif result == "exists":

                    existing += 1


            except Exception as e:

                failed += 1

                print(
                    f"   ❌ Failed: "
                    f"{age_group}"
                )

                print(
                    f"      Error: {str(e)}"
                )


        print()


    # --------------------------------------------------------
    # Save changes
    # --------------------------------------------------------

    try:

        db.session.commit()


        print()
        print("=" * 75)
        print(" SEEDING COMPLETED")
        print("=" * 75)
        print()

        print(
            f"Senior records used     : "
            f"{len(senior_teams)}"
        )

        print(
            f"Age groups requested     : "
            f"{len(AGE_GROUPS)}"
        )

        print(
            f"New teams created       : "
            f"{created}"
        )

        print(
            f"Already existed         : "
            f"{existing}"
        )

        print(
            f"Failed                  : "
            f"{failed}"
        )

        print()

        # ----------------------------------------------------
        # Expected number
        # ----------------------------------------------------

        expected_new = (
            len(senior_teams) *
            len(AGE_GROUPS)
        )

        print(
            f"Expected new records    : "
            f"{expected_new}"
        )

        print()


        # ----------------------------------------------------
        # Current database count
        # ----------------------------------------------------

        total_teams = NationalTeam.query.count()

        print(
            f"National teams in DB    : "
            f"{total_teams}"
        )

        print()


        # ----------------------------------------------------
        # Age-group counts
        # ----------------------------------------------------

        print("=" * 75)
        print(" AGE-GROUP SUMMARY")
        print("=" * 75)
        print()

        for age_group in AGE_GROUPS:

            male_count = NationalTeam.query.filter_by(
                age_group=age_group,
                gender="Male"
            ).count()

            female_count = NationalTeam.query.filter_by(
                age_group=age_group,
                gender="Female"
            ).count()

            total_count = (
                male_count +
                female_count
            )

            print(
                f"{age_group:<12} "
                f"Male: {male_count:<5} "
                f"Female: {female_count:<5} "
                f"Total: {total_count}"
            )

        print()


        # ----------------------------------------------------
        # Final expected total
        # ----------------------------------------------------

        print("=" * 75)
        print(" FINAL DATABASE SUMMARY")
        print("=" * 75)
        print()

        senior_count = NationalTeam.query.filter_by(
            age="Senior"
        ).count()

        youth_count = NationalTeam.query.filter(
            NationalTeam.age.in_(AGE_GROUPS)
        ).count()

        print(
            f"Senior teams             : "
            f"{senior_count}"
        )

        print(
            f"Under-age teams          : "
            f"{youth_count}"
        )

        print(
            f"Total national teams     : "
            f"{senior_count + youth_count}"
        )

        print()


        if failed == 0:

            print(
                "✅ All age groups processed successfully."
            )

        else:

            print(
                f"⚠️ Completed with {failed} failed records."
            )

        print()


    except Exception as e:

        db.session.rollback()

        print()
        print("=" * 75)
        print("❌ SEEDING FAILED")
        print("=" * 75)
        print()

        print(str(e))

        print()

        raise


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":

    app = create_app()

    with app.app_context():

        seed_national_team_age_groups()

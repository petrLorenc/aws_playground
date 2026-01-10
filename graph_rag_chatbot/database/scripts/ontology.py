"""
Dummy and static data for graph database nodes.
This file contains predefined data for nodes that don't come directly from activities_real.json
"""

# LevelOfStudy - maps from education_level in JSON
LEVELS_OF_STUDY = [
    {"id": 1, "name": "Základní škola", "code": "student_zs"},
    {"id": 2, "name": "Střední škola", "code": "student_ss"},
    {"id": 3, "name": "Vysoká škola", "code": "student_vs"},
]

# Mapping from JSON education_level to our codes
EDUCATION_LEVEL_MAP = {
    "student zš": "student_zs",
    "student sš": "student_ss",
    "student vš": "student_vs",
}

# ActivityType - maps from tags in JSON
ACTIVITY_TYPES = [
    {
        "id": 1,
        "name": "soutěž",
        "description": "Soutěžní aktivity a olympiády",
        "parent_id": None,
    },
    {
        "id": 2,
        "name": "dobrovolnictví",
        "description": "Dobrovolnické programy a akce",
        "parent_id": None,
    },
    {
        "id": 3,
        "name": "osobní rozvoj",
        "description": "Aktivity zaměřené na rozvoj osobnosti",
        "parent_id": None,
    },
    {
        "id": 4,
        "name": "stáž",
        "description": "Pracovní stáže a praxe",
        "parent_id": None,
    },
    {
        "id": 5,
        "name": "výjezd do zahraničí",
        "description": "Zahraniční pobyty a výměny",
        "parent_id": None,
    },
    {
        "id": 6,
        "name": "kurz",
        "description": "Vzdělávací kurzy a workshopy",
        "parent_id": 3,
    },  # parent: osobní rozvoj
    {
        "id": 7,
        "name": "stipendium",
        "description": "Stipendijní programy",
        "parent_id": 5,
    },  # parent: výjezd do zahraničí
    {
        "id": 8,
        "name": "studium v čr",
        "description": "Studijní programy v ČR",
        "parent_id": None,
    },
    {
        "id": 9,
        "name": "dobrovolnická centra v čr",
        "description": "Centra koordinující dobrovolnictví",
        "parent_id": 2,
    },  # parent: dobrovolnictví
    {
        "id": 10,
        "name": "inspirativní stránky",
        "description": "Informační a inspirativní zdroje",
        "parent_id": None,
    },
    {
        "id": 11,
        "name": "odkazy",
        "description": "Rozcestníky a odkazy",
        "parent_id": None,
    },
]

# Location - Czech regions + special locations
LOCATIONS = [
    {"id": 1, "name": "Praha", "type": "region", "parent_id": 15},
    {"id": 2, "name": "Jihomoravský kraj", "type": "region", "parent_id": 15},
    {"id": 3, "name": "Středočeský kraj", "type": "region", "parent_id": 15},
    {"id": 4, "name": "Moravskoslezský kraj", "type": "region", "parent_id": 15},
    {"id": 5, "name": "Olomoucký kraj", "type": "region", "parent_id": 15},
    {"id": 6, "name": "Plzeňský kraj", "type": "region", "parent_id": 15},
    {"id": 7, "name": "Jihočeský kraj", "type": "region", "parent_id": 15},
    {"id": 8, "name": "Královehradecký kraj", "type": "region", "parent_id": 15},
    {"id": 9, "name": "Pardubický kraj", "type": "region", "parent_id": 15},
    {"id": 10, "name": "Liberecký kraj", "type": "region", "parent_id": 15},
    {"id": 11, "name": "Ústecký kraj", "type": "region", "parent_id": 15},
    {"id": 12, "name": "Karlovarský kraj", "type": "region", "parent_id": 15},
    {"id": 13, "name": "Zlínský kraj", "type": "region", "parent_id": 15},
    {"id": 14, "name": "Kraj Vysočina", "type": "region", "parent_id": 15},
    {"id": 15, "name": "Česká republika", "type": "country", "parent_id": None},
    {"id": 16, "name": "Online", "type": "virtual", "parent_id": None},
    {"id": 17, "name": "Zahraničí", "type": "abroad", "parent_id": None},
    {"id": 18, "name": "celá ČR/online", "type": "nationwide", "parent_id": 15},
]

# Mapping from JSON location strings to our location IDs
LOCATION_MAP = {
    "Praha": 1,
    "Jihomoravský kraj": 2,
    "Středočeský kraj": 3,
    "Moravskoslezský kraj": 4,
    "Olomoucký kraj": 5,
    "Plzeňský kraj": 6,
    "Jihočeský kraj": 7,
    "Královehradecký kraj": 8,
    "Pardubický kraj": 9,
    "Liberecký kraj": 10,
    "Ústecký kraj": 11,
    "Karlovarský kraj": 12,
    "Zlínský kraj": 13,
    "Kraj Vysočina": 14,
    "Zahraničí": 17,
    "celá ČR/online": 18,
}

# State - Countries (dummy data for abroad)
STATES = [
    {"id": 1, "shortcut": "CZ", "name": "Česká republika"},
    {"id": 2, "shortcut": "DE", "name": "Německo"},
    {"id": 3, "shortcut": "UK", "name": "Velká Británie"},
    {"id": 4, "shortcut": "US", "name": "USA"},
    {"id": 5, "shortcut": "AT", "name": "Rakousko"},
    {"id": 6, "shortcut": "IT", "name": "Itálie"},
    {"id": 7, "shortcut": "ES", "name": "Španělsko"},
    {"id": 8, "shortcut": "FR", "name": "Francie"},
    {"id": 9, "shortcut": "PL", "name": "Polsko"},
    {"id": 10, "shortcut": "SK", "name": "Slovensko"},
    {"id": 11, "shortcut": "NL", "name": "Nizozemsko"},
    {"id": 12, "shortcut": "BE", "name": "Belgie"},
    {"id": 13, "shortcut": "NO", "name": "Norsko"},
    {"id": 14, "shortcut": "SE", "name": "Švédsko"},
    {"id": 15, "shortcut": "IE", "name": "Irsko"},
]

# Skill
SKILLS = [
    {
        "id": 1,
        "name": "komunikace",
        "description": "Prezentační a komunikační dovednosti",
    },
    {"id": 2, "name": "týmová práce", "description": "Spolupráce v týmu"},
    {"id": 3, "name": "leadership", "description": "Vedení lidí a projektů"},
    {
        "id": 4,
        "name": "projektový management",
        "description": "Plánování a řízení projektů",
    },
    {"id": 5, "name": "jazyky", "description": "Jazykové dovednosti"},
    {
        "id": 6,
        "name": "vědecká práce",
        "description": "Výzkumné metody a vědecké psaní",
    },
    {
        "id": 7,
        "name": "grafika",
        "description": "Grafický design a vizuální komunikace",
    },
    {"id": 8, "name": "programování", "description": "IT a programovací dovednosti"},
    {"id": 9, "name": "psaní", "description": "Žurnalistika a kreativní psaní"},
    {"id": 10, "name": "public speaking", "description": "Veřejné vystupování"},
    {
        "id": 11,
        "name": "mezikulturní kompetence",
        "description": "Práce v mezinárodním prostředí",
    },
    {"id": 12, "name": "organizace akcí", "description": "Event management"},
    {"id": 13, "name": "mentoring", "description": "Práce s lidmi, koučink"},
    {"id": 14, "name": "administrativa", "description": "Administrativní dovednosti"},
    {"id": 15, "name": "networking", "description": "Budování kontaktů"},
]

# Job - Career paths
JOBS = [
    {"id": 1, "name": "Programátor", "averageSalary": 70000},
    {"id": 2, "name": "Vědec/Výzkumník", "averageSalary": 45000},
    {"id": 3, "name": "Novinář", "averageSalary": 40000},
    {"id": 4, "name": "Grafik", "averageSalary": 45000},
    {"id": 5, "name": "Projektový manažer", "averageSalary": 60000},
    {"id": 6, "name": "Učitel", "averageSalary": 38000},
    {"id": 7, "name": "Překladatel", "averageSalary": 42000},
    {"id": 8, "name": "Diplomat", "averageSalary": 55000},
    {"id": 9, "name": "NGO pracovník", "averageSalary": 35000},
    {"id": 10, "name": "Marketing specialista", "averageSalary": 50000},
    {"id": 11, "name": "Event manažer", "averageSalary": 45000},
    {"id": 12, "name": "HR specialista", "averageSalary": 48000},
    {"id": 13, "name": "Konzultant", "averageSalary": 65000},
    {"id": 14, "name": "Architekt", "averageSalary": 55000},
    {"id": 15, "name": "Podnikatel", "averageSalary": None},
]

# Skill -> Job mapping (which skills are useful for which jobs)
SKILL_JOB_MAPPING = [
    (8, 1),  # programování -> Programátor
    (6, 2),  # vědecká práce -> Vědec
    (9, 3),  # psaní -> Novinář
    (7, 4),  # grafika -> Grafik
    (4, 5),  # projektový management -> Projektový manažer
    (13, 6),  # mentoring -> Učitel
    (5, 7),  # jazyky -> Překladatel
    (11, 8),  # mezikulturní kompetence -> Diplomat
    (2, 9),  # týmová práce -> NGO pracovník
    (1, 10),  # komunikace -> Marketing specialista
    (12, 11),  # organizace akcí -> Event manažer
    (1, 12),  # komunikace -> HR specialista
    (10, 13),  # public speaking -> Konzultant
    (7, 14),  # grafika -> Architekt
    (3, 15),  # leadership -> Podnikatel
    (15, 15),  # networking -> Podnikatel
]

# Field - Thematic domains
FIELDS = [
    {
        "id": 1,
        "name": "věda a výzkum",
        "description": "Přírodní vědy, technologie, výzkum",
    },
    {
        "id": 2,
        "name": "humanitární práce",
        "description": "Pomoc potřebným, sociální práce",
    },
    {
        "id": 3,
        "name": "žurnalistika a média",
        "description": "Noviny, TV, online média",
    },
    {
        "id": 4,
        "name": "IT a technologie",
        "description": "Programování, digitální technologie",
    },
    {
        "id": 5,
        "name": "kultura a umění",
        "description": "Výtvarné umění, hudba, divadlo, design",
    },
    {"id": 6, "name": "životní prostředí", "description": "Ekologie, ochrana přírody"},
    {"id": 7, "name": "podnikání", "description": "Startupy, business, ekonomika"},
    {
        "id": 8,
        "name": "mezinárodní vztahy",
        "description": "Diplomacie, EU, zahraniční politika",
    },
    {"id": 9, "name": "vzdělávání", "description": "Pedagogika, výuka"},
    {
        "id": 10,
        "name": "sociální vědy",
        "description": "Historie, sociologie, politologie",
    },
    {"id": 11, "name": "zdravotnictví", "description": "Medicína, zdraví"},
    {
        "id": 12,
        "name": "právo a lidská práva",
        "description": "Právní oblast, aktivismus",
    },
]

# Format - Delivery formats
FORMATS = [
    {"id": 1, "name": "jednorázová akce", "durationCategory": "short"},
    {"id": 2, "name": "víkendovka", "durationCategory": "short"},
    {"id": 3, "name": "týdenní program", "durationCategory": "short"},
    {"id": 4, "name": "měsíční program", "durationCategory": "medium"},
    {"id": 5, "name": "semestrální", "durationCategory": "long"},
    {"id": 6, "name": "roční", "durationCategory": "long"},
    {"id": 7, "name": "průběžné", "durationCategory": "ongoing"},
    {"id": 8, "name": "online kurz", "durationCategory": "flexible"},
    {"id": 9, "name": "prezenční", "durationCategory": "in-person"},
    {"id": 10, "name": "hybridní", "durationCategory": "hybrid"},
]

# FundingType - Financial support types
FUNDING_TYPES = [
    {"id": 1, "name": "zdarma", "description": "Aktivita je zcela bezplatná"},
    {"id": 2, "name": "plné stipendium", "description": "Pokryje všechny náklady"},
    {"id": 3, "name": "částečné stipendium", "description": "Pokryje část nákladů"},
    {"id": 4, "name": "grant", "description": "Jednorázová finanční podpora"},
    {"id": 5, "name": "placená účast", "description": "Účastník platí poplatek"},
    {"id": 6, "name": "placená stáž", "description": "Stáž s finančním ohodnocením"},
    {"id": 7, "name": "neplacená", "description": "Bez finančního ohodnocení"},
    {"id": 8, "name": "Erasmus+", "description": "Financováno z programu Erasmus+"},
]

FUNDING_KEYWORDS = {
    1: ["zdarma", "free of charge", "no cost"],  # zdarma
    2: ["plné stipendium", "full scholarship", "fully funded"],  # plné stipendium
    3: [
        "částečné stipendium",
        "partial scholarship",
        "partially funded",
    ],  # částečné stipendium
    4: ["grant", "financial support", "funding"],  # grant
    5: ["placená účast", "paid participation", "fee"],  # placená účast
    6: ["placená stáž", "paid internship", "paid placement"],  # placená stáž
    7: ["neplacená", "unpaid", "voluntary"],  # neplacená
    8: ["Erasmus+", "Erasmus plus", "Erasmus programme"],  # Erasmus+
}

FORMAT_KEYWORDS = {
    1: ["jednoráz", "one-time", "event"],  # jednorázová akce
    2: ["víkend", "weekend"],  # víkendovka
    3: ["týden", "week-long"],  # týdenní program
    4: ["měsíc", "month-long"],  # měsíční program
    5: ["semestr", "semester-long"],  # semestrální
    6: ["rok", "year-long"],  # roční
    7: ["průběžn", "ongoing", "continuous"],  # průběžné
    8: ["online kurz", "e-learning", "online course"],  # online kurz
    9: ["prezenční", "in-person", "on-site"],  # prezenční
    10: ["hybridní", "hybrid"],  # hybridní
}

# Keywords for Field detection (used in load_graph.py)
FIELD_KEYWORDS = {
    1: [
        "věd",
        "výzkum",
        "science",
        "research",
        "laborat",
        "experiment",
    ],  # věda a výzkum
    2: ["humanit", "pomoc", "sociál", "dobrovoln", "charit"],  # humanitární práce
    3: ["žurnalist", "novin", "média", "redak", "journalism"],  # žurnalistika
    4: [
        "IT",
        "program",
        "techno",
        "digital",
        "software",
        "coding",
        "python",
        "web",
    ],  # IT
    5: ["umění", "kultur", "design", "art", "creative", "hudba", "divadl"],  # kultura
    6: ["environment", "ekolog", "přír", "sustain", "climat"],  # životní prostředí
    7: ["podnik", "startup", "business", "ekonom", "entrepreneur"],  # podnikání
    8: [
        "mezinárodn",
        "diplomat",
        "EU",
        "zahranič",
        "international",
    ],  # mezinárodní vztahy
    9: ["vzděláv", "pedagog", "učit", "škol", "education", "teach"],  # vzdělávání
    10: ["histor", "sociolog", "politolog", "společ"],  # sociální vědy
    11: ["zdrav", "medicín", "lékař", "health"],  # zdravotnictví
    12: ["práv", "lidsk", "human rights", "legal", "aktivis"],  # právo a lidská práva
}

# Keywords for Skill detection (used in load_graph.py)
SKILL_KEYWORDS = {
    1: ["komunikac", "prezenta", "communication"],  # komunikace
    2: ["tým", "team", "spolupráce"],  # týmová práce
    3: ["leader", "vedení", "vést", "řídí"],  # leadership
    4: ["projekt", "management", "plánování"],  # projektový management
    5: ["jazyk", "angličtin", "němčin", "language"],  # jazyky
    6: ["vědeck", "výzkum", "research", "science"],  # vědecká práce
    7: ["grafik", "design", "vizuál"],  # grafika
    8: ["program", "coding", "IT", "software"],  # programování
    9: ["psaní", "článk", "writing", "redak"],  # psaní
    10: ["vystup", "present", "speaking"],  # public speaking
    11: ["mezikultur", "intercultural", "international"],  # mezikulturní kompetence
    12: ["event", "akce", "organiz", "festival"],  # organizace akcí
    13: ["mentor", "coach", "podpor"],  # mentoring
    14: ["admin", "kancelář", "office"],  # administrativa
    15: ["network", "kontakt", "connections"],  # networking
}

# ============================================================================
# NEW NODE TYPES FOR LLM ENHANCEMENT
# ============================================================================

# Organisation partnerships (populate with LLM later)
ORGANISATION_PARTNERSHIPS = []

# Concept - Abstract concepts and themes extracted from activity descriptions
CONCEPTS = []  # Will be populated by LLM

# MentionedEntity - Other organizations, programs, competitions mentioned in descriptions
MENTIONED_ENTITIES = []  # Will be populated by LLM

# Technology - Tools, platforms, technologies mentioned
TECHNOLOGIES = []  # Will be populated by LLM

# ============================================================================
# RELATIONSHIP TYPE DEFINITIONS (for documentation)
# ============================================================================

RELATIONSHIP_TYPES = {
    # Existing relationships
    "ORGANIZED_BY": "Activity is organized by Organisation",
    "AIMS_TO": "Activity aims to LevelOfStudy",
    "HAS_TYPE": "Activity has ActivityType",
    "AVAILABLE_IN": "Activity available in Location",
    "FOCUSES_ON": "Activity focuses on Field",
    "REQUIRES": "Activity requires Skill",
    "DEVELOPS": "Activity develops Skill",
    "DELIVERED_AS": "Activity delivered as Format",
    "FUNDED_BY": "Activity funded by FundingType",
    "PARTNERS_WITH": "Organisation partners with Organisation",
    "OPERATES_IN": "Organisation operates in Location",
    "PARENT_OF": "ActivityType is parent of ActivityType",
    "LOCATED_IN": "Location is located in Location/State",
    "USED_IN": "Skill used in Job",
    # New LLM-generated relationships
    "MENTIONS": "Activity mentions MentionedEntity (org/program/competition)",
    "RELATES_TO": "Concept relates to Concept",
    "HAS_CONCEPT": "Activity has Concept",
    "USES_TECHNOLOGY": "Activity uses Technology",
    "PREPARES_FOR": "Activity prepares for Job/Field",
    # Activity-to-Activity relationships
    "SIMILAR_TO": "Activity is similar to Activity (with similarity score)",
    "LEADS_TO": "Activity leads to Activity (progression path)",
    "PREREQUISITE_FOR": "Activity is prerequisite for Activity",
    "COMPLEMENTS": "Activity complements Activity",
    "ALTERNATIVE_TO": "Activity is alternative to Activity",
}

# Skill name to ID mapping for easy lookup
SKILL_NAME_MAP = {x["name"]: x["id"] for x in SKILLS}

# Field name to ID mapping for easy lookup
FIELD_NAME_MAP = {x["name"]: x["id"] for x in FIELDS}

# Format name to ID mapping for easy lookup
FORMAT_NAME_MAP = {x["name"]: x["id"] for x in FORMATS}

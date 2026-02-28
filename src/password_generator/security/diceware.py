"""Diceware-style passphrase generation."""

import secrets
from pathlib import Path
from typing import Iterator

from .secrets_wrapper import SecureRandom


# EFF Large Wordlist (simplified subset for built-in)
DEFAULT_WORDLIST = [
    "abacus", "abdomen", "ability", "absorb", "abstract", "abuse", "academy",
    "accelerate", "accent", "access", "accident", "account", "accuracy",
    "accuse", "achieve", "acid", "acoustic", "acquire", "acrobat", "action",
    "active", "activity", "actual", "adapter", "addition", "address",
    "advance", "advantage", "adventure", "advertise", "advice", "advocate",
    "aerobic", "affect", "afford", "afraid", "africa", "agency", "agenda",
    "agree", "aircraft", "airport", "alcohol", "algebra", "algorithm",
    "alien", "alive", "alliance", "allow", "almost", "alone", "alpha",
    "already", "also", "alter", "always", "amazing", "ambient", "amber",
    "ambition", "amount", "ancient", "anchor", "android", "anger",
    "animal", "ankle", "announce", "annual", "another", "answer",
    "antenna", "anxiety", "anyone", "apart", "apology", "apparent",
    "appear", "apple", "appliance", "approve", "april", "architect",
    "arena", "argue", "arise", "armchair", "armor", "around", "arrange",
    "arrival", "arrow", "article", "artificial", "artist", "aspect",
    "aspire", "assemble", "asset", "assign", "assist", "assume", "asteroid",
    "athlete", "atlas", "atomic", "attach", "attack", "attempt", "attend",
    "attitude", "attorney", "attract", "auction", "audience", "author",
    "autumn", "avenue", "average", "avoid", "awake", "award", "awesome",
    "awkward", "axis", "baboon", "backbone", "bacon", "badge", "baggage",
    "balance", "balcony", "balloon", "bamboo", "banana", "bandage",
    "banking", "banquet", "barcode", "barrier", "baseball", "basement",
    "basket", "battery", "battle", "beacon", "beagle", "beast", "beauty",
    "become", "bedroom", "before", "behave", "behind", "belief", "belong",
    "benefit", "beside", "bestow", "betray", "beyond", "bicycle", "billing",
    "biology", "birthday", "biscuit", "bitter", "blackout", "bladder",
    "blender", "blessing", "blind", "blizzard", "blockade", "blossom",
    "blueprint", "blunder", "boiler", "bombard", "bonanza", "bookcase",
    "bookmark", "booster", "border", "boredom", "borrow", "botany",
    "bottle", "boulevard", "boundary", "bouquet", "bracelet", "brainstorm",
    "branch", "brave", "bread", "breakfast", "breath", "breeze", "bridge",
    "brief", "bright", "brilliant", "broad", "brother", "bubble", "bucket",
    "budget", "buffer", "building", "bulldog", "bullet", "bumper", "bundle",
    "buoyant", "burden", "burning", "business", "butter", "buzzard",
    "cabinet", "cable", "cafeteria", "calculate", "calendar", "caliber",
    "camera", "campus", "canal", "cancel", "candid", "candle", "cannon",
    "canopy", "canvas", "capable", "capital", "captain", "capture",
    "caravan", "carbon", "cardiac", "careful", "carnival", "carpet",
    "carrot", "cartoon", "cascade", "casino", "castle", "catalog",
    "catalyst", "category", "caution", "ceiling", "celebrate", "celestial",
    "celery", "cement", "census", "center", "central", "century", "ceramic",
    "ceremony", "certain", "chain", "challenge", "chamber", "champion",
    "chance", "change", "channel", "chapter", "character", "charge",
    "charity", "charming", "charter", "chase", "cheap", "check", "cheek",
    "cheerful", "chef", "chemical", "cherry", "chest", "chicken", "chief",
    "child", "chimney", "choice", "choose", "chronic", "cider", "cinema",
    "circle", "circuit", "citizen", "citrus", "civil", "claim", "clarify",
    "clash", "classic", "clause", "clay", "clean", "clear", "climate",
    "clinic", "clock", "close", "clothes", "cloud", "clown", "cluster",
    "coach", "coast", "coconut", "coffee", "cogent", "coherent", "coil",
    "coin", "collect", "college", "colony", "color", "column", "combat",
    "combine", "comedy", "comfort", "comic", "command", "comment",
    "commerce", "common", "compact", "company", "compare", "compass",
    "compete", "compile", "complex", "comply", "compose", "compute",
    "concept", "concern", "concert", "conduct", "confirm", "connect",
    "conquer", "consent", "conserve", "consider", "console", "constant",
    "consult", "consume", "contact", "contain", "content", "contest",
    "context", "control", "convert", "convey", "cooking", "copper",
    "coral", "cordial", "corner", "corpse", "correct", "cosmic", "costly",
    "cottage", "cotton", "couch", "council", "counter", "country",
    "courage", "course", "court", "cover", "cowboy", "coyote", "craft",
    "crash", "crazy", "cream", "create", "credit", "creek", "cricket",
    "criminal", "crisis", "critic", "crockery", "crowd", "crown",
    "crucial", "cruise", "crumble", "crunch", "crystal", "cubic", "culture",
    "curious", "current", "curtain", "curved", "custom", "cycle", "cynic",
    "dagger", "damage", "dampen", "dancer", "danger", "daring", "darkness",
    "data", "daughter", "daylight", "deadline", "dealer", "debate",
    "debris", "decade", "december", "decide", "decline", "decorate",
    "decrease", "dedicate", "default", "defend", "define", "degree",
    "deliver", "demand", "democracy", "density", "dental", "depart",
    "depend", "deposit", "depress", "depth", "deputy", "derive",
    "descend", "describe", "desert", "design", "desire", "desktop",
    "destroy", "detach", "detail", "detect", "develop", "device", "diagram",
    "diamond", "diary", "dictate", "diesel", "different", "digital",
    "dignity", "dilemma", "dinner", "dioxide", "diplomat", "direct",
    "disable", "disaster", "discard", "discover", "discuss", "disease",
    "disguise", "dismiss", "display", "distance", "district", "diverse",
    "divide", "divorce", "dizzy", "doctor", "dollar", "domain", "domestic",
    "dominant", "donate", "donkey", "double", "doubt", "dozen", "drag",
    "dragon", "drain", "drama", "drawer", "dream", "dress", "drift",
    "drink", "drive", "drone", "drop", "drought", "drowsy", "drum",
    "dryer", "duckling", "durable", "dynamic", "eagle", "early", "earn",
    "earth", "easily", "easter", "economy", "ecosystem", "educate",
    "effect", "effort", "eight", "either", "elbow", "elder", "election",
    "electric", "elegant", "element", "elephant", "elevator", "elite",
    "embargo", "embassy", "embrace", "emerald", "emerge", "emotion",
    "empire", "employ", "empty", "enable", "enact", "enchant", "encore",
    "encounter", "encourage", "energy", "enforce", "engage", "engine",
    "english", "engrave", "enhance", "enjoy", "enlarge", "enlist",
    "enough", "enrich", "ensure", "entertain", "entire", "entry",
    "envelope", "episode", "equal", "equator", "equip", "erase",
    "erect", "escape", "escort", "essence", "estate", "estimate",
    "eternal", "ethics", "evacuate", "evaluate", "evening", "event",
    "evidence", "evil", "evoke", "exact", "example", "exceed", "excite",
    "exclude", "excuse", "execute", "exercise", "exhaust", "exhibit",
    "exile", "exist", "exodus", "expand", "expect", "expense", "expert",
    "explain", "explode", "export", "express", "extend", "extra",
    "fabric", "facade", "factor", "factory", "faculty", "failure",
    "faint", "fair", "faith", "falcon", "fall", "false", "fame", "family",
    "famous", "fancy", "fantasy", "farmer", "fashion", "fasten", "fatal",
    "father", "fault", "favor", "feature", "federal", "feeble", "feeling",
    "fellow", "female", "fence", "festival", "fever", "fewer", "fiber",
    "fiction", "field", "fifteen", "fifty", "fight", "figure", "filter",
    "final", "finance", "finding", "finger", "finish", "fire", "firm",
    "first", "fiscal", "fishing", "fitness", "flame", "flash", "flavor",
    "flesh", "flight", "float", "flock", "floor", "flour", "flower",
    "fluid", "flush", "focus", "foggy", "folder", "follow", "football",
    "force", "foreign", "forest", "forget", "formal", "format", "former",
    "fortune", "forum", "forward", "fossil", "foster", "fountain",
    "fourth", "fragile", "frame", "freedom", "freeze", "frequent",
    "fresh", "friend", "fright", "fringe", "front", "frost", "frozen",
    "fruit", "fuel", "fully", "function", "funding", "funeral", "funnel",
    "funny", "future", "gadget", "galaxy", "gallery", "gallon", "gambit",
    "gamble", "gaming", "garage", "garden", "garlic", "garment", "gases",
    "gather", "gender", "general", "genius", "gentle", "genuine",
    "gesture", "ghost", "giant", "gifted", "giraffe", "glacier", "glance",
    "glare", "glass", "glide", "global", "gloom", "glory", "glossary",
    "glove", "gluten", "gnome", "goal", "goblin", "gold", "golf",
    "goodbye", "goodness", "gorilla", "gospel", "gossip", "govern",
    "gracious", "grade", "graduate", "graffiti", "grand", "grant",
    "grape", "graph", "grasp", "grass", "grateful", "gravity", "gravy",
    "great", "green", "greet", "grief", "griffin", "grill", "grip",
    "grocery", "ground", "group", "growth", "guard", "guest", "guide",
    "guilty", "guitar", "gumbo", "habit", "hacker", "haggard", "halo",
    "handbook", "handle", "harbor", "hardware", "harmony", "harvest",
    "hasty", "hatch", "hazard", "heading", "healthy", "hearing", "heart",
    "heaven", "hedge", "height", "helicopter", "helmet", "helpful",
    "hence", "herald", "herbal", "herd", "heritage", "heroic", "hidden",
    "hierarchy", "highway", "hijack", "hiking", "hinder", "history",
    "hobby", "hockey", "holder", "holiday", "holler", "hollow", "holy",
    "homage", "honest", "honey", "honor", "horizon", "horn", "horror",
    "horse", "hospice", "hostage", "hostile", "hotel", "hour", "house",
    "hover", "human", "humble", "humor", "hundred", "hunger", "hunter",
    "hurdle", "hurry", "hybrid", "hypnotic", "iceberg", "icicle", "icon",
    "idea", "ideal", "identify", "idiom", "ignite", "ignore", "illegal",
    "illness", "image", "imagine", "imitate", "immense", "immune",
    "impact", "imperfect", "imply", "import", "impose", "impress",
    "improve", "impulse", "income", "increase", "index", "indicate",
    "indoor", "induce", "industry", "infant", "infect", "inferno",
    "infirm", "influence", "inform", "ingest", "inhabit", "inhale",
    "initial", "inject", "injury", "inmate", "innate", "inner", "input",
    "inquiry", "insect", "insert", "inside", "insight", "insist",
    "inspect", "inspire", "install", "instant", "instead", "instinct",
    "instruct", "insult", "intact", "intake", "integer", "integrate",
    "intend", "intense", "interact", "interest", "interim", "internal",
    "internet", "introduce", "invade", "invent", "invest", "invite",
    "involve", "ironic", "irony", "island", "isolate", "issue", "itself",
    "ivory", "jacket", "jaguar", "january", "jealous", "jellyfish",
    "jeopardy", "jersey", "jest", "jetty", "jewel", "jigsaw", "jingle",
    "jitter", "jockey", "jogging", "john", "join", "joint", "jolly",
    "journal", "journey", "jovial", "joyful", "judge", "juice", "july",
    "jumble", "jump", "jungle", "junior", "junk", "jury", "justice",
    "justify", "kangaroo", "karate", "keen", "keeper", "kernel", "kettle",
    "keyboard", "kidney", "kindness", "kinetic", "kingdom", "kiosk",
    "kitchen", "kitten", "kiwi", "knapsack", "kneel", "knife", "knight",
    "knit", "knock", "knot", "knowing", "kosher",
]


def load_wordlist(path: str | None = None) -> list[str]:
    """Load a wordlist from file or return default.
    
    Args:
        path: Path to wordlist file (one word per line).
        
    Returns:
        List of words.
    """
    if path is None:
        return DEFAULT_WORDLIST
    
    wordlist_path = Path(path)
    if wordlist_path.exists():
        with open(wordlist_path) as f:
            return [line.strip().lower() for line in f if line.strip()]
    
    return DEFAULT_WORDLIST


class DicewareGenerator:
    """Generate diceware-style passphrases."""
    
    def __init__(
        self,
        wordlist: list[str] | None = None,
        separator: str = "-",
        capitalize: bool = False,
        append_number: bool = False,
    ):
        """Initialize diceware generator.
        
        Args:
            wordlist: List of words to use.
            separator: Word separator.
            capitalize: Capitalize each word.
            append_number: Append random number to passphrase.
        """
        self.wordlist = wordlist or DEFAULT_WORDLIST
        self.separator = separator
        self.capitalize = capitalize
        self.append_number = append_number
    
    def generate(
        self,
        word_count: int = 6,
        num_passphrases: int = 1,
    ) -> Iterator[str]:
        """Generate passphrase(s).
        
        Args:
            word_count: Number of words per passphrase.
            num_passphrases: Number of passphrases to generate.
            
        Yields:
            Generated passphrases.
        """
        for _ in range(num_passphrases):
            words = [
                SecureRandom.choice(self.wordlist)
                for _ in range(word_count)
            ]
            
            if self.capitalize:
                words = [w.capitalize() for w in words]
            
            passphrase = self.separator.join(words)
            
            if self.append_number:
                passphrase += self.separator + str(secrets.randbelow(100))
            
            yield passphrase
    
    def generate_xkcd_style(
        self,
        word_count: int = 4,
        separator: str = " ",
    ) -> str:
        """Generate xkcd-style passphrase (4 random common words).
        
        Args:
            word_count: Number of words (default 4 for xkcd style).
            separator: Word separator.
            
        Returns:
            Generated passphrase.
        """
        # Use shorter, more common words for xkcd style
        common_words = [w for w in self.wordlist if 4 <= len(w) <= 8]
        
        words = [
            SecureRandom.choice(common_words)
            for _ in range(word_count)
        ]
        
        return separator.join(words)


import re
import string
COMMAND_INITIATORS = [
    r"can you",
    r"could you",
    r"please",
    r"would you",
    r"i want you to",
    r"vera",          # addressing the assistant
    r"hey vera",
]

FILLER_WORDS = r"(please|just|kindly|go ahead and)?"
REQUEST_PATTERNS = [
    r"you could",
    r"you can",
    r"you would",
    r"do you think.*you could",
    r"would it be possible.*to",
    r"is it possible.*to",
]

COMMAND_VERBS = [
    "exit",
    "pause",
    "open",
    "play",
    "stop",
    "resume",
    "search",
    "check",
    "close",
    "increase",
    "decrease",
    "turn",
    "shut down",
    "unpause"
]
# TIME_PATTERNS = [
#     r"what'?s the time",
#     r"what time is it",
#     r"what is the time",
# ]

# DATE_PATTERNS = [
#     r"what'?s today'?s date",
#     r"what date is it",
#     r"what is the date",
# ]

def is_command(text: str) -> bool:
    t = text.lower().strip()

    # -------------------------
    # 1. Direct time/date queries
    # -------------------------
    # for pattern in TIME_PATTERNS:
    #     if re.search(rf"\b{pattern}\b", t):
    #         return True

    # for pattern in DATE_PATTERNS:
    #     if re.search(rf"\b{pattern}\b", t):
    #         return True

    # -------------------------
    # 2. Direct imperative (verb appears first)
    # -------------------------
    words = t.split()
    if words:
        first = words[0].strip(string.punctuation)
        if first in COMMAND_VERBS:
            return True

    # -------------------------
    # 3. Initiator phrase followed by command verb AFTER the initiator
    # -------------------------
    for phrase in COMMAND_INITIATORS:
        for verb in COMMAND_VERBS:
            pattern = rf"\b{phrase}\b\s+{FILLER_WORDS}\s*\b{verb}\b"
            if re.search(pattern, t):
                return True
    for pattern in REQUEST_PATTERNS:
        m = re.search(pattern, t)
        if m:
            start = m.end()
            for verb in COMMAND_VERBS:
                if re.search(rf"\b{verb}\b", t[start:]):
                    return True
    # -------------------------
    # 4. Addressing VERA at the start
    # -------------------------
    if t.startswith("vera"):
        after_vera = t[len("vera"):]
        for verb in COMMAND_VERBS:
            if re.search(rf"\b{verb}\b", after_vera):
                return True

    return False
# -------------------------
# TEST FOR INTENT
# -------------------------
# print(is_command("can you please exit"))           
# print(is_command("Vera, exit"))                   
# print(is_command("can you exit"))                  
# print(is_command("Exit, please vera"))         

# print(is_command("Vera, you know what happened"))
# print(is_command("my friends were exiting..."))   
# print(is_command("I was thinking about exiting"))  

# print(is_command("can you please tell me the time?"))
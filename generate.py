from dataclasses import dataclass
import json
import sys

@dataclass
class Verb:
  do: str
  does: str
  dont: str
  doesnt: str
  did: str
  didnt: str
  was: str = None
  wasnt: str = None
  am: str = None
  aint: str = None
  be: str = None

  def infinitive(self):
    return self.be or self.do

  def conjugate(self, pronoun, past, neg):
    third = pronoun in ("he", "she", "there", "it", "this", "that", "")
    if past and neg:
      return third and self.wasnt or self.didnt \
        or DO.conjugate(pronoun, past, neg) + " " + self.infinitive()
    elif past:
      return third and self.was or self.did
    elif neg and pronoun == "I" and self.aint:
      return self.aint
    elif neg and third:
      return self.doesnt or DO.conjugate(pronoun, past, neg) + " " + self.infinitive()
    elif neg:
      return self.dont or DO.conjugate(pronoun, past, neg) + " " + self.infinitive()
    elif pronoun == "I" and self.am:
      return self.am
    elif third:
      return self.does
    else:
      return self.do


BE        = Verb("are",   "is",     "aren't",   "isn't",    "were",    "weren't", "was", "wasn't", "am", "'m not", "be")
BE_CLITIC = Verb("'re",   "'s",     "aren't",   "isn't",    "were",    "weren't", "was", "wasn't", "'m", "'m not", "be")
DO        = Verb("do",    "does",   "don't",    "doesn't",  "did",     "didn't")
HAVE_AUX  = Verb("have",  "has",    "haven't",  "hasn't",   "had",     "hadn't")
HAVE      = Verb("have",  "has",    None,       None,       "had",     None)
MAY       = Verb("may",   "may",    "mayn't",   "mayn't",   "might",   "mightn't")
MIGHT     = Verb("might", "might",  "mayn't",   "mightn't", None,      None)
WILL      = Verb("will",  "will",   "won't",    "won't",    "would",   "wouldn't")
CAN       = Verb("can",   "can",    "can't",    "can't",    "could",   "couldn't")
SHALL     = Verb("shall", "shall",  "shan't",   "shan't",   "should",  "shouldn't")
KNOW      = Verb("know",  "knows",  None,       None,       "knew",    None)
SEEM      = Verb("seem",  "seems",  None,       None,       "seemed",  None)
TRY       = Verb("try",   "tries",  None,       None,       "tried",   None)
THINK     = Verb("think", "thinks", None,       None,       "thought", None)
WANT      = Verb("want",  "wants",  None,       None,       "wanted",  None)
WERE      = Verb("were",  "were",   "weren't",  "weren't",  None,      None)
NO_VERB   = Verb("",      "",       None,       None,       "'d",      None)

starters = [
  ("SKP", "and", None),
  ("SKPW", "but", None),
  ("SKHR", "can", CAN),
  ("STKH", "do", DO),
  ("SKPH", "how", None),
  ("STPR", "if", None),
  ("STH", "that", None),
  ("SWH", "what", None),
  ("SWHR", "where", None),
  ("SKH", "which", None),
  ("SWR", "why", None),
  ("TWR", "", None),
]

pronouns = [
  ("EU", "I"),
  ("AOE", "we"),
  ("U", "you"),
  ("E", "he"),
  ("AE", "she"),
  ("AEU", "they"),
  ("A", "that"),
  ("AU", "there"),
  ("O", "it"),
  ("OEU", "this"),
  ("-", ""),
]

verbs = [
  ("R", "%s", BE),
  ("B", "%s", BE),
  ("BG", "%s", CAN),
  ("FR", "%s", DO),
  ("F", "%s", HAVE_AUX),
  ("FB", "%s been", HAVE_AUX),
  ("FT", "%s to", HAVE),
  ("S", "%s", BE_CLITIC),
  ("PB", "%s", KNOW),
  ("PBT", "%s that", KNOW),
  ("PL", "%s", MAY),
  ("PLT", "%s", MIGHT),
  ("FP", "%s", TRY),
  ("FPT", "%s to", TRY),
  ("FPL", "%s", SEEM),
  ("FPLT", "%s to", SEEM),
  ("RB", "%s", SHALL),
  ("PBG", "%s", THINK),
  ("PBGT", "%s that", THINK),
  ("L", "%s", WILL),
  ("P", "%s", WANT),
  ("PT", "%s to", WANT),
  ("RP", "%s", WERE),
  ("", "%s", NO_VERB),
]

phrases = {}

for s_pro, pro in pronouns:
  for s_starter, starter, early_verb in starters:
    for s_neg, neg in [("", False), ("*", True)]:
      for s_verb, verb_format, verb in verbs:
        for s_past, past in [("", False), ("D", True)]:
          for s_not, word_not in [("", ""), ("Z", "not")]:
            if s_neg and s_not: continue
            stroke = s_starter + s_pro + s_neg + s_verb + s_past + s_not
            stroke = stroke.replace("U*", "*U").replace("E*", "*E").replace("-*", "*").rstrip("-")
            if any(stroke.endswith(x) for x in "TZ SD TDZ TSZ TSD SDZ".split()): continue
            if early_verb:
              if verb not in (DO, HAVE, KNOW, SEEM, THINK, WANT, NO_VERB): continue
              does = early_verb.conjugate(pro, past, neg)
              phrase = [does, pro, verb_format % verb.infinitive(), word_not]
            else:
              conjugation = verb.conjugate(pro, past, neg)
              if conjugation is None: continue
              phrase = [starter, pro, verb_format % conjugation, word_not]
            phrase = " ".join(filter(None, phrase)).replace(" '", "'")
            if "mayn't" in phrase: continue
            phrases[stroke] = phrase

if __name__ == '__main__':
  if sys.argv[1:]:
    for name in sys.argv[1:]:
      print(name)
      with open(name, "rb") as f:
        for stroke, entry in json.load(f).items():
          if stroke in phrases and phrases[stroke] != entry:
            print(f"Conflict: {stroke} ==> \x1b[31m{phrases[stroke]!r}\x1b[0m or \x1b[32m{entry!r}\x1b[0m")
  else:
    print(len(phrases), file=sys.stderr)
    print(json.dumps(phrases, indent=2))


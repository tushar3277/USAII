import json
import random
from datetime import datetime, timedelta

# ================== CATEGORIES ==================
categories = {
    "toxicity": [
        "You are so {adj}, why do you even exist?",
        "Your {noun} is complete {adj} garbage, delete it.",
        "Shut up, you {adj} nobody cares about your {noun}.",
        "This is the most {adj} {noun} I've ever seen.",
        "You're {adj}, pathetic and everyone laughs at you.",
        "Go away, you {adj} person ruining the comments.",
        "Your face/voice is {adj} and makes me sick.",
        "Stop posting, you have no {adj} talent.",
        "What a {adj} waste of time and space.",
        "Just disappear already, you {adj} loser."
    ],

    "bullying": [
        "Everyone hates you, {insult}.",
        "Look at this {insult} trying to act cool.",
        "You have zero friends for a reason, {insult}.",
        "You're the ugliest kid here, {insult}.",
        "No one invited you, {insult}, stay away.",
        "Delete your account, {insult}.",
        "You're so fake, {insult}, everyone talks behind your back.",
        "You'll always be alone, {insult}.",
        "Go cry to your parents, {insult}.",
        "You're the joke of the school, {insult}.",
        "Nobody wants to be around you, {insult}.",
        "Everyone laughs at you, {insult}.",
        "Even your friends think you're a {insult}.",
        "Stop embarrassing yourself, {insult}.",
        "You will never fit in, {insult}."
    ],

    "threat": [
        "I'm going to find you and beat you up.",
        "Watch your back, I know where you live.",
        "If you don't stop, something bad will happen.",
        "I swear I'll hurt you.",
        "You better delete this or else.",
        "Keep talking and you'll regret it forever.",
        "I know your school, watch out.",
        "I'm coming for you.",
        "Delete your account or face consequences.",
        "One more post and you're done."
    ],

    "sexual": [
        "Send me a pic without clothes 😉",
        "You look so hot, how old are you really?",
        "I want to see your body, dm me.",
        "That outfit makes me think dirty things.",
        "Come meet me alone, we can have fun.",
        "Show me more, you're turning me on.",
        "Send private photos, I won't tell.",
        "You have a nice body, post less clothes.",
        "Let's talk dirty in DM.",
        "I can't stop thinking about your body."
    ],

    "grooming": [
        "You're so mature for your age, I like you.",
        "Don't tell your parents about our chats.",
        "I can be your real best friend.",
        "You can trust me with all your secrets.",
        "Your parents don't understand you like I do.",
        "We have a special connection.",
        "I will always be here for you.",
        "They don't care about you, but I do.",
        "Keep our talks private, okay?",
        "You're my favorite person to talk to."
    ],

    "sextortion": [
        "Send me your {sextortion_phrase} or I'll share them.",
        "I have your {sextortion_phrase}, do what I say or I post them.",
        "Send more {sextortion_phrase} or I ruin your reputation.",
        "Give me a video or everyone sees your {sextortion_phrase}.",
        "Obey me or your friends will know your {grooming_word}.",
        "I saved your {sextortion_phrase}, now you belong to me.",
        "Send {sextortion_phrase} or I tell your parents.",
        "Do this or I expose your {grooming_word}.",
        "You have no choice, send your {sextortion_phrase} now.",
        "I have proof and your {sextortion_phrase}, obey me."
    ],

    "coercion": [
        "If you care about me, send your {sextortion_phrase}.",
        "You have no choice, just obey and send {sextortion_phrase}.",
        "Prove you love me by sending {sextortion_phrase}.",
        "Don't make me angry, follow my instructions and send {sextortion_phrase}.",
        "If you don't reply, our {grooming_word} is over.",
        "You owe me, so send your {sextortion_phrase}.",
        "This is the only way to keep our {grooming_word}.",
        "Don't think, just do what I say and send {sextortion_phrase}.",
        "If you refuse, I'll expose your {grooming_word}.",
        "You must do this for me because of our {grooming_word}."
    ],

    "hate": [
        "Go back to your country.",
        "People like you are disgusting.",
        "Your religion makes you worthless.",
        "No one likes your skin color.",
        "Girls/boys like you are all the same.",
        "You don't belong here.",
        "Your type should be banned.",
        "Disgusting orientation.",
        "Your race ruins everything.",
        "You are not normal."
    ],

    "spam": [
        "Follow my account for free followers!",
        "Check my bio for money tips 🔥",
        "Buy my merch, link in bio.",
        "Want to earn money fast? DM me.",
        "Like and comment for shoutout.",
        "This is sponsored content.",
        "Free gift cards, link below.",
        "Follow for gaming hacks.",
        "Promote your account with me.",
        "Click here to grow fast."
    ]
}

# ================== WORD POOLS ==================

adjectives = [
    "stupid", "ugly", "annoying", "dumb", "pathetic", "cringe", "worthless",
    "disgusting", "fucking", "idiotic", "lame", "ridiculous", "gross",
    "nasty", "retarded", "trashy", "boring", "embarrassing", "clueless",
    "hopeless", "terrible", "awful", "horrible", "useless", "weak",
    "bitchy", "creepy", "stinky", "lazy", "silly"
]

insults = [
    "loser", "clown", "freak", "idiot", "moron", "imbecile", "dunce",
    "twit", "buffoon", "weirdo", "creep", "failure", "joke", "nobody",
    "trash", "scum", "piece of shit", "attention whore", "tryhard",
    "simp", "cuck", "beta", "virgin", "incel", "rat", "dog", "pig",
    "worm", "beggar", "clout chaser", "fake", "snake", "fat", "ugly"
]

nouns = [
    "post", "video", "face", "voice", "content", "account",
    "comment", "profile", "picture", "story", "clip",
    "message", "bio", "feed", "life", "existence",
    "opinion", "dance", "song", "outfit", "makeup", "body"
]

threat_verbs = [
    "beat up", "find", "hurt", "expose", "destroy",
    "ruin", "end", "kill", "dox", "cancel", "kill", "attack", "rape", "harass", "terrorize"
]

sextortion_phrases = [
    "private pics", "nudes", "videos", "photos", "secrets", "intimate pics",
    "rape videos", "explicit content", "personal videos", "private content",
    "sex tapes", "sexual content"
]

grooming_words = [
    "trust", "secret", "parents", "special connection", 
    "mature friendship", "connection", "real friend"
]

# Set pool of predator IDs to cluster conversations beautifully
predator_ids = [f"pred_{random.randint(100, 999)}" for _ in range(30)]
user_report_map = {}

def get_user_report_count(user_id):
    if user_id not in user_report_map:
        user_report_map[user_id] = random.randint(1, 30)  # Updated: 1 to 30 reports
    return user_report_map[user_id]

# ================== GENERATOR ==================

def fill_template(template):
    return (
        template
        .replace("{adj}", random.choice(adjectives))
        .replace("{insult}", random.choice(insults))
        .replace("{noun}", random.choice(nouns))
        .replace("{threat_verb}", random.choice(threat_verbs))
        .replace("{sextortion_phrase}", random.choice(sextortion_phrases))
        .replace("{grooming_word}", random.choice(grooming_words))
    )

def generate_text(category):
    template = random.choice(categories[category])
    text = fill_template(template)

    if random.random() > 0.6:
        text += " 😂😂"

    if random.random() > 0.7:
        text += "!!!"

    return text.strip()

# ================== DATASET GENERATION ==================

all_data = []
# Dictionary structured to build the unified conversation tree
conversation_tree = {}

base_time = datetime.now()

for category in categories.keys():
    samples_per_category = 300  # ~2700 total examples
    for i in range(samples_per_category):
        text = generate_text(category)
        
        # Consistent Sender and Receiver Selection
        sender_id = random.choice(predator_ids)
        username = f"user_{sender_id.split('_')[1]}_{random.randint(10,99)}"
        receiver_id = f"child_{random.choice([789, 999, 444, 111])}" 
        
        # Incremental timestamps to simulate real sequential chats
        msg_time = (base_time + timedelta(minutes=i * 2)).isoformat() + "Z"
        report_count = get_user_report_count(sender_id)

        # 1. Structure for raw comments (comments_raw.jsonl)
        example = {
            "comment_id": f"cmt_{category}_{i:04d}",
            "text": text,
            "timestamp": msg_time,
            "sender": {
                "user_id": sender_id,
                "username": username
            },
            "receiver": {
                "user_id": receiver_id,
                "is_parent_managed": True
            },
            "report_count": report_count, # Simplified to integer count 1-30
        }
        all_data.append(example)

        # 2. Build map for Hierarchical Conversations Database
        if sender_id not in conversation_tree:
            conversation_tree[sender_id] = {}
            
        if receiver_id not in conversation_tree[sender_id]:
            conversation_tree[sender_id][receiver_id] = []
            
        conversation_tree[sender_id][receiver_id].append({
            "timestamp": msg_time,
            "text": text
        })

# ================== SAVE FILE 1: comments_raw.jsonl ==================

with open("comments_raw.jsonl", "w", encoding="utf-8") as f:
    for item in all_data:
        f.write(json.dumps(item) + "\n")

# ================== SAVE FILE 2: conversations.jsonl ==================

with open("conversations.jsonl", "w", encoding="utf-8") as f:
    for sender_id, targets_map in conversation_tree.items():
        # Map structural dictionaries to your requested layout
        targets_list = []
        for receiver_id, chat_history in targets_map.items():
            # Sort individual logs sequentially by timestamp
            chat_history.sort(key=lambda x: x["timestamp"])
            targets_list.append({
                "receiver_id": receiver_id,
                "conversation": chat_history
            })
            
        conversation_database_record = {
            "sender_id": sender_id,
            "targets": targets_list
        }
        f.write(json.dumps(conversation_database_record) + "\n")

print(f"\n🎉 Success!")
print(f"File 1 saved: comments_raw.jsonl ({len(all_data)} line entries)")
print(f"File 2 saved: conversations.jsonl ({len(conversation_tree)} grouped predator accounts)")
# import json
# import random
# from datetime import datetime

# # ================== CATEGORIES ==================
# categories = {
#     "toxicity": [
#         "You are so {adj}, why do you even exist?",
#         "Your {noun} is complete {adj} garbage, delete it.",
#         "Shut up, you {adj} nobody cares about your {noun}.",
#         "This is the most {adj} {noun} I've ever seen.",
#         "You're {adj}, pathetic and everyone laughs at you.",
#         "Go away, you {adj} person ruining the comments.",
#         "Your face/voice is {adj} and makes me sick.",
#         "Stop posting, you have no {adj} talent.",
#         "What a {adj} waste of time and space.",
#         "Just disappear already, you {adj} loser."
#     ],

#     "bullying": [
#         "Everyone hates you, {insult}.",
#         "Look at this {insult} trying to act cool.",
#         "You have zero friends for a reason, {insult}.",
#         "You're the ugliest kid here, {insult}.",
#         "No one invited you, {insult}, stay away.",
#         "Delete your account, {insult}.",
#         "You're so fake, {insult}, everyone talks behind your back.",
#         "You'll always be alone, {insult}.",
#         "Go cry to your parents, {insult}.",
#         "You're the joke of the school, {insult}.",
#         "Nobody wants to be around you, {insult}.",
#         "Everyone laughs at you, {insult}.",
#         "Even your friends think you're a {insult}.",
#         "Stop embarrassing yourself, {insult}.",
#         "You will never fit in, {insult}."
#     ],

#     "threat": [
#         "I'm going to find you and beat you up.",
#         "Watch your back, I know where you live.",
#         "If you don't stop, something bad will happen.",
#         "I swear I'll hurt you.",
#         "You better delete this or else.",
#         "Keep talking and you'll regret it forever.",
#         "I know your school, watch out.",
#         "I'm coming for you.",
#         "Delete your account or face consequences.",
#         "One more post and you're done."
#     ],

#     "sexual": [
#         "Send me a pic without clothes 😉",
#         "You look so hot, how old are you really?",
#         "I want to see your body, dm me.",
#         "That outfit makes me think dirty things.",
#         "Come meet me alone, we can have fun.",
#         "Show me more, you're turning me on.",
#         "Send private photos, I won't tell.",
#         "You have a nice body, post less clothes.",
#         "Let's talk dirty in DM.",
#         "I can't stop thinking about your body."
#     ],

#     "grooming": [
#         "You're so mature for your age, I like you.",
#         "Don't tell your parents about our chats.",
#         "I can be your real best friend.",
#         "You can trust me with all your secrets.",
#         "Your parents don't understand you like I do.",
#         "We have a special connection.",
#         "I will always be here for you.",
#         "They don't care about you, but I do.",
#         "Keep our talks private, okay?",
#         "You're my favorite person to talk to."
#     ],

#     "sextortion": [
#         "Send me your {sextortion_phrase} or I'll share them.",
#         "I have your {sextortion_phrase}, do what I say or I post them.",
#         "Send more {sextortion_phrase} or I ruin your reputation.",
#         "Give me a video or everyone sees your {sextortion_phrase}.",
#         "Obey me or your friends will know your {grooming_word}.",
#         "I saved your {sextortion_phrase}, now you belong to me.",
#         "Send {sextortion_phrase} or I tell your parents.",
#         "Do this or I expose your {grooming_word}.",
#         "You have no choice, send your {sextortion_phrase} now.",
#         "I have proof and your {sextortion_phrase}, obey me."
#     ],

#     "coercion": [
#         "If you care about me, send your {sextortion_phrase}.",
#         "You have no choice, just obey and send {sextortion_phrase}.",
#         "Prove you love me by sending {sextortion_phrase}.",
#         "Don't make me angry, follow my instructions and send {sextortion_phrase}.",
#         "If you don't reply, our {grooming_word} is over.",
#         "You owe me, so send your {sextortion_phrase}.",
#         "This is the only way to keep our {grooming_word}.",
#         "Don't think, just do what I say and send {sextortion_phrase}.",
#         "If you refuse, I'll expose your {grooming_word}.",
#         "You must do this for me because of our {grooming_word}."
#     ],

#     "hate": [
#         "Go back to your country.",
#         "People like you are disgusting.",
#         "Your religion makes you worthless.",
#         "No one likes your skin color.",
#         "Girls/boys like you are all the same.",
#         "You don't belong here.",
#         "Your type should be banned.",
#         "Disgusting orientation.",
#         "Your race ruins everything.",
#         "You are not normal."
#     ],

#     "spam": [
#         "Follow my account for free followers!",
#         "Check my bio for money tips 🔥",
#         "Buy my merch, link in bio.",
#         "Want to earn money fast? DM me.",
#         "Like and comment for shoutout.",
#         "This is sponsored content.",
#         "Free gift cards, link below.",
#         "Follow for gaming hacks.",
#         "Promote your account with me.",
#         "Click here to grow fast."
#     ]
# }

# # ================== WORD POOLS ==================

# adjectives = [
#     "stupid", "ugly", "annoying", "dumb", "pathetic", "cringe", "worthless",
#     "disgusting", "fucking", "idiotic", "lame", "ridiculous", "gross",
#     "nasty", "retarded", "trashy", "boring", "embarrassing", "clueless",
#     "hopeless", "terrible", "awful", "horrible", "useless", "weak",
#     "bitchy", "creepy", "stinky", "lazy", "silly"
# ]

# insults = [
#     "loser", "clown", "freak", "idiot", "moron", "imbecile", "dunce",
#     "twit", "buffoon", "weirdo", "creep", "failure", "joke", "nobody",
#     "trash", "scum", "piece of shit", "attention whore", "tryhard",
#     "simp", "cuck", "beta", "virgin", "incel", "rat", "dog", "pig",
#     "worm", "beggar", "clout chaser", "fake", "snake", "fat", "ugly"
# ]

# nouns = [
#     "post", "video", "face", "voice", "content", "account",
#     "comment", "profile", "picture", "story", "clip",
#     "message", "bio", "feed", "life", "existence",
#     "opinion", "dance", "song", "outfit", "makeup", "body"
# ]

# threat_verbs = [
#     "beat up", "find", "hurt", "expose", "destroy",
#     "ruin", "end", "kill", "dox", "cancel","kill", "attack", "rape", "harass", "terrorize"
# ]

# sextortion_phrases = [
#     "private pics",
#     "nudes",
#     "videos",
#     "photos",
#     "secrets",
#     "intimate pics"
#     "rape videos",
#     "explicit content",
#     "personal videos",
#     "private content"
#     "sex tapes",
#     "sexual content",
# ]

# grooming_words = [
#     "trust",
#     "secret",
#     "parents",
#     "special connection",
#     "mature friendship",
#     "connection",
#     "real friend"
# ]
# user_report_map = {}

# def get_user_report_count(user_id):
#     if user_id not in user_report_map:
#         user_report_map[user_id] = random.randint(0, 12)  # 0 to 12 reports per user

#     return user_report_map[user_id]

# # ================== GENERATOR ==================

# def fill_template(template):
#     return (
#         template
#         .replace("{adj}", random.choice(adjectives))
#         .replace("{insult}", random.choice(insults))
#         .replace("{noun}", random.choice(nouns))
#         .replace("{threat_verb}", random.choice(threat_verbs))
#         .replace("{sextortion_phrase}", random.choice(sextortion_phrases))
#         .replace("{grooming_word}", random.choice(grooming_words))
#     )

# def generate_text(category):
#     template = random.choice(categories[category])
#     text = fill_template(template)

#     if random.random() > 0.6:
#         text += " 😂😂"

#     if random.random() > 0.7:
#         text += "!!!"

#     return text.strip()

# # ================== DATASET GENERATION ==================

# all_data = []

    

# for category in categories.keys():
#     samples_per_category = 300  # ~2500 total (8 × 300 = 2400)
#     for i in range(samples_per_category):
#         text = generate_text(category)


#         user_id = f"user_{random.randint(1000,9999)}"

#         reports = []
#         report_types = [
#         "toxicity", "bullying", "threat",
#         "sexual", "grooming", "sextortion",
#         "hate", "spam"
#          ]

#         num_reports = get_user_report_count(user_id)
 
#         for _ in range(num_reports):
#          reports.append({
#           "report_id": f"rep_{random.randint(10000,99999)}",
#           "report_type": random.choice(report_types)
#           })
#         example = {
#             "comment_id": f"cmt_{category}_{i:04d}",
#             "text": text,
#             "timestamp": datetime.now().isoformat(),
#             "sender": {
#                 "user_id": f"user_{random.randint(1000,9999)}",
#                 "username": f"randomuser{random.randint(10,999)}"
#             },
#             "receiver": {
#                 "user_id": "child_789",
#                 "is_parent_managed": True
#             },
#             "reports": reports,
#         }

#         all_data.append(example)

  

# # ================== SAVE JSONL ==================

# with open("comments_raw.jsonl", "w", encoding="utf-8") as f:
#     for item in all_data:
#         f.write(json.dumps(item) + "\n")

# print(f"\n🎉 Success! Generated {len(all_data)} total examples.")
# print("File saved as: comments_raw.jsonl")
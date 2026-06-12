QUESTS = {
    "what_was_sealed": {
        "id": "what_was_sealed",
        "name": "What Was Sealed",
        "district": 1,
        "steps": [
            {"id": "find_tunnel",   "desc": "Find the collapsed tunnel with Order markings.", "done": False},
            {"id": "recover_logbook","desc": "Recover the sealed logbook from a dead warden.", "done": False},
            {"id": "read_truth",    "desc": "Read the logbook. Learn what the Order chose.", "done": False},
            {"id": "defeat_boss",   "desc": "Confront The First Crack.", "done": False},
        ],
        "active": False,
        "complete": False,
        "xp_reward": 200,
    },
    "the_orders_debt": {
        "id": "the_orders_debt",
        "name": "The Order's Debt",
        "district": 2,
        "steps": [
            {"id": "find_records",  "desc": "Find the Order's financial records in the hidden office.", "done": False},
            {"id": "find_contact",  "desc": "Locate the Broker's human contact.", "done": False},
            {"id": "choice",        "desc": "Expose or silence the contact.", "done": False},
            {"id": "defeat_broker", "desc": "Confront The Broker.", "done": False},
        ],
        "active": False,
        "complete": False,
        "xp_reward": 250,
        "choice_made": None,
    },
    "the_last_order": {
        "id": "the_last_order",
        "name": "The Last Order",
        "district": 3,
        "steps": [
            {"id": "journal_1", "desc": "Find Captain's Journal I.", "done": False},
            {"id": "journal_2", "desc": "Find Captain's Journal II.", "done": False},
            {"id": "journal_3", "desc": "Find Captain's Journal III.", "done": False},
            {"id": "confront",  "desc": "Confront The Last Captain.", "done": False},
        ],
        "active": False,
        "complete": False,
        "xp_reward": 300,
        "talked_down": False,
    },
}

class QuestManager:
    def __init__(self):
        import copy
        self.quests = copy.deepcopy(QUESTS)

    def activate(self, quest_id):
        if quest_id in self.quests:
            self.quests[quest_id]["active"] = True

    def complete_step(self, quest_id, step_id):
        if quest_id not in self.quests:
            return False
        q = self.quests[quest_id]
        for step in q["steps"]:
            if step["id"] == step_id and not step["done"]:
                step["done"] = True
                return True
        return False

    def is_step_done(self, quest_id, step_id):
        if quest_id not in self.quests:
            return False
        for step in self.quests[quest_id]["steps"]:
            if step["id"] == step_id:
                return step["done"]
        return False

    def all_steps_done(self, quest_id):
        if quest_id not in self.quests:
            return False
        return all(s["done"] for s in self.quests[quest_id]["steps"])

    def complete_quest(self, quest_id):
        if quest_id in self.quests:
            self.quests[quest_id]["complete"] = True

    def active_steps(self):
        result = []
        for q in self.quests.values():
            if q["active"] and not q["complete"]:
                for step in q["steps"]:
                    if not step["done"]:
                        result.append(f"[{q['name']}] {step['desc']}")
                        break
        return result

    def to_dict(self):
        return {qid: {
            "active": q["active"],
            "complete": q["complete"],
            "steps": [{"id": s["id"], "done": s["done"]} for s in q["steps"]],
            "choice_made": q.get("choice_made"),
            "talked_down": q.get("talked_down"),
        } for qid, q in self.quests.items()}

    def from_dict(self, data):
        import copy
        self.quests = copy.deepcopy(QUESTS)
        for qid, qdata in data.items():
            if qid not in self.quests:
                continue
            self.quests[qid]["active"] = qdata.get("active", False)
            self.quests[qid]["complete"] = qdata.get("complete", False)
            for saved_step in qdata.get("steps", []):
                for step in self.quests[qid]["steps"]:
                    if step["id"] == saved_step.get("id"):
                        step["done"] = saved_step.get("done", False)
            if "choice_made" in qdata:
                self.quests[qid]["choice_made"] = qdata["choice_made"]
            if "talked_down" in qdata:
                self.quests[qid]["talked_down"] = qdata["talked_down"]

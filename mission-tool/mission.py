import json
import os
import re
import shutil
import glob
from collections import defaultdict

BASE_DIR = ""
OUTPUT_ROOT = ""

FILES = {
    "mission_data":   os.path.join(BASE_DIR, "TableCfg/MissionDataTable.json"),
    "text_table":     os.path.join(BASE_DIR, "TableCfg/TextTable.json"),
    "i18n":           os.path.join(BASE_DIR, "TableCfg/I18nTextTable_CN.json"),
    "reward":         os.path.join(BASE_DIR, "TableCfg/RewardTable.json"),
    "item":           os.path.join(BASE_DIR, "TableCfg/ItemTable.json"),
}

RUNTIME_ASSET_DIR = os.path.join(BASE_DIR, "Json/MissionRuntimeAsset")

VIEW_TYPE_MAP = {
    0: "01_主线剧情 (Main)",
    1: "02_日常委托 (Daily)",
    2: "03_世界支线 (Side)",
    3: "04_角色故事 (Character)",
    4: "05_活动 (Activity)",
    99: "99_机制 (Mechanic)"
}

PREFIX_MAP = {
    "e":  0, "m":  1, "c":  3, "f":  2, "sm": 2, "gm": 2,
    "a":  4, "dm": 99, "db": 4, "hidden": 99 
}

def load_json(path):
    if not os.path.exists(path): return {}
    try:
        with open(path, 'r', encoding='utf-8') as f: return json.load(f)
    except: return {}

def sanitize_filename(name):
    if not name: return "Unknown"
    return re.sub(r'[\\/*?:"<>|]', "_", name).strip()

def iterate_data(data):
    if isinstance(data, list): return data
    if isinstance(data, dict): return data.values()
    return []

def natural_keys(text):
    return [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', text)]

class WikiGeneratorClean:
    def __init__(self):
        print("加载基础配置表...")
        self.tables = {k: load_json(v) for k, v in FILES.items()}
        self.i18n = self.tables['i18n']
        self.text_table = self.tables['text_table']
        self.item_table = self.tables['item']
        self.reward_table = self.tables['reward']
        
        self.master_db = defaultdict(lambda: {
            "name": "", "desc": "", "level": "无", 
            "rewards": [], "objectives": [],
            "source": "Unknown"
        })

    def resolve(self, key_obj):
        raw_key = ""
        if isinstance(key_obj, dict):
            raw_key = (key_obj.get("text") or key_obj.get("id") or 
                       key_obj.get("key") or key_obj.get("Key") or key_obj.get("value"))
        else: raw_key = key_obj
        if not raw_key: return ""
        key_str = str(raw_key)
        if key_str in self.text_table:
            val = self.text_table[key_str]
            if isinstance(val, dict): val = val.get("text") or val.get("id")
            return self.i18n.get(str(val), str(val))
        return self.i18n.get(key_str, key_str)
    
    def resolve_item_name(self, item_id):
        if item_id in self.item_table:
            name_obj = self.item_table[item_id].get("name")
            return self.resolve(name_obj)
        return item_id

    def build_skeleton(self):
        print("构建任务数据骨架...")
        for info in iterate_data(self.tables['mission_data']):
            mid = info.get("missionId")
            if not mid: continue
            
            entry = self.master_db[mid]
            entry["source"] = "Table"
            entry["name"] = self.resolve(info.get("missionName"))
            entry["desc"] = self.resolve(info.get("missionDesc") or info.get("missionDescription"))
            
            rid = info.get("missionRewardId") or info.get("rewardId")
            if rid: self._parse_rewards(rid, entry["rewards"])
            if "questDic" in info: self._parse_quests(info["questDic"], entry["objectives"])

        files = glob.glob(os.path.join(RUNTIME_ASSET_DIR, "*.json"))
        for fpath in files:
            data = load_json(fpath)
            mid = data.get("missionId")
            if not mid: continue
            
            entry = self.master_db[mid]
            entry["source"] = "Runtime"
            
            name = self.resolve(data.get("missionName"))
            if name and name != mid: entry["name"] = name
            entry["desc"] = self.resolve(data.get("missionDescription"))
            if "levelId" in data: entry["level"] = data["levelId"]
            
            rid = data.get("rewardId")
            if rid: 
                entry["rewards"] = []
                self._parse_rewards(rid, entry["rewards"])
            if "questDic" in data:
                entry["objectives"] = []
                self._parse_quests(data["questDic"], entry["objectives"])

    def _parse_quests(self, quest_dic, target_list):
        quests = quest_dic.values() if isinstance(quest_dic, dict) else quest_dic
        for q in quests:
            for obj in q.get("objectiveList", []):
                txt = self.resolve(obj.get("description"))
                txt = re.sub(r"<@qu\.key>(.*?)</>", r"【\1】", txt)
                if txt: target_list.append(txt)

    def _parse_rewards(self, reward_id, target_list):
        if not reward_id or reward_id not in self.reward_table: return
        info = self.reward_table[reward_id]
        bundles = info.get("itemBundles") or info.get("rewardList") or []
        for b in bundles:
            iid = b.get("id") or b.get("itemId")
            count = b.get("count") or b.get("amount") or 1
            iname = self.resolve_item_name(iid)
            target_list.append(f"{iname} x{count}")

    def get_series_key(self, mid):
        if mid.startswith('c') and re.match(r'(c\d+)', mid): return re.match(r'(c\d+)', mid).group(1)
        if mid.startswith('e') and re.match(r'(e\d+)', mid): return re.match(r'(e\d+)', mid).group(1)
        if (mid.startswith('db') or mid.startswith('a') or mid.startswith('dm')) and re.match(r'([a-z]+\d+m\d+)', mid):
            return re.match(r'([a-z]+\d+m\d+)', mid).group(1)
        if 'l' in mid: return mid
        return mid

    def generate(self):
        print("正在生成数据文档...")
        series_map = defaultdict(list)
        for mid, data in self.master_db.items():
            if not data["name"] and not data["objectives"]: continue
            series_key = self.get_series_key(mid)
            series_map[series_key].append((mid, data))

        if os.path.exists(OUTPUT_ROOT): shutil.rmtree(OUTPUT_ROOT)
        os.makedirs(OUTPUT_ROOT)
        
        for series_key, missions in series_map.items():
            missions.sort(key=lambda x: natural_keys(x[0]))
            
            folder_name = "[未分类]"
            prefix_match = re.match(r"([a-z]+)", series_key)
            if prefix_match:
                p = prefix_match.group(1)
                if p in PREFIX_MAP: folder_name = VIEW_TYPE_MAP.get(PREFIX_MAP[p], "99_其他")

            file_title = f"{series_key}"
            for m, d in missions:
                if d["name"] and d["name"] != "Unknown" and d["name"] != m:
                    file_title = f"{series_key}_{sanitize_filename(d['name'])}_等"
                    break
            if len(missions) == 1:
                mid, d = missions[0]
                name_str = d['name'] if d['name'] and d['name'] != "Unknown" else "Unkown"
                file_title = f"{mid}_{sanitize_filename(name_str)}"

            final_dir = os.path.join(OUTPUT_ROOT, folder_name)
            if not os.path.exists(final_dir): os.makedirs(final_dir)
            
            with open(os.path.join(final_dir, f"{file_title}.md"), 'w', encoding='utf-8') as f:
                if len(missions) > 1:
                    f.write(f"# {series_key} 任务数据\n\n---\n")
                
                for mid, data in missions:
                    display_name = data['name'] or mid
                    f.write(f"\n## {display_name}\n")
                    f.write(f"- **任务描述**: {data['desc'] or '无'}\n")
                    
                    if data['rewards']:
                        f.write("\n**任务奖励**:\n")
                        for r in sorted(list(set(data["rewards"]))): f.write(f"- {r}\n")
                    
                    if data['objectives']:
                        f.write("\n**任务目标**:\n")
                        seen_obj = set()
                        for obj in data['objectives']:
                            if obj not in seen_obj:
                                f.write(f"- {obj}\n")
                                seen_obj.add(obj)
                    
                    f.write("\n---\n")

        print(f"全部完成！输出目录: {OUTPUT_ROOT}")

if __name__ == "__main__":
    app = WikiGeneratorClean()
    app.build_skeleton()
    app.generate()
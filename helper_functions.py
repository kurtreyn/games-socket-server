import json
from pathlib import Path


class HelperFunctions:
	def __init__(self):
		self.file_path = Path("logs/site-data.json")

	def load_site_data(self) -> dict:
		if not self.file_path.exists():
			return {"users": [], "rooms": []}

		with open(self.file_path, 'r', encoding="utf-8") as infile:
			return json.load(infile)

	def add_user(self, username):
		self.file_path = Path("logs/site-data.json")
		site_data = self.load_site_data()
		site_data["users"].append({"username": username})
		with open(self.file_path, 'w', encoding="utf-8") as outfile:
			json.dump(site_data, outfile, indent=4, ensure_ascii=False)




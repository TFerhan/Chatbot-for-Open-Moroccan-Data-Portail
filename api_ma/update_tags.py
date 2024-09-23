import json
import requests
import re
import argparse

def get_new_data():
  link_tags = "https://data.gov.ma/data/api/3/action/tag_list"
  link_titres = "https://data.gov.ma/data/api/3/action/package_list"

  try:
    tags_req = requests.get(link_tags)
    titres_req = requests.get(link_titres)
  except Exception as e:
    print(f"Error in fetching data from links : {link_tags} and {link_titres} ")
    exit(1)

  result_tags = tags_req.json()["result"]
  result_titres = titres_req.json()["result"]

  result_titres = [re.sub("-", " ", titre) for titre in result_titres]
  result_merged = result_tags + result_titres
  return result_merged

def load_json(data_path):
  try:
    with open(data_path, "r") as f:
      data = json.load(f)
      return data
  except FileNotFoundError:
    print("File not found")
    exit(1)

def add_to_json(data_path, updated_path):
  try:
    count = 0
    data = get_new_data()
    origin = load_json(data_path)
    count = len(data) - len(origin)
    for rs in data:
      if rs not in origin:
        origin.append(rs)
    print(f"Added {count} new items to {data_path}")
    with open(updated_path, "w") as f:
      json.dump(origin, f)
    print(f"Updated file saved to {updated_path}")
  except Exception as e:
    print(f"Error in adding to json file : {e}")
    exit(1)

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Add new items to the json file")
  parser.add_argument("data_path", type = str, help = "Path to the json file")
  parser.add_argument("updated_path", type = str, help = "Path to the updated json file")
  args = parser.parse_args()
  add_to_json(args.data_path, args.updated_path)

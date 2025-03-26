import json

with open("test.ldtk") as f:
    data = json.load(f)

level_num = int(input("Enter level number: "))
px_to_grid = 32

for layer in data["levels"]:
    if layer["identifier"] == f"Level_{level_num}":
        width, height = layer["pxWid"] // px_to_grid, layer["pxHei"] // px_to_grid
        grid = [[0 for x in range(width)] for y in range(height)]
        for map_data in layer["layerInstances"]:
            if map_data["__identifier"] == "Tiles":
                tilemap = map_data["gridTiles"]
            else:
                entites = map_data["entityInstances"]
        break

# tiles
for obj in tilemap:
    x, y = obj["px"]
    x, y = x // px_to_grid, y // px_to_grid
    grid[y][x] = obj["t"]

# entities
entity_dict_list = []
for entity in entites:
    x, y = entity["__grid"]
    if entity["__identifier"] == "Player":
        spawn = [x, y]
    else:
        entity_dict_list.append({
            "type": entity["__identifier"].lower(),
            "x": x,
            "y": y
        })

# --- custom JSON output ---
print("{")
print('    "tiles": [')

for i, row in enumerate(grid):
    line = "        [" + ", ".join(f"{n:2}" for n in row) + "]"
    if i < len(grid) - 1:
        line += ","
    print(line)

print("    ],")

print('    "enemies": [')
for i, entity in enumerate(entity_dict_list):
    line = "        " + json.dumps(entity)
    if i < len(entity_dict_list) - 1:
        line += ","
    print(line)
print("    ],")

print(f'    "spawn": {spawn}')
print("}")

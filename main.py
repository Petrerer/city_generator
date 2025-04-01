import CityGeneration

# TEST
# Get directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Path for the exported STL file
output_path = os.path.join(script_dir, 'scene_with_building.stl')

# Create ground plane
plane = create_plane()

# Create building mesh
building_mesh = building(20, 20, 30, 30, 30)

# Combine plane and building into one scene
combined = trimesh.util.concatenate([plane, building_mesh])

# Export scene to STL file
combined.export(output_path)

# Print success message
print(f"Wygenerowano plik: {output_path}")

city = City(10)
city.visualise_city()
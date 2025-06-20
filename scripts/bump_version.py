import re
import sys
import json # Added for JSON manipulation

def bump_version(release_type):
    manifest_path = "custom_components/chj_saih/manifest.json" # Changed path
    try:
        with open(manifest_path, "r") as f:
            manifest = json.load(f) # Load JSON content
    except FileNotFoundError:
        print(f"Error: {manifest_path} not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {manifest_path}")
        sys.exit(1)

    current_version = manifest.get("version")
    if not current_version:
        print(f"Error: 'version' key not found in {manifest_path}")
        sys.exit(1)

    version_regex = r"(\d+)\.(\d+)\.(\d+)" # Simpler regex for "X.Y.Z"
    match = re.match(version_regex, current_version)

    if not match:
        print(f"Error: Version string '{current_version}' in {manifest_path} is not in X.Y.Z format.")
        sys.exit(1)

    major, minor, patch = map(int, match.groups())

    if release_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif release_type == "minor":
        minor += 1
        patch = 0
    elif release_type == "patch":
        patch += 1
    else:
        print(f"Error: Invalid release type '{release_type}'. Must be one of 'major', 'minor', 'patch'.")
        sys.exit(1)

    new_version = f"{major}.{minor}.{patch}"
    manifest["version"] = new_version # Update version in JSON object

    try:
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2) # Write updated JSON with indentation
            f.write("\n") # Add trailing newline, common practice
    except Exception as e:
        print(f"Error writing updated content to {manifest_path}: {e}")
        sys.exit(1)

    print(new_version) # Output new version for GitHub Actions

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python bump_version.py <major|minor|patch>")
        sys.exit(1)

    release_type_arg = sys.argv[1]
    bump_version(release_type_arg)

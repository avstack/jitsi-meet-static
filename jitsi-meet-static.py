#!/usr/bin/env python3

import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import tempfile

parser = argparse.ArgumentParser(description="Compile the Jitsi Meet frontend to a static site")
parser.add_argument('--input', type=str, required=True, help='the path to the checked-out Jitsi Meet source code that will be built')
parser.add_argument('--output', type=str, required=True, help='the destination directory for the compiled static site (which should not already exist)')
parser.add_argument('--config-url', type=str, help='a config.js URL, if it should be loaded dynamically rather than baked in')
parser.add_argument('--interface-config-url', type=str, help='an interface_config.js URL, if it should be loaded dynamically rather than baked in')
parser.add_argument('--stack', type=str, help='an AVStack stack name, as a shortcut for setting --config-url and --interface-config-url')
args = parser.parse_args()

if args.stack is not None:
  if args.config_url is None:
    args.config_url = f"https://{args.stack}.onavstack.net/config.js"
  if args.interface_config_url is None:
    args.interface_config_url = f"https://{args.stack}.onavstack.net/interface_config.js"

# Remove checksums from Git dependencies in the NPM package lockfile to prevent spurious build errors
# on non-x86 architectures.
#
# The git dependencies specify a commit hash, so Git's hashing is already protecting the integrity.
# NPM's checksum algorithm is broken: it compresses the checked-out Git repository before hashing it,
# which results in a different checksum on different architectures.
#
# https://github.com/npm/cli/issues/2846 
with open(os.path.join(args.input, "package-lock.json")) as f:
  lockfile = json.load(f)
modified = False
for package in lockfile["packages"].values():
  if "resolved" in package and "integrity" in package and package["resolved"].startswith("git+ssh://"):
    del package["integrity"]
    modified = True
if modified:
  with open(os.path.join(args.input, "package-lock.json"), "w") as f:
    json.dump(lockfile, f)

subprocess.run("npm --loglevel=error install --no-audit --no-fund", shell=True, cwd=args.input, check=True)
try:
  subprocess.run("./node_modules/.bin/webpack -p", shell=True, cwd=args.input, check=True)
except:
  print("Re-running webpack without -p...")
  subprocess.run("./node_modules/.bin/webpack", shell=True, cwd=args.input, check=True)
subprocess.run("make deploy-init deploy-appbundle deploy-rnnoise-binary deploy-tflite deploy-meet-models deploy-lib-jitsi-meet deploy-libflac deploy-olm deploy-css", shell=True, cwd=args.input, check=True)

os.mkdir(args.output)
for subdir in ["libs", "fonts", "images", "lang", "sounds", "static"]:
  shutil.copytree(os.path.join(args.input, subdir), os.path.join(args.output, subdir))

shutil.copy2(os.path.join(args.input, "resources", "robots.txt"), os.path.join(args.output, "robots.txt"))
shutil.copy2(os.path.join(args.input, "libs", "external_api.min.js"), os.path.join(args.output, "external_api.js"))

with open(os.path.join(args.input, "lang", "languages.json")) as f:
  languages = json.load(f)
  for language in languages.keys():
    language_filename = os.path.join(args.input, "node_modules", "i18n-iso-countries", "langs", f"{language}.json")
    if os.path.isfile(language_filename):
      shutil.copy2(language_filename, os.path.join(args.output, "lang", f"countries-{language}.json"))

if os.path.isfile(os.path.join(args.input, "pwa-worker.js")):
  shutil.copy2(os.path.join(args.input, "pwa-worker.js"), os.path.join(args.output, "pwa-worker.js"))

os.mkdir(os.path.join(args.output, "css"))
for file in glob.glob("*.css", root_dir=os.path.join(args.input, "css")):
  shutil.copy2(os.path.join(args.input, "css", file), os.path.join(args.output, "css", file))

for file in glob.glob("*.html", root_dir=args.input) + glob.glob("static/*.html", root_dir=args.input):
  with open(os.path.join(args.input, file)) as in_f:
    content = in_f.read()
    if args.config_url is not None:
      content = re.sub(r'<script>\s*<!--\s*#include\s+virtual="/config.js"\s*-->\s*</script>', f'<script src="{args.config_url}"></script>', content)
    if args.interface_config_url is not None:
      content = re.sub(r'<script>\s*<!--\s*#include\s+virtual="/interface_config.js"\s*-->\s*</script>', f'<script src="{args.interface_config_url}"></script>', content)
    content = re.sub(r'<!--\s*#include\s+virtual="([^"]+)"\s*-->', lambda match: open(os.path.join(args.input, match[1].lstrip("/"))).read(), content)
    with open(os.path.join(args.output, file), "w") as out_f:
      out_f.write(content)

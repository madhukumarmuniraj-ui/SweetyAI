with open("sweety.py", "r") as f:
    code = f.read()

plugin_cli_def = '''
def handle_plugin_cli(argv):
    import json
    p_parser = argparse.ArgumentParser(
        prog="sweety plugin",
        description="Manage Anthropic Knowledge-Work Plugins locally.",
    )
    p_parser.add_argument("action", choices=["list", "sync"], help="Action: list available plugins or sync repository")
    args = p_parser.parse_args(argv)
    
    if args.action == "sync":
        from plugin_loader import setup_knowledge_plugins
        setup_knowledge_plugins()
    else:
        plugin_dir = "anthropic_plugins"
        if not os.path.exists(plugin_dir):
            print("[Info] No plugins synced yet. Run `python3 sweety.py plugin sync` first.")
            return
        print("\\n=== Installed Anthropic Knowledge-Work Plugins ===")
        for p in os.listdir(plugin_dir):
            meta_path = os.path.join(plugin_dir, p, ".claude-plugin", "plugin.json")
            if os.path.exists(meta_path):
                with open(meta_path, "r") as mf:
                    data = json.load(mf)
                print(f" - [{data['name']}] : {data['description']}")
        print("===================================================\\n")
'''

if "def handle_plugin_cli" not in code:
    code = code.replace("def main():", plugin_cli_def + "\n\ndef main():")

if 'sys.argv[1] == "plugin"' not in code:
    target = 'elif sys.argv[1] == "practice":\n            handle_practice_cli(sys.argv[2:])\n            return'
    replacement = target + '\n        elif sys.argv[1] == "plugin":\n            handle_plugin_cli(sys.argv[2:])\n            return'
    code = code.replace(target, replacement)

with open("sweety.py", "w") as f:
    f.write(code)

print("[Success] 'sweety plugin' command integrated into sweety.py!")

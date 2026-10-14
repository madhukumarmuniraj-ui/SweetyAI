with open("sweety_cua.py", "r") as f:
    content = f.read()

# Replace uppercase Runtime with lowercase runtime in DummyAgent
old_dummy = '''class DummyAgent:
    class Runtime:
        env = dict(os.environ)'''

new_dummy = '''class DummyAgent:
    class runtime:
        env = dict(os.environ)'''

content = content.replace(old_dummy, new_dummy)
content = content.replace("agent.runtime.env", "agent.runtime.env") # ensures matching

with open("sweety_cua.py", "w") as f:
    f.write(content)

print("[Success] DummyAgent runtime casing corrected!")

def test_app(app, inputs):
    for output in app.stream(inputs):
        node_name, node_state = list(output.items())[0]
        print(f"\n======================= {node_name} =======================\n")
        print("State")
        for key, val in node_state.items():
            print(f"    '{key}' : ")
            print(f"        {val}")
        print("\n===============================================\n")
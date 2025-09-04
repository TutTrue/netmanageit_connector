if __name__ == "__main__":
    import json
    with open("./scripts/all_observables.json", "r") as f:
        data = json.load(f)
    print(len(data["data"]["stixCyberObservables"]["edges"]))
    print(data["data"]["stixCyberObservables"]["pageInfo"]["globalCount"])
    
    
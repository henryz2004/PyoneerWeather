def prettyprint(d, indent=0):

    if not isinstance(d, dict):
        print((indent)*" | "+str(d))

    else:
        for k, v in d.items():
            print(indent*" | "+str(k), ":")
            prettyprint(v, indent=indent+1)

if __name__ == "__main__":

    test_dict = {
        1: "One",
        "Trying": {
            "Supposed": "to print this",
            "And": 4,
            "AS well as": {
                "Another dict": 3
            }
        },
        "None": None
    }

    prettyprint(test_dict)
class Command:
    QUERY = 1
    NEXT = 2
    LIST = 3

    @staticmethod
    def parse(cmd):
        formatted_cmd = cmd.lower().strip()
        if formatted_cmd == "next":
            return Command.NEXT
        elif formatted_cmd == "list":
            return Command.LIST
        else:
            return Command.QUERY    
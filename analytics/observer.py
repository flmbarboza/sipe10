from copy import deepcopy


class Observer:

    def diff(self, before, after):

        before = deepcopy(before)
        after = deepcopy(after)

        events = []

        before_map = {
            item["id"]: item
            for item in before
        }

        after_map = {
            item["id"]: item
            for item in after
        }

        #
        # novos
        #

        for item_id in after_map:

            if item_id not in before_map:

                events.append(
                    {
                        "event":"field_added",
                        "item":after_map[item_id]
                    }
                )

        #
        # removidos
        #

        for item_id in before_map:

            if item_id not in after_map:

                events.append(
                    {
                        "event":"field_removed",
                        "item":before_map[item_id]
                    }
                )

        #
        # alterados
        #

        for item_id in before_map:

            if item_id not in after_map:
                continue

            antigo = before_map[item_id]

            novo = after_map[item_id]

            if antigo["texto"] != novo["texto"]:

                events.append(
                    {
                        "event":"field_changed",
                        "before":antigo,
                        "after":novo
                    }
                )

        return events


observer = Observer()

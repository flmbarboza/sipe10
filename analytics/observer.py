from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Change:

    event: str

    item_id: str

    before: dict | None = None

    after: dict | None = None

    changed_fields: list[str] = field(default_factory=list)


class Observer:

    def diff(
        self,
        before: list[dict],
        after: list[dict],
        *,
        key: str = "id",
        watched_fields: list[str] | None = None,
    ) -> list[Change]:

        watched_fields = watched_fields or ["texto"]

        before = deepcopy(before)
        after = deepcopy(after)

        before_map = {
            item[key]: item
            for item in before
        }

        after_map = {
            item[key]: item
            for item in after
        }

        changes = []

        #
        # adicionados
        #

        for item_id, item in after_map.items():

            if item_id not in before_map:

                changes.append(
                    Change(
                        event="field_added",
                        item_id=item_id,
                        after=item
                    )
                )

        #
        # removidos
        #

        for item_id, item in before_map.items():

            if item_id not in after_map:

                changes.append(
                    Change(
                        event="field_removed",
                        item_id=item_id,
                        before=item
                    )
                )

        #
        # alterados
        #

        for item_id in before_map.keys():

            if item_id not in after_map:
                continue

            before_item = before_map[item_id]
            after_item = after_map[item_id]

            modified = []

            for field in watched_fields:

                before_value = before_item.get(field)
                after_value = after_item.get(field)

                if before_value != after_value:
                    modified.append(field)

            if modified:

                changes.append(
                    Change(
                        event="field_changed",
                        item_id=item_id,
                        before=before_item,
                        after=after_item,
                        changed_fields=modified
                    )
                )

        return changes


observer = Observer()

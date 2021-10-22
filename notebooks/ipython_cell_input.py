def get_ids_by_part(self, parts: tuple) -> tuple[set[int]]:
    """Return all ids for each name (part) of a GOV item."""
    # see https://github.com/CorrelAid/compgen-ii-cgv/issues/13
    # list with a set of found ids for each part of the name
    ids_by_part = [self.gov.ids_by_name.get(name, set()) for name in parts]

    # do we have unmatched parts?
    if not all(ids_by_part):
        if len(parts) == 1:
            name = parts[0]
            candidates = LocCorrection.from_list(
                tuple(self.gov.get_loc_names())
            ).get_best_candidates(name, MAX_COST)
            if len(candidates) == 1:
                logger.info(f"Solved problem for {name}: found {candidates[0][0]}.")
            # TODO: what do we do if we have more than one candidate?
            ids_by_part = [self._get_ids_for_single_candidate(candidates)]
        elif len(parts) == 2:
            # is there at least one match?
            if any(ids_by_part):
                for i, (part, ids) in enumerate(zip(parts, ids_by_part)):
                    if not ids:
                        unmatched_name = part
                        matched_name = [
                            name for name in parts if name in self.gov.ids_by_name
                        ][0]
                        ids_for_name = self.gov.ids_by_name[matched_name]
                        relevant_ids = set().union(
                            *[
                                self.gov.all_reachable_nodes_by_id[id_]
                                for id_ in ids_for_name
                            ]
                        )
                        relevant_names = set().union(
                            *[self.gov.names_by_id[id_] for id_ in relevant_ids]
                        )
                        lC = LocCorrection.from_list(tuple(relevant_names))
                        candidates = lC.get_best_candidates(
                            unmatched_name, MAX_COST
                        )
                        if len(candidates) == 1:
                            logger.info(f"Solved problem for {matched_name} (ok), {unmatched_name} (not ok): found {candidates[0][0]}.")
                        # TODO: what do we do if we have more than one candidate?
                        ids_by_part[i] = self._get_ids_for_single_candidate(candidates, relevant_ids)                    

    return tuple(ids_by_part)

"""Recognized catalog failures, independent of the database and UI."""


class RecommendationDataError(Exception):
    def __init__(self, reason: str, *, recipe_id=None, concept_id=None, sku_id=None):
        # Do not retain source values, user input, or connection information.
        self.reason = reason
        self.recipe_id = recipe_id
        self.concept_id = concept_id
        self.sku_id = sku_id
        super().__init__(reason)

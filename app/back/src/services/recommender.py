from sqlalchemy.orm import Session
from ..db.models import ItemDB

WEATHER_FALLBACKS = {
    "Summer":       ["Transitional", "Winter"],
    "Winter":       ["Transitional", "Summer"],
    "Transitional": ["Summer", "Winter"],
}


STYLE_FALLBACKS = {
    "Casual":      ["Minimalist", "Streetwear", "Sporty"],
    "Formal":      ["Elegant", "Minimalist"],
    "Streetwear":  ["Casual", "Sporty"],
    "Bohemian":    ["Vintage", "Casual"],
    "Sporty":      ["Casual", "Streetwear"],
    "Elegant":     ["Formal", "Minimalist"],
    "Vintage":     ["Bohemian", "Casual"],
    "Minimalist":  ["Casual", "Elegant", "Formal"],
}

GENDER_FALLBACKS = {
    "Men's":   ["Unisex"],
    "Women's": ["Unisex"],
    "Unisex":  [],
}

GENDER_NEUTRAL_CATEGORIES = {"sunglasses", "accessories", "hats", "scarves"}

ANCHOR_TARGETS = {
    "tops":        ["bottoms", "shoes", "outerwear", "bags", "accessories", "jewellery", "scarves", "hats", "sunglasses"],
    "bottoms":     ["tops", "shoes", "outerwear", "bags", "accessories", "jewellery", "scarves", "hats", "sunglasses"],
    "all-body":    ["shoes", "outerwear", "bags", "accessories", "jewellery", "scarves", "hats", "sunglasses"],
    "outerwear":   ["tops", "bottoms", "shoes", "bags", "accessories", "jewellery", "scarves", "hats", "sunglasses"],
    "shoes":       ["tops", "bottoms", "outerwear", "bags", "accessories", "jewellery", "scarves", "hats"],
    "bags":        ["tops", "bottoms", "outerwear", "shoes", "accessories", "jewellery", "scarves", "hats"],
    "hats":        ["tops", "bottoms", "outerwear", "shoes", "bags", "accessories", "scarves", "sunglasses"],
    "scarves":     ["tops", "bottoms", "outerwear", "shoes", "bags", "accessories", "hats"],
    "jewellery":   ["tops", "all-body", "outerwear", "bags", "accessories"],
    "accessories": ["tops", "bottoms", "outerwear", "shoes", "bags", "jewellery", "scarves", "hats"],
    "sunglasses":  ["tops", "outerwear", "hats", "accessories", "bags"],
}

DEFAULT_TARGETS = ["tops", "bottoms", "shoes", "outerwear"]

MUTUALLY_EXCLUSIVE = [
    frozenset(["tops", "all-body"]),
    frozenset(["bottoms", "all-body"]),
]


class OutfitRecommender:
    def __init__(self):
        self.is_loaded = True

    def _find_best_item(
        self,
        db: Session,
        target_cat: str,
        anchor_embedding,
        style: str,
        weather: str,
        gender: str,
        exclude_ids: list,
        user_id: int,
    ):
        """
        Fallback priority:
        STYLE IS ALWAYS RESPECTED. Only weather and gender are relaxed.

        1. Exact:  style + weather + gender
        2. Weather fallback: style + fallback_weather + gender
        3. Gender fallback: style + weather + fallback_gender
        4. Weather + gender fallback: style + fallback_weather + fallback_gender

        Style fallbacks (STYLE_FALLBACKS) only tried AFTER all weather/gender
        combinations of the original style are exhausted:
        5. Compatible style + original weather + gender
        6. Compatible style + fallback weather + gender
        7. Compatible style + original weather + fallback gender
        8. Compatible style + fallback weather + fallback gender

        If nothing found → return None (missing). Never force incompatible styles.
        """
        distance_calc = ItemDB.compat_embedding.l2_distance(anchor_embedding).label("distance")
        is_neutral = target_cat in GENDER_NEUTRAL_CATEGORIES

        def query(s, w, g=None):
            filters = [
                ItemDB.user_id == user_id,
                ItemDB.category == target_cat,
                ItemDB.style == s,
                ItemDB.weather == w,
                ItemDB.compat_embedding.is_not(None),
            ]
            if exclude_ids:
                filters.append(ItemDB.id.notin_(exclude_ids))
                
            if g is not None:
                filters.append(ItemDB.gender == g)
            return (
                db.query(ItemDB, distance_calc)
                .filter(*filters)
                .order_by(distance_calc)
                .limit(1)
                .first()
            )

        # Gender-neutral categories: skip gender filter entirely
        if is_neutral:
            # Exact style + weather
            result = query(style, weather)
            if result: return (*result, "exact")

            # Relax weather only
            for fw in WEATHER_FALLBACKS.get(weather, []):
                result = query(style, fw)
                if result: return (*result, f"weather~{fw}")

            # Try compatible styles, respect weather first then relax it
            for fs in STYLE_FALLBACKS.get(style, []):
                result = query(fs, weather)
                if result: return (*result, f"style~{fs}")
                for fw in WEATHER_FALLBACKS.get(weather, []):
                    result = query(fs, fw)
                    if result: return (*result, f"style~{fs}+weather~{fw}")

            return None 

        all_styles = [style] + STYLE_FALLBACKS.get(style, [])
        all_weathers = [weather] + WEATHER_FALLBACKS.get(weather, [])
        all_genders = [gender] + GENDER_FALLBACKS.get(gender, [])

        for si, s in enumerate(all_styles):
            for wi, w in enumerate(all_weathers):
                for gi, g in enumerate(all_genders):
                    result = query(s, w, g)
                    if result:
                        parts = []
                        if si > 0: parts.append(f"style~{s}")
                        if wi > 0: parts.append(f"weather~{w}")
                        if gi > 0: parts.append(f"gender~{g}")
                        label = "+".join(parts) if parts else "exact"
                        return (*result, label)

        return None  

    def generate_outfit(
        self,
        db: Session,
        anchor_item: ItemDB,
        filters: dict,
        user_id: int,
        exclude_ids: list = None,
    ) -> list:
        exclude_ids = exclude_ids or []
        if anchor_item.id not in exclude_ids:
            exclude_ids.append(anchor_item.id)
        if anchor_item.compat_embedding is None:
            raise ValueError(f"Item {anchor_item.id} has no compatibility embedding.")

        targets = ANCHOR_TARGETS.get(anchor_item.category, DEFAULT_TARGETS)
        targets = [t for t in targets if t != anchor_item.category]

        style   = filters["style"]
        weather = filters["weather"]
        gender  = filters["gender"]
        outfit_list = []

        filled_categories: set = {anchor_item.category}

        for target_cat in targets:
            skip = False
            for exclusive_pair in MUTUALLY_EXCLUSIVE:
                if target_cat in exclusive_pair and exclusive_pair & filled_categories:
                    skip = True
                    break
            if skip:
                continue

            result = self._find_best_item(
                db=db,
                target_cat=target_cat,
                anchor_embedding=anchor_item.compat_embedding,
                style=style,
                weather=weather,
                gender=gender,
                exclude_ids=exclude_ids,
                user_id=user_id,
            )

            if not result:
                outfit_list.append({
                    "item_id": None,
                    "category": target_cat,
                    "compatibility_score": 0.0,
                    "match_quality": "missing",
                    "image_path": None,
                })
                continue

            best_candidate, distance, match_quality = result
            filled_categories.add(target_cat)

            outfit_list.append({
                "item_id": str(best_candidate.id),
                "category": best_candidate.category,
                "compatibility_score": round(1.0 / (1.0 + distance), 4),
                "match_quality": match_quality,
                "image_path": best_candidate.image_path,
            })

        return outfit_list